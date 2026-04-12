import tkinter as tk
from tkinter import messagebox
from game_logic import SIZE, is_valid_solution
from solver import solve_sequential, solve_threaded, get_one_solution
from database import save_solution, save_player, save_performance
import time

CELL = 50


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sixteen Queens 👑")

        self.board = [-1] * SIZE

        # store correct solution (for hint)
        self.correct_solution = None

        # Name input
        tk.Label(root, text="Player Name").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack()

        # Buttons
        tk.Button(root, text="Run Sequential", command=self.run_seq).pack()
        tk.Button(root, text="Run Threaded", command=self.run_thread).pack()

        self.canvas = tk.Canvas(root, width=SIZE * CELL, height=SIZE * CELL)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)

        tk.Button(root, text="Submit", command=self.submit).pack()

        self.draw(correct=False)

    # ================= DRAW BOARD =================
    def draw(self, correct=False):
        self.canvas.delete("all")

        for r in range(SIZE):
            for c in range(SIZE):
                color = "white" if (r + c) % 2 == 0 else "gray"

                self.canvas.create_rectangle(
                    c * CELL, r * CELL,
                    (c + 1) * CELL, (r + 1) * CELL,
                    fill=color
                )

                if self.board[r] == c:
                    # 🔴 show red queen if correct solution is displayed
                    if correct:
                        self.canvas.create_text(
                            c * CELL + 25,
                            r * CELL + 25,
                            text="👑",
                            fill="red",
                            font=("Arial", 24)
                        )
                    else:
                        self.canvas.create_text(
                            c * CELL + 25,
                            r * CELL + 25,
                            text="👑",
                            font=("Arial", 24)
                        )

    # ================= CLICK =================
    def click(self, event):
        r = event.y // CELL
        c = event.x // CELL

        # ✅ SAFE BOUNDARY CHECK (IMPORTANT FIX)
        if r < 0 or r >= SIZE or c < 0 or c >= SIZE:
            return

        self.board[r] = c if self.board[r] != c else -1
        self.draw()

    # ================= SUBMIT =================
    def submit(self):
        name = self.name_entry.get()

        if not name:
            messagebox.showerror("Error", "Enter name")
            return

        # ✅ VALID SOLUTION
        if is_valid_solution(self.board):
            sol = ",".join(map(str, self.board))

            if save_solution(sol):
                save_player(name, sol)
                messagebox.showinfo("Success", "✅ Valid Solution Saved")
            else:
                messagebox.showwarning("Duplicate", "⚠️ Already Found Solution")

        # ❌ INVALID → SHOW CORRECT SOLUTION
        else:
            self.correct_solution = get_one_solution()

            if self.correct_solution:
                self.board = self.correct_solution.copy()
                self.draw(correct=True)

                messagebox.showerror(
                    "Invalid",
                    "❌ Wrong Solution!\nShowing correct answer in RED 👑"
                )
            else:
                messagebox.showerror("Error", "No solution found")

    # ================= SEQUENTIAL =================
    def run_seq(self):
        sols, t = solve_sequential()
        save_performance("Sequential", t)
        messagebox.showinfo(
            "Sequential",
            f"Solutions: {len(sols)}\nTime: {t:.2f}s"
        )

    # ================= THREADED =================
    def run_thread(self):
        sols, t = solve_threaded()
        save_performance("Threaded", t)
        messagebox.showinfo(
            "Threaded",
            f"Solutions: {len(sols)}\nTime: {t:.2f}s"
        )


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()