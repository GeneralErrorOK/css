from typing import List

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label, Sparkline, Digits

from config import settings


class ServiceRow(HorizontalGroup):
    service_updates = reactive({}, always_update=True, init=False)

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__()

    @staticmethod
    def _get_class_name_from_service_status(service_status: str) -> str:
        match service_status:
            case "OK":
                return "cOK"
            case "FF":
                return "cWARNING"
            case "OF":
                return "cERROR"
            case _:
                return "cNONE"

    @staticmethod
    def _get_class_name_from_series(score_series: List[int], offense: bool) -> str:
        selection = score_series[-settings.TREND_LENGTH_ROUNDS :]
        # Can't measure trend over 1 item. Can't divide by zero.
        if len(selection) == 1 or selection[0] == 0:
            return "cNONE"
        difference_percent = ((selection[-1] - selection[0]) / selection[0]) * 100

        if offense:
            if difference_percent >= settings.OFFENSIVE_SCORE_THRESHOLDS["high"]:
                return "cOK"
            elif difference_percent >= settings.OFFENSIVE_SCORE_THRESHOLDS["medium"]:
                return "cWARNING"
            elif difference_percent >= settings.OFFENSIVE_SCORE_THRESHOLDS["low"]:
                return "cERROR"
            else:
                return "cNONE"
        else:
            if difference_percent >= settings.DEFENSIVE_SCORE_THRESHOLDS["high"]:
                return "cERROR"
            elif difference_percent >= settings.DEFENSIVE_SCORE_THRESHOLDS["medium"]:
                return "cWARNING"
            elif difference_percent >= settings.DEFENSIVE_SCORE_THRESHOLDS["low"]:
                return "cOK"
            else:
                return "cNONE"

    def compose(self) -> ComposeResult:
        yield Label(self.service_name, classes="servicelabel", id="service_label")
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
        self.query_one(
            "#service_label", Label
        ).classes = self._get_class_name_from_service_status(
            service_updates.get(self.service_name, {}).get("status")
        )

        self.query_one("#off_d", Digits).update(
            str(service_updates.get(self.service_name, {}).get("off_total"))
        )
        self.query_one("#def_d", Digits).update(
            str(service_updates.get(self.service_name, {}).get("def_total"))
        )
        self.query_one("#off_d", Digits).classes = self._get_class_name_from_series(
            service_updates.get(self.service_name, {}).get("off_series"), offense=True
        )
        self.query_one("#def_d", Digits).classes = self._get_class_name_from_series(
            service_updates.get(self.service_name, {}).get("def_series"), offense=False
        )

        self.query_one("#off_s", Sparkline).data = service_updates.get(
            self.service_name, {}
        ).get("off_series")
        self.query_one("#def_s", Sparkline).data = service_updates.get(
            self.service_name, {}
        ).get("def_series")
