import datetime

from sqlalchemy import Column, ForeignKey, func, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class GameRound(Base):
    __tablename__ = "rounds"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    round_nr: Mapped[int] = mapped_column(unique=True)


class ServiceStatus(Base):
    __tablename__ = "service_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    status: Mapped[str]

class ServiceScore(Base):
    __tablename__ = "service_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    offense_total: Mapped[int]
    defence_total: Mapped[int]

class HighscoreAndSLA(Base):
    __tablename__ = "high_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    label: Mapped[str]
    score: Mapped[int]
    position: Mapped[int]
    sla: Mapped[str]