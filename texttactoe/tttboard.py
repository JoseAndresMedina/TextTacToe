from itertools import cycle

from textual.widgets import Button
from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView
from textual.message import Message

from rich.panel import Panel

class GameStatusNote(Message):
    """A Message meant for the App to update game info"""
    def __init__(self, sender, winner=None, ) -> None:
        super().__init__(sender)
        self.winner = winner

class TTTBox(Widget):
    """A interactable box in TicTacToe widget"""

    # winner: denotes whether this box is a part of a winning 3-in-a-row
    # disable: denotes whether this box is disbaled for interaction, happens on game_over
    mouse_over = Reactive(False)
    is_selected = Reactive(False)
    winner = Reactive(False)
    color = ""
    disable = False

    def __init__(self, board, name=None):
        super().__init__(name=name)
        self.board = board

    def render(self) -> Panel:
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

    def toggle_disable(self):
        """Used to disable tiles on game over"""
        self.disable = not self.disable
        self.log(f"toggling myslef {self}")

    def reset_tttbox(self) -> None:
        """Resets tile to prepare for next game"""
        self.toggle_disable()
        self.is_selected = False
        self.winner = False
        self.mouse_over = False

    def on_enter(self) -> None:
        if not self.disable:
            self.mouse_over = True

    def on_leave(self) -> None:
        if not self.disable:
            self.mouse_over = False

    def on_click(self) -> None:
        if not self.disable:
            if not self.is_selected:
                self.is_selected=True
                self.board.react_box_click()

class Player():

    def __init__(self, name:str, color:str=None):
        self.name = name
        self.color = color
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.streak = 0

    def add_win(self):
        self.wins+=1

class TTTBoard(GridView):
    """TicTacToe Board widget"""

    #set of possoble states after a click is received 
    CONTINUE = 0
    WIN = 1
    TIE = 2

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

    # TODO: test speed if made async 
    def on_mount(self) -> None:
        self.init_game()
        self.grid.set_align("center", "top")    
        self.grid.set_gap(2,1)
        self.grid.set_gutter(column=3,row=1)

        # add rows and columns with repeat arg
        self.grid.add_column(name="col", min_size=2, max_size=10,repeat=3)
        self.grid.add_row(name="row", min_size=2, max_size=5,repeat=3)
        
        self.board = [TTTBox(self) for _ in range(self.rows*self.columns)]

        self.grid.place(*self.board)

    def display_win(self, indexes):
        """Show winning 3-in-a-row"""
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
        for indexes in self.win_indexes(self.rows):
            if all((self.board_access(r,c,self.rows).color == self.current_turn.color )for r, c in indexes):
                return self.WIN, indexes

        selected = 0
        for tile in self.board:
            if tile.is_selected:
                selected+=1
        if selected ==self.rows*self.columns:
            return self.TIE,[]

        return self.CONTINUE,[]

    def init_game(self):
        """Initializes Game turns"""
        self.switch_turns()

    def switch_turns(self):
        """Switched turns to next player in the cycle"""
        self.current_turn = next(self.player_cycle)

    def reset_game(self):
        """Resets the game board """
        for box in self.board:
            box.reset_tttbox() 
        self.won = False
        self.switch_turns()

    def toggle_disable(self):
        """Toggle board interactability"""
        for tile in self.board:
            tile.toggle_disable()

    def react_box_click(self):
        """Handle a TTTBoxClick"""
        # TODO: this could possbly be replaced by watchers, action, and compute functions
        status,indexes = self.is_winner()
        if status is self.WIN:
            self.current_turn.add_win()
            self.emit_no_wait(GameStatusNote(self,self.current_turn))
            self.display_win(indexes)
            self.toggle_disable()
            # TODO: Show win Panel
        elif status is self.TIE:
            self.emit_no_wait(GameStatusNote(self))
            self.toggle_disable()
            # self.display_tie()
            # TODO: Show win Panel
        else:
            self.switch_turns()