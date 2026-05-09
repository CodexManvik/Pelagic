from __future__ import annotations

from functools import lru_cache
from typing import Any, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ai.guards import check_query_cost, validate_sql
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
    configured = {table.strip() for table in settings.sql_allowlist_tables.split(",") if table}
    configured.add("active_floats_summary")
    return configured


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
        [
            ("system", prompt),
            (
                "system",
                "Prefer active_floats_summary for basin-level aggregates when it can answer the question.",
            ),
            ("human", "{question}"),
        ]
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
    sql_plan = state.get("sql_plan")
    if sql_plan is None:
        return {"errors": ["SQL plan missing."]}

    guard = validate_sql(sql_plan.sql, _allowed_tables())
    if not guard.ok:
        errors = list(state.get("errors", [])) + [guard.reason or "SQL rejected"]
        return {"errors": errors}
    settings = get_settings()
    cost_result = await check_query_cost(
        session=state["session"],
        sql=sql_plan.sql,
        params=sql_plan.params,
        max_cost=settings.sql_max_cost,
    )
    if not cost_result.ok:
        errors = list(state.get("errors", [])) + [
            cost_result.reason or "Query cost exceeds free-tier limit."
        ]
        return {"errors": errors}
    return {"errors": []}


async def execute_node(state: GraphState) -> dict[str, Any]:
    sql_plan = state.get("sql_plan")
    if sql_plan is None:
        raise RuntimeError("SQL plan missing.")
    try:
        rows = await execute_sql(
            session=state["session"],
            sql=sql_plan.sql,
            params=sql_plan.params,
            max_rows=state["max_rows"],
        )
        return {"rows": rows, "errors": []}
    except SQLAlchemyError as exc:
        errors = list(state.get("errors", []))
        error_text = str(exc)
        errors.append(f"SQL execution failed: {exc.__class__.__name__}: {exc}")
        if "INTERVAL" in error_text or "syntax error at or near \"$" in error_text:
            errors.append(
                "Postgres cannot parameterize INTERVAL literals. Use make_interval(days => :time_window_days)."
            )
        return {"rows": [], "errors": errors}


async def interpret_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("oceanographer.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    sql_plan = state.get("sql_plan")
    chain = template | build_chat_model().with_structured_output(OceanographerAnswer)
    answer = await chain.ainvoke(
        {
            "question": state["question"],
            "sql": sql_plan.sql if sql_plan else "",
            "rows": state.get("rows") or [],
        }
    )
    return {"answer": answer}


async def repair_node(state: GraphState) -> dict[str, Any]:
    prompt = load_prompt("repair_sql.md")
    template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("human", "{question}")]
    )
    sql_plan = state.get("sql_plan")
    chain = template | build_chat_model().with_structured_output(SqlPlan)
    repaired = await chain.ainvoke(
        {
            "question": state["question"],
            "sql": sql_plan.sql if sql_plan else "",
            "errors": state.get("errors", []),
            "schema": SCHEMA_CONTEXT,
        }
    )
    return {"sql_plan": repaired, "attempt": state["attempt"] + 1, "errors": []}


def _next_after_validation(state: GraphState) -> str:
    settings = get_settings()
    if state.get("errors"):
        if state.get("attempt", 0) < settings.sql_max_retries:
            return "repair"
        return "end"
    return "execute"


def _next_after_execute(state: GraphState) -> str:
    settings = get_settings()
    if state.get("errors"):
        if state.get("attempt", 0) < settings.sql_max_retries:
            return "repair"
        return "end"
    return "interpret"


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
    graph.add_conditional_edges(
        "execute",
        _next_after_execute,
        {"repair": "repair", "interpret": "interpret", "end": END},
    )
    graph.add_edge("interpret", END)

    return graph.compile()
