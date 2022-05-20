from itertools import cycle
from textual.widgets import Placeholder

from textual.app import App
from textual import events
from textual.widgets import Footer, Header, Button
from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView
from textual.message import Message, MessageTarget

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.pretty import Pretty
from rich.text import Text
from rich import box
from rich.console import RenderableType

import asyncio

# TODO: add info in messages about player 
class GameStatusNote(Message):

    def __init__(self, sender, winner=None, ) -> None:
        super().__init__(sender)
        self.winner = winner


    """A Message meant for the Board and App to update game info"""
    pass

class TTTBox(Widget,can_focus=False):
    """A interactable box in TicTacToe widget"""

    mouse_over = Reactive(False)
    is_selected = Reactive(False)
    winner = Reactive(False)
    # color = Reactive("")
    color = ""
    disable = False

    def __init__(self, board, name=None):
        super().__init__(name=name)
        self.board = board

    #set color here, no where else
    # TODO: 
    # - also disable tiles once game has been completed
    def render(self) -> Panel:
        if not self.disable:
            if not self.is_selected:
                if self.mouse_over:
                    self.color = self.board.current_turn.color
                else:
                    self.color = "grey35"
            else:
                if self.winner:
                    self.color = "bright_white"

            r = Button("", style=f"on {self.color}")
            return r

    def reset_tttbox(self) -> None:
        self.is_selected = False
        self.winner = False

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_click(self) -> None:
        if not self.is_selected:
            self.is_selected=True
            self.board.react_box_click()

class Player():

    def __init__(self, name:str, color:str=None):
        self.name = name
        self.color = color
        self.wins = 0

    def add_win(self):
        self.wins+=1

# TODO: add internal board logic that tracks Tie's
class TTTBoard(GridView):
    """TicTacToe Board widget"""

    rows = 3
    columns = 3

    show_end_panel = Reactive(False)

    def __init__(self, player1: Player = None, player2:Player = None):
        super().__init__()

        default_pl = Player("Player1",color="red")
        default_p2 = Player("Player2",color="blue")
        if not player1:
            self.player1 = default_pl
            self.player2 = default_p2
        elif (not player2):
            self.player1 = player1
            self.player2 = default_p2
        else:
            self.player1 = player1
            self.player2 = player2
        
        self.current_turn = self.player1
        self.player_list = [self.player1, self.player2]
        self.player_cycle = cycle(self.player_list)

    def display_win(self):
        win, indexes = self.is_winner()
        self.log(f"WIN INDEXES: {indexes}")
        for r,c in indexes:
            tile = self.board_access(r, c, self.rows)
            tile.winner = True

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
        """Checks if current board arengement is a winning combination"""
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


    # TODO: test speed if made async 
    def on_mount(self) -> None:
        self.init_game()
        self.grid.set_align("center", "center")    
        self.grid.set_gap(2,1)

        # add rows and columns with repeat arg
        self.grid.add_column(name="col", min_size=2, max_size=10,repeat=3)
        self.grid.add_row(name="row", min_size=2, max_size=5,repeat=3)
        
        # give name to each area and populate board 
        # area_names =[f"r{x},c{y}" for x in range(self.columns) for y in range(self.rows)]
        self.board = [TTTBox(self) for _ in range(self.rows*self.columns)]

        self.grid.place(*self.board)

        # end_game_panel = PlaceHolder("")
        # # end_game_panel.visible = False
        # self.grid.place()

    def react_box_click(self):
        """Handle a TTTBoxClick"""
        # TODO: this could possbly be replaced by watchers, action, and compute functions
        win,indexes = self.is_winner()
        if win:
            self.current_turn.add_win()
            self.emit_no_wait(GameStatusNote(self,self.current_turn))
            self.display_win()
            # TODO: Show win Panel
        else:
            self.switch_turns()


class PlayerInfoBox(Widget,):

    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")
    content = Reactive("")
    player = None

    def __init__(self, *, name= None,player =None) -> None:
        super().__init__(name=name)
        self.player = player
        self.content =  f"Name: {self.player.name}\n"\
                        f"Wins: {self.player.wins}"

    def render(self) -> RenderableType:
        return Panel(
                Align.left(self.content),
                title=f"{self.player.name}",
                border_style="green" if self.mouse_over else f"{self.player.color}",
                box=box.ROUNDED,
                )

    def new_content(self, player):
        self.player = player
        self.content =  f"Name: {self.player.name}\n"\
                        f"Wins: {self.player.wins}"

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False


class GameInfoPanel(GridView):
    """An info panel meant to display player details"""

    def __init__(self, players = None):
        super().__init__()
        self.players = players

    def on_mount(self):

        self.grid.add_column(name="left", min_size=10,max_size=30)
        self.grid.add_row(name ="row", fraction=1, repeat=3, max_size=10)
        self.info_panels = [PlayerInfoBox(name = "InfoPanel", player=p) for p in self.players]
        
        self.grid.place(*self.info_panels)

    def update_panels(self, player):
        for p in self.info_panels:
            if p.player.name == player.name:
                p.new_content(player)

# TODO: app should track wins losses, and relay that to info game panel
class TextTacToe(App):

    player1 = Player("Alice",color="rgb(0,161,162)")
    player2 = Player("Bob",color="yellow")
    players = [player1, player2]

    async def on_load(self) -> None:
    # async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")
        await self.bind("r", "reset_board", "Reset Game")

    async def on_mount(self) -> None:
        
        self.game_board = TTTBoard(self.player1,self.player2)
        self.footer = Footer()
        self.info_panel_grid = GameInfoPanel(self.players)
        self.header = Header(style="white on black")

        await self.view.dock(self.header,edge = "top")
        await self.view.dock(self.footer,edge="bottom")
        # bug where size needs to be set but i dont want it
        await self.view.dock(self.info_panel_grid,edge="left",size=30)
        await self.view.dock(self.game_board, edge="top")
        

        # self.end_game_panel = Placeholder(name="end_panel")
        # self.end_game_panel.visible = False
        # await self.view.dock(self.end_game_panel, edge="top",size=10,z=1)
        # self.end_game_panel.layout_offset_y = -10

    async def action_reset_board(self):
        self.game_board.reset_game()

    async def handle_game_status_note(self, message: GameStatusNote):
        # handle win
        if message.winner:
            self.info_panel_grid.update_panels(message.winner)
        else:
            pass
            # TODO: Handle Ties



if __name__ == "__main__":
    TextTacToe.run(title = "TextTacToe",log="textual.log",  log_verbosity=3)