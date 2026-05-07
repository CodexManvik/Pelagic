from datetime import UTC, date, datetime
from typing import List, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Float as SqlFloat,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Float(Base):
    """Canonical ARGO float metadata."""

    __tablename__ = "floats"

    float_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    wmo_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    deployment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    profiles: Mapped[List["Profile"]] = relationship(
        back_populates="float",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Profile(Base):
    """A single vertical profile collected by an ARGO float."""

    __tablename__ = "profiles"
    __table_args__ = (
        UniqueConstraint(
            "float_id",
            "cycle_number",
            name="uq_profiles_float_cycle",
        ),
    )

    profile_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    float_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("floats.float_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    profile_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    lat: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)

    float: Mapped["Float"] = relationship(back_populates="profiles")
    measurements: Mapped[List["Measurement"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Measurement(Base):
    """Observed ocean variables at a depth within one profile."""

    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint("profile_id", "depth", name="uq_measurements_profile_depth"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.profile_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    depth: Mapped[float] = mapped_column(SqlFloat, nullable=False)
    temperature: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)
    salinity: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)
    oxygen: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="measurements")


class QueryAudit(Base):
    """Audit trail for NL query runs."""

    __tablename__ = "query_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(SqlFloat, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
    trace_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class Embedding(Base):
    """Vector embeddings for semantic retrieval."""

    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(768))
