import httpx
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from textual import log

from models.scores import Service, ServiceStatus


class ScoreStoreService:
    def __init__(self, db_engine: Engine) -> None:
        self._db_engine = db_engine


    def _process_service_status(self, scoreboard: dict) -> None:
        me = scoreboard["me"]
        round_nr = int(scoreboard["round"])
        services_statuses = []
        for highscore_unit in scoreboard["highscore"]:
            if highscore_unit["name"] == me:
                # TODO: Register SLA?
                our_services = highscore_unit["services"]
                for service in our_services:
                    services_statuses.append((service, our_services[service]["status"]))

        with Session(self._db_engine) as session:
            for service, status in services_statuses:
                # 1) Check if Service is known, if not: add
                service_statement = select(Service).where(Service.name == service)
                found_service = session.execute(service_statement).first()
                if found_service is None:
                    new_service = Service(name=service)
                    session.add(new_service)
                    session.commit()
                    service_id = new_service.id
                else:
                    service_id = found_service.id
                # 2) Add datapoint to ServiceStatus
                service_status = ServiceStatus(service_id=service_id, round_nr=round_nr, status=status)
                session.add(service_status)
                session.commit()

    async def get_scores(self, url: str) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            log.error("Failed to get scores!")
            return

        scoreboard = response.json().get("success")
        self._process_service_status(scoreboard)
        # self._process_scores(scoreboard)