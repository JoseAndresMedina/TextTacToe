# TextTacToe
This is an TUI App for playing TicTacToe built using [Textual](https://github.com/willmcgugan/textual/) in Python3.

![View Of TextTacToe](img/TextTacToe.gif)

>**NOTE:** Due to the fact that textual t is still in the develepment stage, I reccomend you install this only in virtual env. This app will probably change heavily as textual changes.

## Dependencies

Textual:
```
python -m pip install textual 
```

## Install

```
python -m pip install texttactoe
```
## Run

If installed correctly, you should be able to run 1 of 2 ways, as a python module or a standalone script:

```
python -m texttactoe
```
or
```
texttactoe
```
 The following options are available for customization. Note that the color options currently do not check whether they are a valid colors. We use textual/rich to customize the color and so it mus be a valid choice from these frameworks.
```
usage: texttactoe [-h] [-v] [-p1 PLAYER1] [-p2 PLAYER2] [-c1 COLOR1] [-c2 COLOR2] [-r]

A tictactoe TUI.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         display version information
  -p1 PLAYER1, --player1 PLAYER1
                        Name of Player1
  -p2 PLAYER2, --player2 PLAYER2
                        Name of Player2
  -c1 COLOR1, --color1 COLOR1
                        Color of Player1
  -c2 COLOR2, --color2 COLOR2
                        Color of Player2
  -r, --random          Randomize player colors
```