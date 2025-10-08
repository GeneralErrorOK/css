import datetime
from typing import List

from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    scores: Mapped[List["ServiceScore"]] = relationship(back_populates="service")
    service_statuses: Mapped[List["ServiceStatus"]] = relationship(back_populates="service")


class GameRound(Base):
    __tablename__ = "rounds"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    round_nr: Mapped[int] = mapped_column(unique=True)
    service_scores: Mapped[List["ServiceScore"]] = relationship(back_populates="game_round")
    high_scores: Mapped[List["HighscoreAndSLA"]] = relationship(back_populates="game_round")
    service_statuses: Mapped[List["ServiceStatus"]] = relationship(back_populates="game_round")
    scores: Mapped[List["ServiceScore"]] = relationship(back_populates="game_round")


class ServiceStatus(Base):
    __tablename__ = "service_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    service: Mapped[Service] = relationship(back_populates="service_statuses")
    game_round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    game_round: Mapped[GameRound] = relationship(back_populates="service_statuses")
    status: Mapped[str]


class ServiceScore(Base):
    __tablename__ = "service_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    service: Mapped[Service] = relationship(back_populates="scores")
    game_round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    game_round: Mapped[GameRound] = relationship(back_populates="scores")
    offense_total: Mapped[int]
    defence_total: Mapped[int]


class HighscoreAndSLA(Base):
    __tablename__ = "high_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    game_round: Mapped[GameRound] = relationship(back_populates="high_scores")
    label: Mapped[str]
    score: Mapped[int]
    position: Mapped[int]
    sla: Mapped[str]
    me_team: Mapped[str]
