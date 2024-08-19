import random

cards = list("AABBCCDDEEFF")
random.shuffle(cards)
grid = [cards[i:i + 4] for i in range(0, 12, 4)]
revealed = [["*" for _ in range(4)] for _ in range(3)]

def show_grid():
    for row in revealed:
        print(" ".join(row))

def pick_card():
    row, col = map(int, input("Pick a card (row col): ").split())
    return row - 1, col - 1

matches = 0
while matches < 6:
    show_grid()
    r1, c1 = pick_card()
    revealed[r1][c1] = grid[r1][c1]
    show_grid()
    
    r2, c2 = pick_card()
    revealed[r2][c2] = grid[r2][c2]
    show_grid()

    if grid[r1][c1] == grid[r2][c2]:
        print("Match!")
        matches += 1
    else:
        print("No match.")
        revealed[r1][c1] = revealed[r2][c2] = "*"

print("You matched all the pairs!")
