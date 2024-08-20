import random
import time
import json

leaderboard = {1: [], 2: [], 3: []}
achievements = {"No Hints": False, "Speedster": False}

def create_grid(size):
    num_pairs = (size * size) // 2
    cards = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:num_pairs]) * 2
    random.shuffle(cards)
    return [cards[i:i + size] for i in range(0, size * size, size)]

def show_grid(grid, revealed):
    print("    " + "   ".join(str(i + 1) for i in range(len(grid))))
    print("  +" + "---+" * len(grid))
    for idx, row in enumerate(revealed):
        print(f"{idx + 1} | " + " | ".join(row) + " |")
        print("  +" + "---+" * len(grid))

def pick_card(size):
    while True:
        row, col = map(int, input("Pick a card (row col): ").split())
        if 0 <= row - 1 < size and 0 <= col - 1 < size:
            return row - 1, col - 1
        print("Invalid coordinates, try again.")

def provide_hint(grid, revealed):
    row, col = random.choice([(r, c) for r in range(len(grid)) for c in range(len(grid)) if revealed[r][c] == "*"])
    print(f"Hint: Revealing card at ({row+1}, {col+1})")
    revealed[row][col] = grid[row][col]
    show_grid(grid, revealed)
    time.sleep(2)
    revealed[row][col] = "*"

def save_game(level, grid, revealed, attempts, matches, time_limit, start_time):
    game_state = {
        "level": level,
        "grid": grid,
        "revealed": revealed,
        "attempts": attempts,
        "matches": matches,
        "time_limit": time_limit,
        "start_time": time.time() - start_time
    }
    with open("matchmaster_save.json", "w") as file:
        json.dump(game_state, file)
    print("Game saved!")

def load_game():
    try:
        with open("matchmaster_save.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("No saved game found.")
        return None

def check_achievements(attempts, time_taken, hints_used, time_limit):
    if not hints_used:
        achievements["No Hints"] = True
        print("Achievement unlocked: No Hints!")
    if time_limit and time_taken <= time_limit / 2:
        achievements["Speedster"] = True
        print("Achievement unlocked: Speedster!")

def play_game(size, time_limit=None, grid=None, revealed=None, attempts=0, matches=0, start_time=None):
    if not grid:
        grid = create_grid(size)
        revealed = [["*" for _ in range(size)] for _ in range(size)]
    total_matches = (size * size) // 2
    if not start_time:
        start_time = time.time()

    hints_used = False
    while matches < total_matches:
        if time_limit and time.time() - start_time > time_limit:
            print("Time's up! You lost!")
            return False

        show_grid(grid, revealed)
        hint_choice = input("Do you want a hint? (y/n): ").lower()
        if hint_choice == 'y':
            hints_used = True
            provide_hint(grid, revealed)
        
        r1, c1 = pick_card(size)
        revealed[r1][c1] = grid[r1][c1]
        show_grid(grid, revealed)
        
        r2, c2 = pick_card(size)
        revealed[r2][c2] = grid[r2][c2]
        show_grid(grid, revealed)

        attempts += 1
        if grid[r1][c1] == grid[r2][c2]:
            print("Match!")
            matches += 1
        else:
            print("No match.")
            revealed[r1][c1] = revealed[r2][c2] = "*"
        
        save_choice = input("Do you want to save the game? (y/n): ").lower()
        if save_choice == 'y':
            save_game(level, grid, revealed, attempts, matches, time_limit, start_time)
            print("Exiting the game.")
            return False

    time_taken = time.time() - start_time
    print(f"Congratulations! You matched all pairs in {attempts} attempts!")
    print(f"Time taken: {int(time_taken)} seconds")
    print(f"Average match speed: {time_taken / total_matches:.2f} seconds per match")

    check_achievements(attempts, time_taken, hints_used, time_limit)
    return attempts

def update_leaderboard(level, attempts):
    leaderboard[level].append(attempts)
    leaderboard[level] = sorted(leaderboard[level])[:3]
    print(f"Top scores for Level {level}: {leaderboard[level]}")

def select_difficulty():
    print("Select difficulty: (1) Easy, (2) Medium, (3) Hard")
    choice = int(input("Enter choice: "))
    if choice == 1:
        return 4, None
    elif choice == 2:
        return 6, 120
    elif choice == 3:
        return 8, 180

def multiplayer_mode(size, time_limit):
    grid = create_grid(size)
    revealed = [["*" for _ in range(size)] for _ in range(size)]
    scores = [0, 0]
    turn = 0
    print("Multiplayer mode: Player 1 vs Player 2")

    while sum(scores) < (size * size) // 2:
        show_grid(grid, revealed)
        print(f"Player {turn + 1}'s turn")
        r1, c1 = pick_card(size)
        revealed[r1][c1] = grid[r1][c1]
        show_grid(grid, revealed)
        
        r2, c2 = pick_card(size)
        revealed[r2][c2] = grid[r2][c2]
        show_grid(grid, revealed)

        if grid[r1][c1] == grid[r2][c2]:
            print(f"Player {turn + 1} found a match!")
            scores[turn] += 1
        else:
            print("No match.")
            revealed[r1][c1] = revealed[r2][c2] = "*"
            turn = 1 - turn  # Switch turns

    winner = "Player 1" if scores[0] > scores[1] else "Player 2"
    print(f"Game over! {winner} wins with {max(scores)} matches!")

def main():
    print("Welcome to MatchMaster!")
    load_choice = input("Do you want to load a saved game? (y/n): ").lower()
    if load_choice == 'y':
        game_state = load_game()
        if game_state:
            play_game(
                size=len(game_state['grid']),
                time_limit=game_state['time_limit'],
                grid=game_state['grid'],
                revealed=game_state['revealed'],
                attempts=game_state['attempts'],
                matches=game_state['matches'],
                start_time=time.time() - game_state['start_time']
            )
            return

    level = 1
    while True:
        mode_choice = input("Select mode: (1) Single Player, (2) Multiplayer: ").lower()
        if mode_choice == '2':
            grid_size, time_limit = select_difficulty()
            multiplayer_mode(grid_size, time_limit)
            break

        print(f"\nLevel {level}")
        grid_size, time_limit = select_difficulty()
        attempts = play_game(grid_size, time_limit)

        if attempts:
            update_leaderboard(level, attempts)

        cont = input("Do you want to continue to the next level? (y/n): ").lower()
        if cont == 'y':
            level += 1
        elif input("Do you want to replay this level? (y/n): ").lower() == 'y':
            continue
        else:
            print("Thanks for playing MatchMaster!")
            break

main()
