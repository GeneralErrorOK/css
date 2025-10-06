from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class ServiceStatus(Base):
    __tablename__ = "service_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    round_nr: Mapped[int]
    status: Mapped[str]

class ServiceScore(Base):
    __tablename__ = "service_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    round_nr: Mapped[int]
    offense_total: Mapped[int]
    defence_total: Mapped[int]