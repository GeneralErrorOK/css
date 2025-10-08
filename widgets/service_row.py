from textual.app import ComposeResult
from textual.containers import ItemGrid, Horizontal, Grid, Container, HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Sparkline, Digits


class ServiceRow(HorizontalGroup):
    service_updates = reactive({}, always_update=True, init=False)

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.service_name, classes="servicelabel")
        # Offense
        yield Sparkline(
            data=self.service_updates.get(self.service_name, {}).get("off_series"),
            id="off_s",
        )
        yield Digits(id="off_d")
        # Defence
        yield Digits(id="def_d")
        yield Sparkline(
            data=self.service_updates.get(self.service_name, {}).get("def_series"),
            id="def_s",
        )

    def watch_service_updates(self, service_updates: dict) -> None:
        self.query_one("#off_d", Digits).update(
            str(service_updates.get(self.service_name, {}).get("off_total"))
        )
        self.query_one("#def_d", Digits).update(
            str(service_updates.get(self.service_name, {}).get("def_total"))
        )

        self.query_one("#off_s", Sparkline).data = service_updates.get(
            self.service_name, {}
        ).get("off_series")
        self.query_one("#def_s", Sparkline).data = service_updates.get(
            self.service_name, {}
        ).get("def_series")
