import httpx
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from textual import log

from models.scores import Service, ServiceStatus, HighscoreAndSLA, ServiceScore


class ScoreStoreService:
    def __init__(self, db_engine: Engine) -> None:
        self._db_engine = db_engine

    def _round_is_registered(self, round_num: int) -> bool:
        with Session(self._db_engine) as session:
            round_stmt = select(ServiceStatus).where(ServiceStatus.round_nr == round_num)
            round_result = session.scalars(round_stmt).first()
        return round_result is not None


    def _process_service_status(self, scoreboard: dict) -> None:
        me = scoreboard["me"]
        round_nr = scoreboard["round"]
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
                service_status = ServiceStatus(service_id=service_id, round_nr=round_nr, status=status)
                session.add(service_status)
                session.commit()

    def _process_highscore_and_sla(self, scoreboard: dict) -> None:
        if len(scoreboard["highscore_labels"]) == 0:
            # No need to process an empty score ;)
            return
        me = scoreboard["me"]
        round_nr = scoreboard["round"]
        label = scoreboard["highscore_labels"][-1]
        for highscore_unit in scoreboard["highscore"]:
            if highscore_unit["name"] == me:
                sla = highscore_unit["sla"]
                highscore = highscore_unit["scores"][-1]

                with Session(self._db_engine) as session:
                    highscore_entry = HighscoreAndSLA(
                        round_nr=round_nr,
                        label=label,
                        score=highscore,
                        sla=sla,
                    )
                    session.add(highscore_entry)
                    session.commit()
                break

    def _get_service_id_from_name(self, name: str) -> int | None:
        with Session(self._db_engine) as session:
            stmt = select(Service).where(Service.name.ilike(name))
            result = session.scalars(stmt).first()
            if result is None:
                return None
            else:
                return result.id

    def _process_service_scores(self, scoreboard: dict) -> None:
        round_nr = int(scoreboard["round"])
        for service_name, service_stats in scoreboard["missions"].items():
            service_id = self._get_service_id_from_name(service_name)
            if service_id is None:
                log.error("Couldn't find matching service id for %s", service_name)
                return
            offense_total = service_stats["offense_points"]
            defence_total = service_stats["defence_points"]

            with Session(self._db_engine) as session:
                service_score = ServiceScore(
                    service_id=service_id,
                    round_nr=round_nr,
                    offense_total=offense_total,
                    defence_total=defence_total,
                )
                session.add(service_score)
                session.commit()


    async def get_scores(self, url: str) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            log.error("Failed to get scores!")
            return

        scoreboard = response.json().get("success")
        round_nr = int(scoreboard["round"])
        if self._round_is_registered(round_nr):
            return

        self._process_service_status(scoreboard)
        self._process_highscore_and_sla(scoreboard)
        self._process_service_scores(scoreboard)