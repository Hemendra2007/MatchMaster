import random
import time
import json
import os

leaderboard = {1: [], 2: [], 3: []}
achievements = {"No Hints": False, "Speedster": False, "Minimalist": False}
game_stats = {"total_time_played": 0, "total_matches_found": 0}
profiles = {}

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

def provide_hint(grid, revealed, start_time, time_limit):
    row, col = random.choice([(r, c) for r in range(len(grid)) for c in range(len(grid)) if revealed[r][c] == "*"])
    print(f"Hint: Revealing card at ({row+1}, {col+1})")
    revealed[row][col] = grid[row][col]
    show_grid(grid, revealed)
    time.sleep(2)
    revealed[row][col] = "*"
    penalty = random.randint(5, 15)
    if time_limit:
        start_time -= penalty
        print(f"Time penalty: {penalty} seconds added to your time.")

def save_game(slot, level, grid, revealed, attempts, matches, time_limit, start_time):
    game_state = {
        "level": level,
        "grid": grid,
        "revealed": revealed,
        "attempts": attempts,
        "matches": matches,
        "time_limit": time_limit,
        "start_time": time.time() - start_time
    }
    with open(f"matchmaster_save_slot_{slot}.json", "w") as file:
        json.dump(game_state, file)
    print(f"Game saved in slot {slot}!")

def load_game(slot):
    try:
        with open(f"matchmaster_save_slot_{slot}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"No saved game found in slot {slot}.")
        return None

def load_profile():
    global achievements, game_stats
    name = input("Enter your profile name: ")
    if name in profiles:
        achievements = profiles[name]["achievements"]
        game_stats = profiles[name]["stats"]
        print(f"Profile '{name}' loaded!")
    else:
        profiles[name] = {"achievements": achievements.copy(), "stats": game_stats.copy()}
        print(f"New profile '{name}' created!")

def save_profile():
    global achievements, game_stats
    name = input("Enter your profile name to save: ")
    profiles[name] = {"achievements": achievements, "stats": game_stats}
    with open("matchmaster_profiles.json", "w") as file:
        json.dump(profiles, file)
    print(f"Profile '{name}' saved!")

def check_custom_achievements():
    if game_stats["total_matches_found"] >= 50:
        print("Achievement unlocked: Match Master! (Found 50 matches in total)")
    if game_stats["total_time_played"] >= 3600:
        print("Achievement unlocked: Marathon Player! (Played for over an hour)")

def check_achievements(attempts, time_taken, hints_used, time_limit):
    if not hints_used:
        achievements["No Hints"] = True
        print("Achievement unlocked: No Hints!")
    if time_limit and time_taken <= time_limit / 2:
        achievements["Speedster"] = True
        print("Achievement unlocked: Speedster!")
    if attempts <= (len(grid) * len(grid[0])) // 4:
        achievements["Minimalist"] = True
        print("Achievement unlocked: Minimalist!")
    check_custom_achievements()

def select_custom_level():
    while True:
        try:
            size = int(input("Enter custom grid size (4 to 8): "))
            if 4 <= size <= 8:
                return size, None
            print("Invalid size, must be between 4 and 8.")
        except ValueError:
            print("Please enter a valid number.")

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
            provide_hint(grid, revealed, start_time, time_limit)
            time_limit += random.randint(5, 10)  # Adjust time limit after using a hint
        
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
            game_stats["total_matches_found"] += 1
        else:
            print("No match.")
            revealed[r1][c1] = revealed[r2][c2] = "*"
        
        save_choice = input("Do you want to save the game? (y/n): ").lower()
        if save_choice == 'y':
            slot = input("Choose a slot to save (1-3): ")
            save_game(slot, size, grid, revealed, attempts, matches, time_limit, start_time)
            print("Exiting the game.")
            return False

    time_taken = time.time() - start_time
    game_stats["total_time_played"] += time_taken
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
    print("Select difficulty: (1) Easy, (2) Medium, (3) Hard, (4) Custom")
    choice = int(input("Enter choice: "))
    if choice == 1:
        return 4, None
    elif choice == 2:
        return 6, 120
    elif choice == 3:
        return 8, 180
    elif choice == 4:
        return select_custom_level()

def multiplayer_mode(size, time_limit):
    grid = create_grid(size)
    revealed = [["*" for _ in range(size)] for _ in range(size)]
    scores = [0, 0]
    turn = 0
    player_names = [input("Enter name for Player 1: "), input("Enter name for Player 2: ")]
    print(f"Multiplayer mode: {player_names[0]} vs {player_names[1]}")

    while sum(scores) < (size * size) // 2:
        show_grid(grid, revealed)
        print(f"{player_names[turn]}'s turn")
        r1, c1 = pick_card(size)
        revealed[r1][c1] = grid[r1][c1]
        show_grid(grid, revealed)
        
        r2, c2 = pick_card(size)
        revealed[r2][c2] = grid[r2][c2]
        show_grid(grid, revealed)

        if grid[r1][c1] == grid[r2][c2]:
            print(f"{player_names[turn]} found a match!")
            scores[turn] += 1
        else:
            print("No match.")
            revealed[r1][c1] = revealed[r2][c2] = "*"
            turn = 1 - turn  # Switch turns

    winner = player_names[0] if scores[0] > scores[1] else player_names[1]
    print(f"Game over! {winner} wins with {max(scores)} matches!")
    if input("Do you want to replay multiplayer mode? (y/n): ").lower() == 'y':
        multiplayer_mode(size, time_limit)

def main():
    print("Welcome to MatchMaster!")
    load_choice = input("Do you want to load a saved game? (y/n): ").lower()
    if load_choice == 'y':
        slot = input("Choose a slot to load (1-3): ")
        game_state = load_game(slot)
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

    load_profile()

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
            print(f"Thanks for playing MatchMaster! Total time played: {int(game_stats['total_time_played'])} seconds. Total matches found: {game_stats['total_matches_found']}")
            break

    save_profile()

main()
