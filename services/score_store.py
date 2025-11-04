import httpx
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from textual import log

from config.settings import ME_TEAM
from models.scores import (
    Service,
    ServiceStatus,
    HighscoreAndSLA,
    ServiceScore,
    GameRound,
)


class ScoreStoreService:
    def __init__(self, db_engine: Engine) -> None:
        self._db_engine = db_engine

    def _round_is_registered(self, score_timestamp: str) -> bool:
        with Session(self._db_engine) as session:
            stmt = select(GameRound).where(GameRound.score_timestamp == score_timestamp)
            round_result = session.scalars(stmt).first()
        return round_result is not None

    def _get_round_id(self, timestamp: str) -> int | None:
        with Session(self._db_engine) as session:
            stmt = select(GameRound).where(GameRound.score_timestamp == timestamp)
            round_result = session.scalars(stmt).first()
            if round_result is None:
                log.error(f"Round {timestamp} not found!")
            else:
                return round_result.id

    def _process_service_status(self, scoreboard: dict, round_id: int) -> None:
        me = ME_TEAM
        services_statuses = []
        for highscore_unit in scoreboard["highscore"]:
            if highscore_unit["name"] == me:
                our_services = highscore_unit["services"]
                for service in our_services:
                    services_statuses.append((service, our_services[service]["status"]))

        with Session(self._db_engine) as session:
            for service, status in services_statuses:
                # 1) Check if Service is known, if not: add
                service_statement = select(Service).where(Service.name == service)
                found_service = session.scalars(service_statement).first()
                if found_service is None:
                    new_service = Service(name=service)
                    session.add(new_service)
                    session.commit()
                    session.refresh(new_service)
                    service_id = new_service.id
                else:
                    service_id = found_service.id
                # 2) Add datapoint to ServiceStatus
                service_status = ServiceStatus(
                    service_id=service_id, game_round_id=round_id, status=status
                )
                session.add(service_status)
                session.commit()

    def _process_highscore_and_sla(self, scoreboard: dict, round_id: int) -> None:
        if len(scoreboard["highscore_labels"]) == 0:
            # No need to process an empty score ;)
            return
        me = ME_TEAM
        label = scoreboard["highscore_labels"][-1]
        highscores = []
        sla = ""
        highscore = 0
        for highscore_unit in scoreboard["highscore"]:
            if highscore_unit["name"] == me:
                sla = highscore_unit["sla"]
                highscore = highscore_unit["scores"][-1]
            highscores.append(highscore_unit["scores"][-1])

        highscores.sort(reverse=True)
        position = highscores.index(highscore) + 1

        with Session(self._db_engine) as session:
            highscore_entry = HighscoreAndSLA(
                game_round_id=round_id,
                label=label,
                score=highscore,
                position=position,
                sla=sla,
                me_team=me,
            )
            session.add(highscore_entry)
            session.commit()

    def _get_service_id_from_name(self, name: str) -> int | None:
        with Session(self._db_engine) as session:
            stmt = select(Service).where(Service.name.ilike("%" + name + "%"))
            result = session.scalars(stmt).first()
            if result is None:
                if len(name) <= 2:
                    return None
                else:
                    return self._get_service_id_from_name(name[1:-1])
            else:
                return result.id

    def _process_service_scores(self, scoreboard: dict, round_id: int) -> None:
        me = ME_TEAM
        for highscore_unit in scoreboard["highscore"]:
            if highscore_unit["name"] == me:
                our_services = highscore_unit["services"]
                for service in our_services:
                    service_id = self._get_service_id_from_name(service)
                    with Session(self._db_engine) as session:
                        service_score = ServiceScore(
                            service_id=service_id,
                            game_round_id=round_id,
                            offense_total=our_services[service]["capture"],
                            defence_total=our_services[service]["lost"],
                        )
                        session.add(service_score)
                        session.commit()

    def _register_round(self, timestamp: str) -> int:
        with Session(self._db_engine) as session:
            new_round = GameRound(score_timestamp=timestamp)
            session.add(new_round)
            session.commit()
            return new_round.id

    async def get_scores(self, url: str) -> bool:
        """Request score update from server.

        Returns:
            True on update, False otherwise."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
            except httpx.ConnectError:
                log.error("Failed to connect to server")
                return False

        if response.status_code != 200:
            log.error("Failed to get scores!")
            return False

        scoreboard = response.json().get("success")
        timestamp = scoreboard["highscore_labels"][-1]
        if self._round_is_registered(timestamp):
            return False
        else:
            round_id = self._register_round(timestamp)

        self._process_service_status(scoreboard, round_id)
        self._process_highscore_and_sla(scoreboard, round_id)
        self._process_service_scores(scoreboard, round_id)

        return True
