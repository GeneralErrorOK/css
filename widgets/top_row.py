from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label


class TopRow(HorizontalGroup):
    current_score = reactive({}, always_update=True, init=False)

    def compose(self) -> ComposeResult:
        yield Label(id="scorepanel", classes="headerlabel")
        yield Label("OFFENSE", classes="headerlabel")
        yield Label("DEFENCE", classes="headerlabel")

    def watch_current_score(self, current_score: int) -> None:
        self.query_one("#scorepanel", Label).update(
            f"Score: {current_score.get('score', 0)} (#{current_score.get('position', 1)})"
        )
