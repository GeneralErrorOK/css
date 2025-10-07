import httpx
from sqlalchemy import create_engine, MetaData
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal, ItemGrid
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Digits, Log, Label

from models.scores import Base
from services.score_store import ScoreStoreService
from services.stats_retriever import StatsRetriever


class TopRow(ItemGrid):
    current_score = reactive((0, 0))
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(min_column_width=12, *args, **kwargs)
    def compose(self) -> ComposeResult:
        yield Label(id="scorepanel")
        yield Label("OFFENSE")
        yield Label("DEFENCE")

    def watch_current_score(self, current_score: int) -> None:
        self.query_one("#scorepanel", Label).update(f"Score: {current_score[0]} (#{current_score[1]})")


class CybernetScoringSystem(App):
    round_num = reactive(0, recompose=True)
    current_score = reactive((0, 0), recompose=True)
    def __init__(self, url: str, counter: bool = False, num_samples: int = 0, *args, **kwargs):
        self.url = url
        self._index_counter = 0
        self._counter = counter
        self._num_samples = num_samples
        self._engine = create_engine("sqlite:///db/css.sqlite3", echo=False)
        Base.metadata.create_all(bind=self._engine)
        self._score_store = ScoreStoreService(self._engine)
        self._stats_retriever = StatsRetriever(self._engine)

        super().__init__(*args, **kwargs)


    async def _update_scores(self):
        if self._counter:
            updated = await self._score_store.get_scores(f"{self.url}/{self._num_samples}/{self._index_counter}")
            self._index_counter += 1
        else:
            updated = await self._score_store.get_scores(self.url)

        if not updated:
            return

        cur_score, cur_pos, cur_sla = self._stats_retriever.get_score_position_sla()
        self.title = f"Cybernet Scoring System | Round #{self._stats_retriever.get_current_round_number()} | SLA: {cur_sla}"
        self.current_score = cur_score, cur_pos


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="⛊")
        yield TopRow().data_bind(current_score=CybernetScoringSystem.current_score)
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(10, self._update_scores)


if __name__ == "__main__":
    app = CybernetScoringSystem(url="http://127.0.0.1:8000/api/scoreboard", num_samples=100, counter=True)
    app.run()