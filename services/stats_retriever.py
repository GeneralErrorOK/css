from typing import Tuple

from sqlalchemy import Engine, select, ScalarResult
from sqlalchemy.orm import Session, selectinload

from models.scores import GameRound, HighscoreAndSLA, ServiceScore, Service


class StatsRetriever:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_team_name(self) -> str:
        with Session(self._engine) as session:
            stmt = select(HighscoreAndSLA).order_by(HighscoreAndSLA.id.desc()).limit(1)
            highscore: HighscoreAndSLA = session.execute(stmt).scalar_one_or_none()
            if highscore is not None:
                return highscore.me_team
            else:
                return "unknown"

    def get_current_round_number(self) -> int:
        with Session(self._engine) as session:
            stmt = select(GameRound).order_by(GameRound.id.desc()).limit(1)
            gameround = session.execute(stmt).scalar_one_or_none()
            if gameround is not None:
                return gameround.id
            else:
                return 0

    def get_current_score_position_sla(self) -> Tuple[int, int, str]:
        game_round_id = self.get_current_round_number()
        with Session(self._engine) as session:
            stmt = select(HighscoreAndSLA).where(HighscoreAndSLA.game_round_id == game_round_id)
            dataset: HighscoreAndSLA = session.execute(stmt).scalar_one_or_none()
            if dataset is not None:
                return dataset.score, dataset.position, dataset.sla
            else:
                return 0, 1, "100%"

    def get_service_updates_dict(self) -> dict:
        update = {}
        with Session(self._engine) as session:
            recent_round_number = self.get_current_round_number()
            stmt = (
                select(ServiceScore)
                .options(selectinload(ServiceScore.service))
                .join(ServiceScore.service)
                .where(ServiceScore.game_round_id > recent_round_number - 6)
                .order_by(ServiceScore.game_round_id)
            )

            dataset: ScalarResult[ServiceScore] = session.scalars(stmt)
            if dataset is None:
                return {}
            for score in dataset:
                if update.get(score.service.name) is None:
                    update[score.service.name] = {
                        "off_series": [],
                        "def_series": []
                    }
                update[score.service.name]["off_series"].append(score.offense_total)
                update[score.service.name]["def_series"].append(score.defence_total)
                update[score.service.name]["off_total"] = score.offense_total
                update[score.service.name]["def_total"] = score.defence_total

        return update.copy()
