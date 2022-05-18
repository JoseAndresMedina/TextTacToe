from itertools import cycle
from textual.widgets import Placeholder

from textual.app import App
from textual import events
from textual.widgets import Footer, Header, Button
from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView
from textual.message import Message, MessageTarget

from rich.panel import Panel
from rich import box
from rich.console import RenderableType

import asyncio

# TODO: add info in messages about player 
class TTTBoxClick(Message):
    """A Message meant for the Board and App to update game info"""
    pass

class TTTBox(Widget,can_focus=False):
    """A interactable box in TicTacToe widget"""

    mouse_over = Reactive(False)
    is_selected = Reactive(False)
    color = Reactive("")
    disable = False

    # TODO: probably dont want to change color as it causes re-render
    def render(self) -> Panel:
        if not self.disable:
            style = "on"
            if self.is_selected:
                style = "on"
            else:
                if self.mouse_over:
                    self.color = "grey82 "
                else:
                    self.color = "grey35"

            r = Button("", style=f"{style} {self.color}")
            # r = Panel(renderable="", style=f"{style} {self.color}")
            return r

    def reset_tttbox(self) -> None:
        self.is_selected = False
        self.panel_color = ""

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_click(self) -> None:
        if not self.is_selected:
            self.color = self._parent.current_turn.color
            self.is_selected=True
            # self._parent.switch_turns()
            self.emit_no_wait(TTTBoxClick(self))


class Player():

    def __init__(self, name:str, color:str=None):
        self.name = name
        self.color = color
        self.name = ""
        self.wins = 0

    def add_win(self):
        self.wins+=1

# TODO: add internal board logic that tracks player turn, colors, board status (Win vs Tie)
class TTTBoard(GridView):
    """TicTacToe Board widget"""

    player1 = Player("Player1",color="rgb(0,161,162)")
    player2 = Player("Player2",color="yellow")
    current_turn = player1

    player_list = [player1, player2]
    player_cycle = cycle(player_list)

    rows = 3
    columns = 3

    show_end_panel = Reactive(False)
    won = Reactive(False)

    def watch_won(self,won: bool):
        if won:
            win, indexes = self.is_winner()
            self.log(f"{indexes}")
            for r,c in indexes:
                tile = self.board_access(r,c,self.rows)
                self.log(f"accessing tile {tile}")
                tile.color = "bright_white"


    def win_indexes(self, n):
        """Compute Win indexes for TicTacToe"""
        # Rows
        for r in range(n):
            yield [(r, c) for c in range(n)]
        # Columns
        for c in range(n):
            yield [(r, c) for r in range(n)]
        # Diagonal top left to bottom right
        yield [(i, i) for i in range(n)]
        # Diagonal top right to bottom left
        yield [(i, n - 1 - i) for i in range(n)]

    def board_access(self,r,c,n):
        """"Helper function, calculates position in 1D array of board tiles"""
        return self.board[((r*n)+c)]

    def is_winner(self):
        """Checks if current board arengement is a winning combinationS"""
        # weird formula is due to the boexes just being in a list ratehr than 2d list
        for indexes in self.win_indexes(self.rows):
            if all((self.board_access(r,c,self.rows).color == self.current_turn.color )for r, c in indexes):
                return True, indexes
        return False,[]

    def init_game(self):
        """Initializes Game turns"""
        # start turn counting
        self.switch_turns()

    def switch_turns(self):
        """Switched turns to next player in the cycle"""
        self.current_turn = next(self.player_cycle)

    def reset_game(self):
        """Resets the game board """
        for box in self.board:
            box.reset_tttbox() 
        self.won = False

    def on_mount(self) -> None:
        self.init_game()
        self.grid.set_align("center", "center")    
        self.grid.set_gap(2,1)

        # add rows and columns with repeat arg
        self.grid.add_column(name="col", min_size=5, max_size=10,repeat=3)
        self.grid.add_row(name="row", min_size=5, max_size=5,repeat=3)
        
        # give name to each area and populate board 
        area_names =[f"r{x},c{y}" for x in range(self.columns) for y in range(self.rows)]
        self.board = [TTTBox(name=area_names[_]) for _ in range(self.rows*self.columns)]

        self.grid.place(*self.board)

        # end_game_panel = PlaceHolder("")
        # # end_game_panel.visible = False
        # self.grid.place()

    def handle_tttbox_click(self, message: TTTBoxClick) -> None:
        """Handle a TTTBoxClick"""
        # TODO: this could possbly be replaced by watchers, action, and compute functions
        assert isinstance(message.sender, TTTBox)

        win,indexes = self.is_winner()
        if win:
            self.log("WIN")
            self.won = True
            # TODO: Show win Panel
            # self.reset_game()
        else:
            self.switch_turns()


class GameInfoPanel(Widget):
    """An info panel meant to display player details"""
    # TODO: switch to a grid view with panels displaying Player info

    content: Reactive[RenderableType] = Reactive("")

    def render(self) -> Panel:
            return Panel("game info content", box=box.ROUNDED, style="turquoise2") 


# TODO: app should track wins losses, and relay that to info game panel
class TextTacToe(App):

    async def on_load(self) -> None:
    # async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")
        await self.bind("r", "reset_board", "Reset Game")


    async def action_reset_board(self):
        self.game_board.reset_game()


    async def on_mount(self) -> None:

        self.info_panel = GameInfoPanel()
        self.game_board = TTTBoard()
        self.footer = Footer()
        
        await self.view.dock(Header(style="turquoise2"))
        await self.view.dock(self.footer,edge="bottom")

        await self.view.dock(self.info_panel, edge="left",size = 32)
        await self.view.dock(self.game_board, edge="top")

        self.end_game_panel = Placeholder(name="end_panel")
        # self.end_game_panel.visible = False
        await self.view.dock(self.end_game_panel, edge="top",size=10,z=1)
        self.end_game_panel.layout_offset_y = -10




if __name__ == "__main__":
    TextTacToe.run(title = "TextTacToe",log="textual.log",  log_verbosity=3)