from typing import Tuple

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from models.scores import GameRound, HighscoreAndSLA


class StatsRetriever:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_current_round_number(self) -> int:
        with Session(self._engine) as session:
            stmt = select(GameRound).order_by(GameRound.id.desc()).limit(1)
            gameround = session.execute(stmt).scalar_one_or_none()
            if gameround is not None:
                return gameround.id
            else:
                return 0

    def get_score_position_sla(self) -> Tuple[int, int, str]:
        game_round = self.get_current_round_number()
        with Session(self._engine) as session:
            stmt = select(HighscoreAndSLA).where(HighscoreAndSLA.round_id == game_round)
            dataset: HighscoreAndSLA = session.execute(stmt).scalar_one_or_none()
            if dataset is not None:
                return dataset.score, dataset.position, dataset.sla
            else:
                return 0, 0, "100%"
