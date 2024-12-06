import tkinter as tk
import random
import json
from tkinter import simpledialog

# Leaderboard file
LEADERBOARD_FILE = "leaderboard.json"

class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("2048")
        self.frame = tk.Frame(self.master, bg="gray")
        self.frame.pack()
        
        # Game variables
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.high_score = self.load_high_score()
        self.previous_states = []
        self.cells = []
        
        # Difficulty Levels
        self.start_game_prompt()
        
        # Game Grid UI
        for i in range(4):
            row = []
            for j in range(4):
                label = tk.Label(self.frame, text="", font=("Arial", 24), width=5, height=2, bg="lightgray", relief="solid")
                label.grid(row=i, column=j, padx=5, pady=5)
                row.append(label)
            self.cells.append(row)
        
        # Score Display
        self.score_label = tk.Label(self.master, text=f"Score: {self.score}", font=("Arial", 16), bg="white", relief="solid")
        self.score_label.pack(pady=10)
        self.high_score_label = tk.Label(self.master, text=f"High Score: {self.high_score}", font=("Arial", 16), bg="white", relief="solid")
        self.high_score_label.pack(pady=10)
        
        self.add_new_tile()
        self.add_new_tile()
        self.update_grid()
        
        self.master.bind("<Key>", self.handle_keypress)
    
    def start_game_prompt(self):
        """Prompt the user to choose a difficulty level."""
        difficulty = simpledialog.askstring("Difficulty Level", "Choose Difficulty: Easy, Medium, or Hard")
        if difficulty and difficulty.lower() == "medium":
            self.grid[random.randint(0, 3)][random.randint(0, 3)] = 4
        elif difficulty and difficulty.lower() == "hard":
            for _ in range(2):
                self.grid[random.randint(0, 3)][random.randint(0, 3)] = 4
    
    def load_high_score(self):
        """Load the high score from the leaderboard file."""
        try:
            with open(LEADERBOARD_FILE, "r") as file:
                data = json.load(file)
                return data.get("high_score", 0)
        except FileNotFoundError:
            return 0
    
    def save_high_score(self):
        """Save the high score to the leaderboard file."""
        with open(LEADERBOARD_FILE, "w") as file:
            json.dump({"high_score": self.high_score}, file)
    
    def add_new_tile(self):
        """Add a new tile (2 or 4) to a random empty cell."""
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
    
    def update_grid(self):
        """Update the grid UI based on the current grid state."""
        for i in range(4):
            for j in range(4):
                value = self.grid[i][j]
                self.cells[i][j].config(
                    text=str(value) if value else "",
                    bg=self.get_color(value)
                )
        self.score_label.config(text=f"Score: {self.score}")
        self.high_score_label.config(text=f"High Score: {self.high_score}")
    
    def get_color(self, value):
        """Get the background color for a given tile value."""
        colors = {
            0: "lightgray", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
            16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
            256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
        }
        return colors.get(value, "black")
    
    def handle_keypress(self, event):
        """Handle keypress events to move the tiles."""
        self.previous_states.append((self.grid, self.score))
        if event.keysym in ("Up", "Down", "Left", "Right"):
            if self.make_move(event.keysym):
                self.add_new_tile()
                self.update_grid()
                if self.check_game_over():
                    self.show_game_over()
    
    def make_move(self, direction):
        """Make a move in the given direction."""
        moved = False
        if direction == "Up":
            moved = self.move_up()
        elif direction == "Down":
            moved = self.move_down()
        elif direction == "Left":
            moved = self.move_left()
        elif direction == "Right":
            moved = self.move_right()
        return moved
    
    def move_up(self):
        """Move tiles up."""
        return self.merge_tiles(transpose=True, reverse=False)
    
    def move_down(self):
        """Move tiles down."""
        return self.merge_tiles(transpose=True, reverse=True)
    
    def move_left(self):
        """Move tiles left."""
        return self.merge_tiles(transpose=False, reverse=False)
    
    def move_right(self):
        """Move tiles right."""
        return self.merge_tiles(transpose=False, reverse=True)
    
    def merge_tiles(self, transpose=False, reverse=False):
        """Merge tiles based on the direction."""
        if transpose:
            self.grid = [list(row) for row in zip(*self.grid)]
        if reverse:
            self.grid = [row[::-1] for row in self.grid]
        
        moved = False
        for row in self.grid:
            compressed = [value for value in row if value != 0]
            merged = []
            skip = False
            for i in range(len(compressed)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(compressed) and compressed[i] == compressed[i + 1]:
                    merged.append(compressed[i] * 2)
                    self.score += compressed[i] * 2
                    if self.score > self.high_score:
                        self.high_score = self.score
                    skip = True
                else:
                    merged.append(compressed[i])
            merged.extend([0] * (4 - len(merged)))
            if merged != row:
                moved = True
            row[:] = merged
        
        if reverse:
            self.grid = [row[::-1] for row in self.grid]
        if transpose:
            self.grid = [list(row) for row in zip(*self.grid)]
        return moved
    
    def check_game_over(self):
        """Check if the game is over (no moves left)."""
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    return False
                if j + 1 < 4 and self.grid[i][j] == self.grid[i][j + 1]:
                    return False
                if i + 1 < 4 and self.grid[i][j] == self.grid[i + 1][j]:
                    return False
        return True
    
    def show_game_over(self):
        """Display the game over message and reset the game."""
        self.save_high_score()
        tk.messagebox.showinfo("Game Over", f"Game Over! Your Score: {self.score}")
        self.master.destroy()


# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
