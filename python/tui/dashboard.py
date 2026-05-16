"""Module docstring."""
from textual.app import App
from textual.widgets import Header, Footer, Static


class SysCleanDashboard(App):
    """Class docstring."""

    CSS_PATH = "dashboard.css"

    def compose(self):

        yield Header()

        yield Static(
            "SysClean Live Dashboard",
            id="title"
        )

        yield Footer()


if __name__ == "__main__":
    app = SysCleanDashboard()
    app.run()
