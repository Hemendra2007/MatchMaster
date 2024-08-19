import random
import time

leaderboard = {1: [], 2: [], 3: []}  # Store top 3 scores

def create_grid(size):
    num_pairs = (size * size) // 2
    cards = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:num_pairs]) * 2
    random.shuffle(cards)
    return [cards[i:i + size] for i in range(0, size * size, size)]

def show_grid(grid):
    for row in grid:
        print(" ".join(row))

def pick_card(size):
    while True:
        row, col = map(int, input("Pick a card (row col): ").split())
        if 0 <= row - 1 < size and 0 <= col - 1 < size:
            return row - 1, col - 1
        else:
            print("Invalid coordinates, try again.")

def provide_hint(grid, revealed):
    row, col = random.choice([(r, c) for r in range(len(grid)) for c in range(len(grid)) if revealed[r][c] == "*"])
    print(f"Hint: Revealing card at ({row+1}, {col+1})")
    revealed[row][col] = grid[row][col]
    show_grid(revealed)
    time.sleep(2)
    revealed[row][col] = "*"

def play_game(size, time_limit=None):
    grid = create_grid(size)
    revealed = [["*" for _ in range(size)] for _ in range(size)]
    matches = 0
    attempts = 0
    total_matches = (size * size) // 2
    start_time = time.time()

    while matches < total_matches:
        if time_limit and time.time() - start_time > time_limit:
            print("Time's up! You lost!")
            return False

        show_grid(revealed)
        hint_choice = input("Do you want a hint? (y/n): ").lower()
        if hint_choice == 'y':
            provide_hint(grid, revealed)
        
        r1, c1 = pick_card(size)
        revealed[r1][c1] = grid[r1][c1]
        show_grid(revealed)
        
        r2, c2 = pick_card(size)
        revealed[r2][c2] = grid[r2][c2]
        show_grid(revealed)

        attempts += 1
        if grid[r1][c1] == grid[r2][c2]:
            print("Match!")
            matches += 1
        else:
            print("No match.")
            revealed[r1][c1] = revealed[r2][c2] = "*"

    print(f"Congratulations! You matched all the pairs in {attempts} attempts!")
    return attempts

def update_leaderboard(level, attempts):
    leaderboard[level].append(attempts)
    leaderboard[level] = sorted(leaderboard[level])[:3]
    print(f"Top scores for Level {level}: {leaderboard[level]}")

def select_difficulty():
    print("Select difficulty: (1) Easy, (2) Medium, (3) Hard")
    choice = int(input("Enter choice: "))
    if choice == 1:
        return 4, None  # Easy: 4x4 grid, no time limit
    elif choice == 2:
        return 6, 120  # Medium: 6x6 grid, 120 seconds
    elif choice == 3:
        return 8, 180  # Hard: 8x8 grid, 180 seconds

def main():
    print("Welcome to MatchMaster!")
    level = 1
    while True:
        print(f"\nLevel {level}")
        grid_size, time_limit = select_difficulty()
        attempts = play_game(grid_size, time_limit)

        if attempts:
            update_leaderboard(level, attempts)

        cont = input("Do you want to continue to the next level? (y/n): ").lower()
        if cont == 'y':
            level += 1
        else:
            print("Thanks for playing MatchMaster!")
            break

main()
