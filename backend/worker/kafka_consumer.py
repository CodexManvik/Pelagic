from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError

from db.session import AsyncSessionLocal
from schemas.ingestion import ArgoMeasurementPayload
from services.ingestion import persist_events


logger = logging.getLogger("argo-kafka-consumer")


def _parse_brokers(raw: str) -> list[str]:
    return [broker.strip() for broker in raw.split(",") if broker.strip()]


def build_consumer() -> AIOKafkaConsumer:
    brokers = os.getenv("KAFKA_BROKERS")
    username = os.getenv("KAFKA_USERNAME")
    password = os.getenv("KAFKA_PASSWORD")
    topic = os.getenv("KAFKA_TOPIC", "argo-events")
    security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
    sasl_mechanism = os.getenv("KAFKA_SASL_MECHANISM", "SCRAM-SHA-256")

    if not brokers or not username or not password:
        raise RuntimeError(
            "Missing Kafka configuration. Expected KAFKA_BROKERS, KAFKA_USERNAME, KAFKA_PASSWORD."
        )

    return AIOKafkaConsumer(
        topic,
        bootstrap_servers=_parse_brokers(brokers),
        security_protocol=security_protocol,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=username,
        sasl_plain_password=password,
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


async def consume_forever() -> None:
    consumer = build_consumer()
    await consumer.start()

    try:
        async for message in consumer:
            payload: Any = message.value
            if isinstance(payload, dict):
                payload = [payload]

            try:
                events = [ArgoMeasurementPayload.model_validate(item) for item in payload]
            except ValidationError:
                logger.exception("Invalid Kafka payload; skipping.")
                await consumer.commit()
                continue

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    await persist_events(session, events)

            logger.info("Consumed %d events from Kafka.", len(events))
            await consumer.commit()
    finally:
        await consumer.stop()


def main() -> None:
    asyncio.run(consume_forever())


if __name__ == "__main__":
    main()
