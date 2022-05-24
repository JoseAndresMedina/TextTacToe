import argparse
from sys import version_info
from __init__ import __version__

from textual.app import App
from textual.widgets import Footer, Header

from __init__ import TTTBoard, GameStatusNote, Player, PlayerPanel

def run(argv=None):
    parser = argparse.ArgumentParser(description="A tictactoe TUI.")

    parser.add_argument("--version","-v", action="version", version=get_version(), help="display version information",)
    parser.add_argument("--player1","-p1", help="Name of Player1",)
    parser.add_argument("--player2","-p2", help="Name of Player2",)

    args = parser.parse_args(argv)

    TextTacToe.run(title = "TextTacToe",log="textual.log",  log_verbosity=3)


class TextTacToe(App):

    player1 = Player("Alice",color="rgb(0,161,162)")
    player2 = Player("Bob",color="yellow")
    players = [player1, player2]

    async def on_load(self) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")
        await self.bind("r", "reset_board", "Reset Game")

    async def on_mount(self) -> None:

        self.game_board = TTTBoard(self.player1,self.player2)
        self.footer = Footer()
        self.header = Header(style="white on black")
        self.info_panels = [PlayerPanel(name = "InfoPanel", player=p) for p in self.players]

        await self.view.dock(self.header,edge = "top")
        await self.view.dock(self.footer,edge="bottom")
        self.grid = await self.view.dock_grid(edge = "top")

        self.grid.add_column("col0", fraction=1, max_size=30)
        self.grid.add_column("col1", fraction=2)
        self.grid.add_row("row1", fraction=1, max_size = 7)
        self.grid.add_row("row2", fraction=1, max_size = 7)
        self.grid.add_row("row3", fraction=1, max_size=7)

        self.grid.add_areas(
                panel1  = "col0,row1",
                panel2  = "col0,row2",
                board   = "col1,row1-start|row3-end",
        )
        self.grid.place(panel1  = self.info_panels[0])
        self.grid.place(panel2  = self.info_panels[1])
        self.grid.place(board   = self.game_board)

    async def action_reset_board(self):
        self.game_board.reset_game()

    def update_panels(self, player):
        """Update player panel info"""
        for p in self.info_panels:
            if p.player.name == player.name:
                p.new_content(player)

    async def handle_game_status_note(self, message: GameStatusNote):
        # handle win
        if message.winner:
            self.update_panels(message.winner)
        else:
            pass
            # TODO: Handle Ties

def get_version():
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    return "\n".join([f"texttactoe {__version__} [Python {python_version}]",])

if __name__ == "__main__":
    run()