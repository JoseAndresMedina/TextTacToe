
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
