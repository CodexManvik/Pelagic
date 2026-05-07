from __future__ import annotations

from functools import lru_cache
from typing import Any, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ai.guards import validate_sql
from ai.llm import build_chat_model
from ai.schemas import OceanographerAnswer, RouterDecision, SqlPlan
from ai.tools import SCHEMA_CONTEXT, execute_sql
from core.config import get_settings
from core.prompts import load_prompt


class GraphState(TypedDict):
    question: str
    time_window_days: int | None
    max_rows: int
    router: RouterDecision | None
    sql_plan: SqlPlan | None
    rows: list[dict[str, Any]] | None
    answer: OceanographerAnswer | None
    errors: list[str]
    attempt: int
    session: AsyncSession


def _allowed_tables() -> set[str]:
    settings = get_settings()
    return {table.strip() for table in settings.sql_allowlist_tables.split(",") if table}


async def route_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("router.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    chain = template | build_chat_model().with_structured_output(RouterDecision)
    decision = await chain.ainvoke({"question": state["question"]})
    return {"router": decision}


async def sql_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("sql_engineer.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    router_data = state["router"].model_dump() if state["router"] else {}
    chain = template | build_chat_model().with_structured_output(SqlPlan)
    sql_plan = await chain.ainvoke(
        {
            "question": state["question"],
            "router": router_data,
            "schema": SCHEMA_CONTEXT,
            "time_window_days": state["time_window_days"],
        }
    )
    return {"sql_plan": sql_plan}


async def validate_node(state: GraphState) -> dict[str, Any]:
    if not state.get("sql_plan"):
        return {"errors": ["SQL plan missing."]}

    guard = validate_sql(state["sql_plan"].sql, _allowed_tables())
    if not guard.ok:
        errors = list(state.get("errors", [])) + [guard.reason or "SQL rejected"]
        return {"errors": errors}
    return {"errors": []}


async def execute_node(state: GraphState) -> dict[str, Any]:
    if not state.get("sql_plan"):
        raise RuntimeError("SQL plan missing.")

    rows = await execute_sql(
        session=state["session"],
        sql=state["sql_plan"].sql,
        params=state["sql_plan"].params,
        max_rows=state["max_rows"],
    )
    return {"rows": rows}


async def interpret_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("oceanographer.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    chain = template | build_chat_model().with_structured_output(OceanographerAnswer)
    answer = await chain.ainvoke(
        {
            "question": state["question"],
            "sql": state["sql_plan"].sql if state.get("sql_plan") else "",
            "rows": state.get("rows") or [],
        }
    )
    return {"answer": answer}


async def repair_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("repair_sql.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    chain = template | build_chat_model().with_structured_output(SqlPlan)
    sql_plan = await chain.ainvoke(
        {
            "question": state["question"],
            "sql": state["sql_plan"].sql if state.get("sql_plan") else "",
            "errors": state.get("errors", []),
            "schema": SCHEMA_CONTEXT,
        }
    )
    return {"sql_plan": sql_plan, "attempt": state["attempt"] + 1, "errors": []}


def _next_after_validation(state: GraphState) -> str:
    settings = get_settings()
    if state.get("errors"):
        if state.get("attempt", 0) < settings.sql_max_retries:
            return "repair"
        return "end"
    return "execute"


@lru_cache(maxsize=1)
def build_query_graph() -> Any:
    graph = StateGraph(GraphState)

    graph.add_node("route", route_node)
    graph.add_node("sql", sql_node)
    graph.add_node("validate", validate_node)
    graph.add_node("repair", repair_node)
    graph.add_node("execute", execute_node)
    graph.add_node("interpret", interpret_node)

    graph.set_entry_point("route")
    graph.add_edge("route", "sql")
    graph.add_edge("sql", "validate")
    graph.add_conditional_edges(
        "validate",
        _next_after_validation,
        {"repair": "repair", "execute": "execute", "end": END},
    )
    graph.add_edge("repair", "validate")
    graph.add_edge("execute", "interpret")
    graph.add_edge("interpret", END)

    return graph.compile()
