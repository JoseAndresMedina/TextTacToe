from itertools import cycle

from textual.app import App
from textual import events
from textual.widgets import Footer, Header
from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView
from textual.message import Message, MessageTarget

from rich.panel import Panel
from rich import box
from rich.console import RenderableType

# TODO: add info in messages about player 
class TTTBoxClick(Message):
    pass

class TTTBox(Widget,can_focus=False):

    mouse_over = Reactive(False)
    is_selected = Reactive(False)
    color = ""

    def render(self) -> Panel:
        self.log(f"COLOR1: {self.color}")
        style = ""
        if self.is_selected:
            self.log(f"COLOR3: {self.color}")
            style = "on"
        else:
            self.log(f"COLOR2: {self.color}")
            if self.mouse_over:
                self.color = "grey82 "
            else:
                self.color = "grey35"

        r = Panel(renderable="", style=f"{style} {self.color}")
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

    player1 = Player("Player1",color="red")
    player2 = Player("Player2",color="blue")
    current_turn = player1

    player_list = [player1, player2]
    player_cycle = cycle(player_list)

    rows = 3
    columns = 3


    def win_indexes(self, n):
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

    def is_winner(self, board, color):
        board_rows = 3
        # weird formula is due to the boexes just being in a list ratehr than 2d list
        for indexes in self.win_indexes(board_rows):
            self.log(f"hi {indexes}")
            self.log(f"color: {self.current_turn.color}")

            if all((board[((r*board_rows)+c)].color == color )for r, c in indexes):
                return True
        return False

    def init_game(self):
        # start turn counting
        self.switch_turns()

    def switch_turns(self):
        self.current_turn = next(self.player_cycle)

    def reset_game(self):
        [box.reset_tttbox() for box in self.board]

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
        self.log(f"{self.board}")
        self.grid.place(*self.board)

    def handle_tttbox_click(self, message: TTTBoxClick) -> None:
        """A message sent by the TTTBox button"""
        assert isinstance(message.sender, TTTBox)

        win = self.is_winner(self.board, self.current_turn.color)
        if win:
            self.log("WIN")
            # TODO: Show win Panel
            self.reset_game()
        else:
            self.switch_turns()


class GameInfoPanel(Widget):

    content: Reactive[RenderableType] = Reactive("")

    def render(self) -> Panel:
            return Panel("game info content", box=box.ROUNDED, style="dodger_blue3") 


# TODO: app should track wins losses, and relay that to info game panel
class TextTacToe(App):

    async def on_load(self) -> None:
    # async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")



    async def on_mount(self) -> None:

        self.info_panel = GameInfoPanel()
        self.game_board = TTTBoard()
        
        await self.view.dock(Header(style="none"))
        await self.view.dock(Footer(),edge="bottom")

        await self.view.dock(self.info_panel, edge="left",size = 32)
        await self.view.dock(self.game_board, edge="top")



if __name__ == "__main__":
    TextTacToe.run(title = "TicTacToe2",log="textual.log",  log_verbosity=3)