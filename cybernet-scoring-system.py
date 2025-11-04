from sqlalchemy import create_engine
from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer

from config.settings import SCOREBOARD_URL, REFRESH_INTERVAL_S, NUM_SAMPLES, DEV_SERVER_MODE, DB_FILENAME
from models.scores import Base
from services.score_store import ScoreStoreService
from services.stats_retriever import StatsRetriever
from widgets.service_row import ServiceRow
from widgets.top_row import TopRow


class CybernetScoringSystem(App):
    CSS_PATH = "style/css.tcss"

    round_num = reactive(0, recompose=True)
    current_score = reactive({}, recompose=True)
    service_updates = reactive({}, recompose=True)

    def __init__(
        self,
        url: str,
        refresh_interval: int,
        counter: bool = False,
        num_samples: int = 0,
        *args,
        **kwargs,
    ):
        self.url = url
        self.refresh_interval = refresh_interval
        self._index_counter = 1
        self._counter = counter
        self._num_samples = num_samples
        self._engine = create_engine(f"sqlite:///db/{DB_FILENAME}", echo=False)
        if DEV_SERVER_MODE:
            Base.metadata.drop_all(bind=self._engine)
            Base.metadata.create_all(bind=self._engine)
        else:
            Base.metadata.create_all(bind=self._engine)
        self._score_store = ScoreStoreService(self._engine)
        self._stats_retriever = StatsRetriever(self._engine)

        super().__init__(*args, **kwargs)

    def _toggle_update_warning(self):
        self.query_one(Header).toggle_class("updateWarning")
        self.query_one(Footer).toggle_class("updateWarning")

    async def _update_scores(self):
        if self._counter:
            updated = await self._score_store.get_scores(
                f"{self.url}/{self._num_samples}/{self._index_counter}"
            )
            self._index_counter += 1
        else:
            updated = await self._score_store.get_scores(self.url)

        if not updated:
            return

        cur_score, cur_pos, cur_sla = (
            self._stats_retriever.get_current_score_position_sla()
        )
        self.title = f"Cybernet Scoring System | {self._stats_retriever.get_team_name()} | Round #{self._stats_retriever.get_current_round_number()} | SLA: {cur_sla}"
        self.current_score = {
            "score": cur_score,
            "position": cur_pos,
        }
        self.current_score = self.current_score
        self.service_updates = self._stats_retriever.get_service_updates_dict()
        self.service_updates = self.service_updates

        self.set_timer(0.1, self._toggle_update_warning)
        self.set_timer(5, self._toggle_update_warning)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="⛊")
        yield TopRow().data_bind(current_score=CybernetScoringSystem.current_score)
        for service_name in self.service_updates:
            yield ServiceRow(service_name).data_bind(
                service_updates=CybernetScoringSystem.service_updates
            )
        yield Footer()

    def on_mount(self) -> None:
        self.set_timer(0.1, self._update_scores)
        self.set_interval(self.refresh_interval, self._update_scores)


if __name__ == "__main__":
    app = CybernetScoringSystem(
        url=SCOREBOARD_URL,
        refresh_interval=REFRESH_INTERVAL_S,
        num_samples=NUM_SAMPLES,
        counter=DEV_SERVER_MODE,
    )
    app.run()
