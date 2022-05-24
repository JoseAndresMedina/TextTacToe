
from textual import events
from textual.widget import Widget
from textual.reactive import Reactive

from rich.panel import Panel
from rich.align import Align
from rich import box
from rich.console import RenderableType

class PlayerPanel(Widget):

    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")
    content = Reactive("")
    player = None

    def __init__(self, *, name= None,player =None) -> None:
        super().__init__(name=name)
        self.player = player
        self.content =  f"Wins: {self.player.wins}"

    def render(self) -> RenderableType:
        return Panel(
                Align.left(self.content),
                title=f"{self.player.name}",
                border_style="bright_white" if self.mouse_over else f"{self.player.color}",
                box=box.ROUNDED,
                )

    def new_content(self, player):
        """Update player panel content"""
        self.player = player
        self.content = f"Wins: {self.player.wins}"

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
