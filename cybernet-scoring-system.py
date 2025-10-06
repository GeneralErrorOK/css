import httpx
from sqlalchemy import create_engine, MetaData
from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Digits, Log, Label

from models.scores import Service, ServiceScore, ServiceStatus
from services.score_store import ScoreStoreService


class RoundNumberDisplay(Widget):
    round_num = reactive(0)
    def compose(self) -> ComposeResult:
        yield Label("Round #")
        yield Digits()

    def watch_round_num(self, round_num: int) -> None:
        self.query_one(Digits).update(str(round_num))


class CybernetScoringSystem(App):
    round = reactive(0, recompose=True)
    def __init__(self, num_samples: int, *args, **kwargs):
        self._index_counter = 0
        self._num_samples = num_samples
        self._engine = create_engine("sqlite:///db/css.sqlite3", echo=False)
        MetaData().create_all(bind=self._engine)
        self._score_store = ScoreStoreService(self._engine)
        super().__init__(*args, **kwargs)


    async def _pull_update(self):
        await self._score_store.get_scores(f"http://127.0.0.1:8000/api/scoreboard/{self._num_samples}/{self._index_counter}")
        self._index_counter += 1

    def compose(self) -> ComposeResult:
        yield Header()
        yield RoundNumberDisplay().data_bind(round_num=CybernetScoringSystem.round)
        yield Footer()

    def on_mount(self) -> None:
        self._pull_update()
        self.set_interval(5, self._pull_update)


if __name__ == "__main__":
    app = CybernetScoringSystem(num_samples=20)
    app.run()