import tkinter as tk
from tkinter import messagebox, ttk
import threading
import database as db
import solver
from game_logic import SIZE, QUEEN_COUNT, is_valid_solution

CELL = 35
COLOR_1 = "#DDB88C"
COLOR_2 = "#A66D4F"

class QueenGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sixteen Queens Puzzle")
        self.board = [-1] * SIZE
        self.is_calculating = False  # Flag to prevent multiple clicks
        self.setup_ui()

    def setup_ui(self):
        # Header with status
        self.header = tk.Label(self.root, text=f"Place {QUEEN_COUNT} Queens", font=("Arial", 14, "bold"))
        self.header.pack(pady=10)

        # Name Input
        name_frame = tk.Frame(self.root)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="Player Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(side=tk.LEFT, padx=5)

        # Board Canvas
        self.canvas = tk.Canvas(self.root, width=SIZE*CELL, height=SIZE*CELL, highlightthickness=0)
        self.canvas.pack(pady=10, padx=20)
        self.canvas.bind("<Button-1>", self.on_click)

        # Controls
        self.ctrl_frame = tk.Frame(self.root)
        self.ctrl_frame.pack(pady=15)
        
        self.btn_seq = tk.Button(self.ctrl_frame, text="Run Sequential", width=15, command=self.run_seq)
        self.btn_seq.grid(row=0, column=0, padx=5)
        
        self.btn_thread = tk.Button(self.ctrl_frame, text="Run Threaded", width=15, command=self.run_thread)
        self.btn_thread.grid(row=0, column=1, padx=5)
        
        self.btn_submit = tk.Button(self.ctrl_frame, text="SUBMIT", width=15, bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.submit)
        self.btn_submit.grid(row=0, column=2, padx=5)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(SIZE):
            for c in range(SIZE):
                color = COLOR_1 if (r + c) % 2 == 0 else COLOR_2
                self.canvas.create_rectangle(c*CELL, r*CELL, (c+1)*CELL, (r+1)*CELL, fill=color, outline=color)
                if self.board[r] == c:
                    self.canvas.create_text(c*CELL+CELL/2, r*CELL+CELL/2, text="♛", font=("Arial", 20), fill="#2c3e50")
        
        count = sum(1 for x in self.board if x != -1)
        self.header.config(text=f"Queens Placed: {count} / {QUEEN_COUNT}")

    def on_click(self, event):
        if self.is_calculating: return
        col, row = event.x // CELL, event.y // CELL
        if 0 <= row < SIZE and 0 <= col < SIZE:
            # Toggle queen
            self.board[row] = col if self.board[row] != col else -1
            self.draw_board()

    def set_ui_state(self, state):
        """Disables or enables buttons during long calculations."""
        self.is_calculating = (state == "disabled")
        btn_state = "disabled" if self.is_calculating else "normal"
        self.btn_seq.config(state=btn_state)
        self.btn_thread.config(state=btn_state)
        self.btn_submit.config(state=btn_state)
        if self.is_calculating:
            self.root.config(cursor="watch")
        else:
            self.root.config(cursor="")

    def run_seq(self):
        self.set_ui_state("disabled")
        self.header.config(text="Calculating Sequential (Please Wait)...", fg="blue")
        
        def task():
            try:
                # 1. Using Sequential program to find max solutions
                count, duration = solver.solve_sequential()
                # 2. Save answers/record time in Database
                db.save_performance("Sequential", count, duration)
                # 3. Return result to main thread
                self.root.after(0, lambda: self.finish_bench("Sequential", count, duration))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=task, daemon=True).start()

    def run_thread(self):
        self.set_ui_state("disabled")
        self.header.config(text="Calculating Threaded (Please Wait)...", fg="green")
        
        def task():
            try:
                # 1. Using Threaded program to find max solutions
                count, duration = solver.solve_threaded()
                # 2. Save answers/record time in Database
                db.save_performance("Threaded", count, duration)
                # 3. Return result to main thread
                self.root.after(0, lambda: self.finish_bench("Threaded", count, duration))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=task, daemon=True).start()

    def finish_bench(self, mode, count, duration):
        self.set_ui_state("normal")
        self.draw_board()
        messagebox.showinfo(f"{mode} Complete", 
                            f"Max Solutions Found: {count}\n"
                            f"Time Taken: {duration:.4f} seconds\n\n"
                            "Data has been saved to the Database.")

    def submit(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter player name first.")
            return

        if is_valid_solution(self.board):
            sol_str = ",".join(map(str, self.board))
            # Save person's name + correct response in DB
            if db.save_solution(sol_str):
                db.save_player(name, sol_str)
                messagebox.showinfo("Success", f"Correct! Solution recognized for {name}.")
                
                # Check if system should clear the 'recognized' flag
                # (Assuming max solutions threshold met)
                if db.get_found_count() >= 10: # Adjustment for testing
                    db.clear_solution_flags()
                    messagebox.showinfo("Reset", "All solutions found! The solution flag has been cleared for future players.")
            else:
                # Indicate solution has already been recognized
                messagebox.showwarning("Already Known", "This solution has already been recognized! Try a different one.")
        else:
            messagebox.showerror("Invalid", "This is not a valid 8-queen configuration.")

if __name__ == "__main__":
    root = tk.Tk()
    # Apply modern theme
    style = ttk.Style(root)
    app = QueenGame(root)
    root.mainloop()