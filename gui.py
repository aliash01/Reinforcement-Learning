import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import heapq
import time
from pathfinding import PathfindingAlgorithms
from reinforcementlearning import RLPathfinder

'''
Grid-based Pathfinding Visualiser

A visualisation tool which demonstrates various pathfinding algorithms
on a customisable grid. Users can create obstacles, set start/goal positions,
and observe how different algorithms explore the grid.
'''

class GridSizeDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, initial_width=5, initial_height=5):
        self.width = initial_width
        self.height = initial_height
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Grid Width:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        tk.Label(master, text="Grid Height:").grid(row=1, column=0, sticky="w", pady=5, padx=5)

        self.width_entry = tk.Entry(master)
        self.width_entry.grid(row=0, column=1, pady=5, padx=5)
        self.width_entry.insert(0, str(self.width))

        self.height_entry = tk.Entry(master)
        self.height_entry.grid(row=1, column=1, pady=5, padx=5)
        self.height_entry.insert(0, str(self.height))

        return self.width_entry  

    def validate(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            if width < 1 or width > 10 or height < 1 or height > 10:
                messagebox.showerror("Invalid Input", "Grid dimensions must be between 1 and 10.")
                return False

            self.result = (width, height)
            return True
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return False

class VisualGridEnv:
    '''
    Main class for pathfinding visualisation environment.

    Provides an interactive grid where users can:
    - Place start, goal, and obstacle blocks
    - Run different pathfinding algorithms
    - Visualize algorithm explanation and resulting paths
    - Customise grid dimensions
    '''

    # --- Grid Setup and Display ---
    def __init__(self, grid_width=5, grid_height=5, cell_size=80):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.grid = [["O" for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        self.pathfinding = PathfindingAlgorithms(self.grid, self.grid_height, self.grid_width)
        self.reinforcementlearning = RLPathfinder(self.grid, self.grid_height, self.grid_width)

        self.root = tk.Tk()
        self.root.title("Grid Environment Simulator")
        self.root.resizable(False, False)

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=10)

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=10)

        self.resize_btn = tk.Button(self.menu_frame, text="Resize Grid", command=self.resize_grid)
        self.resize_btn.grid(row=0, column=1, padx=5)

        self.sim_btn = tk.Button(self.menu_frame, text="Run Simulation", command=self.run_simulation)
        self.sim_btn.grid(row=0, column=2, padx=5)

        self.canvas_cells = []
        self.create_grid()

        self.root.mainloop()

    def create_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.canvas_cells = []

        self.canvas = tk.Canvas(
            self.grid_frame, 
            width=self.grid_width * self.cell_size,
            height=self.grid_height * self.cell_size,
            bg="white"
        )
        self.canvas.pack()

        for i in range(self.grid_height):
            row_cells = []
            for j in range(self.grid_width):

                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill_color = "white" if self.grid[i][j] == "O" else "black"
                cell = self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="gray")
                self.canvas.tag_bind(cell, "<Button-1>", lambda event, row=i, col=j: self.cell_clicked(row, col))
                row_cells.append(cell)
            self.canvas_cells.append(row_cells)

    def update_grid_display(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.grid[i][j] == "O":
                    fill_color = "white"
                elif self.grid[i][j] == "X":
                    fill_color = "black"
                elif self.grid[i][j] == "S":
                    fill_color = "green"
                elif self.grid[i][j] == "G":
                    fill_color = "yellow"
                elif self.grid[i][j] == "P":  
                    fill_color = "blue"
                else:
                    fill_color = "white"

                self.canvas.itemconfig(self.canvas_cells[i][j], fill=fill_color)

    # --- User Interaction Handlers ---

    def cell_clicked(self, row, col):
        if hasattr(self, 'placement_mode'):
            mode = self.placement_mode.get()

            if mode == "obstacle":

                if self.grid[row][col] not in ["S", "G"]:
                    self.grid[row][col] = "X" if self.grid[row][col] == "O" else "O"

            elif mode == "start":

                for i in range(self.grid_height):
                    for j in range(self.grid_width):
                        if self.grid[i][j] == "S":
                            self.grid[i][j] = "O"

                if self.grid[row][col] != "X" and self.grid[row][col] != "G":
                    self.grid[row][col] = "S"

            elif mode == "goal":

                for i in range(self.grid_height):
                    for j in range(self.grid_width):
                        if self.grid[i][j] == "G":
                            self.grid[i][j] = "O"

                if self.grid[row][col] != "X" and self.grid[row][col] != "S":
                    self.grid[row][col] = "G"

        self.update_grid_display()

    def update_placement_mode(self):
        mode = self.placement_mode.get()
        if mode == "start":
            self.canvas.config(cursor="cross green")
            self.current_mode = "view"  
        elif mode == "goal":
            self.canvas.config(cursor="cross yellow")
            self.current_mode = "view"
        elif mode == "obstacle":
            self.canvas.config(cursor="cross black")
            self.current_mode = "toggle"  
        else:
            self.canvas.config(cursor="")
            self.current_mode = "view"

    def resize_grid(self):
        try:
            dialog = GridSizeDialog(
                self.root, 
                "Resize Grid", 
                initial_width=self.grid_width,
                initial_height=self.grid_height
            )

            if dialog.result:  
                new_width, new_height = dialog.result

                new_grid = [["O" for _ in range(new_width)] for _ in range(new_height)]
                for i in range(min(self.grid_height, new_height)):
                    for j in range(min(self.grid_width, new_width)):
                        new_grid[i][j] = self.grid[i][j]

                self.grid_width = new_width
                self.grid_height = new_height
                self.grid = new_grid

                self.pathfinding.update_grid_reference(self.grid, self.grid_height, self.grid_width)
                self.reinforcementlearning.update_grid_reference(self.grid, self.grid_height, self.grid_width)

                self.create_grid()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize grid: {str(e)}")

    def run_simulation(self):
        sim_window = tk.Toplevel(self.root)
        sim_window.title("Simulation")
        sim_window.geometry("400x300")  

        main_window_x = self.root.winfo_x()
        main_window_width = self.root.winfo_width()
        sim_window_x = main_window_x + main_window_width + 10  
        main_window_y = self.root.winfo_y()
        sim_window.geometry(f"+{sim_window_x}+{main_window_y}")

        mode_frame = tk.Frame(sim_window)
        mode_frame.pack(pady=10)

        self.placement_mode = tk.StringVar(value="none")

        tk.Radiobutton(mode_frame, text="Normal Mode", variable=self.placement_mode, 
                    value="none", command=self.update_placement_mode).grid(row=0, column=0, padx=5)
        tk.Radiobutton(mode_frame, text="Set Start", variable=self.placement_mode, 
                    value="start", command=self.update_placement_mode).grid(row=0, column=1, padx=5)
        tk.Radiobutton(mode_frame, text="Set Goal", variable=self.placement_mode, 
                    value="goal", command=self.update_placement_mode).grid(row=0, column=2, padx=5)
        tk.Radiobutton(mode_frame, text="Set Obstacles", variable=self.placement_mode, 
                    value="obstacle", command=self.update_placement_mode).grid(row=0, column=3, padx=5)

        alg_frame = tk.Frame(sim_window)
        alg_frame.pack(pady=10)

        tk.Button(alg_frame, text="A*", command=self.a_star).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(alg_frame, text="BFS", command=self.BFS).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(alg_frame, text="Dijkstra", command=self.dijkstra).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(alg_frame, text="DFS", command=self.DFS).grid(row=0, column=3, padx=5, pady=5)

        vis_frame = tk.Frame(sim_window)
        vis_frame.pack(pady=5)

        self.visualization_mode = tk.StringVar(value="final_path")

        tk.Label(vis_frame, text="Visualization:").grid(row=0, column=0, padx=5)
        tk.Radiobutton(vis_frame, text="Final Path Only", variable=self.visualization_mode, 
                    value="final_path").grid(row=0, column=1, padx=5)
        tk.Radiobutton(vis_frame, text="Show Exploration", variable=self.visualization_mode, 
                    value="exploration").grid(row=0, column=2, padx=5)

        tk.Label(sim_window, text="Click on grid to set positions", font=("Arial", 12)).pack(pady=10)

        tk.Button(sim_window, text="Clear Path", command=self.clear_path).pack(pady=5)
        tk.Button(sim_window, text="Close", command=sim_window.destroy).pack(pady=10)

# --- Position Management --- 

    def set_start_position(self):
        start_dialog = tk.Toplevel(self.root)
        start_dialog.title("Set Start Position")
        start_dialog.geometry("300x150")
        start_dialog.resizable(False, False)

        start_dialog.grab_set()  

        tk.Label(start_dialog, text="X coordinate (0-{}):".format(self.grid_width-1)).pack(pady=(10, 5))
        x_entry = tk.Entry(start_dialog, width=10)
        x_entry.pack()

        tk.Label(start_dialog, text="Y coordinate (0-{}):".format(self.grid_height-1)).pack(pady=(10, 5))
        y_entry = tk.Entry(start_dialog, width=10)
        y_entry.pack()

        def submit_coords():
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())

                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:

                    for i in range(self.grid_height):
                        for j in range(self.grid_width):
                            if self.grid[i][j] == "S":
                                self.grid[i][j] = "O"

                    self.grid[y][x] = "S"
                    self.update_grid_display()  
                    start_dialog.destroy()
                else:
                    messagebox.showerror("Invalid Coordinates", 
                                        f"Coordinates must be within grid bounds (0-{self.grid_width-1}, 0-{self.grid_height-1})")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for coordinates.")

        tk.Button(start_dialog, text="Set Start", command=submit_coords).pack(pady=10)

    def set_goal_position(self):
        goal_dialog = tk.Toplevel(self.root)
        goal_dialog.title("Set Goal Position")
        goal_dialog.geometry("300x150")
        goal_dialog.resizable(False, False)

        goal_dialog.grab_set()  

        tk.Label(goal_dialog, text="X coordinate (0-{}):".format(self.grid_width-1)).pack(pady=(10, 5))
        x_entry = tk.Entry(goal_dialog, width=10)
        x_entry.pack()

        tk.Label(goal_dialog, text="Y coordinate (0-{}):".format(self.grid_height-1)).pack(pady=(10, 5))
        y_entry = tk.Entry(goal_dialog, width=10)
        y_entry.pack()

        def submit_coords():
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())

                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:

                    for i in range(self.grid_height):
                        for j in range(self.grid_width):
                            if self.grid[i][j] == "G":
                                self.grid[i][j] = "O"

                    self.grid[y][x] = "G"
                    self.update_grid_display()  
                    goal_dialog.destroy()
                else:
                    messagebox.showerror("Invalid Coordinates", 
                                        f"Coordinates must be within grid bounds (0-{self.grid_width-1}, 0-{self.grid_height-1})")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for coordinates.")

        tk.Button(goal_dialog, text="Set Goal", command=submit_coords).pack(pady=10)

    def find_start_and_goal(self):
        if not self.check_grid("S") or not self.check_grid("G"):
            messagebox.showwarning("Missing Points", "Please set both start and goal positions.")
            return None, None

        start = None
        goal = None
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.grid[i][j] == "S":
                    start = (i, j)
                elif self.grid[i][j] == "G":
                    goal = (i, j)

        return start, goal

    def check_grid(self, check):
        for row in self.grid:
            if check in row:
                return True
        return False

# --- Path Management ---

    def clear_path(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.grid[i][j] not in ["S", "G", "X"]:  
                    self.grid[i][j] = "O"  
        self.update_grid_display()

    def reconstruct_path(self, came_from, start, goal, algorithm_name="Pathfinding"):
        if goal not in came_from:
            messagebox.showinfo(algorithm_name, "No path found!")
            return

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]

        for i, j in reversed(path):
            if self.grid[i][j] not in ["S", "G"]:
                self.grid[i][j] = "P"
                self.canvas.itemconfig(self.canvas_cells[i][j], fill="blue")
                self.root.update()
                time.sleep(0.1)  

        messagebox.showinfo(algorithm_name, "Path found!")

    def visualize_exploration(self, node, is_goal=False):
        if self.visualization_mode.get() == "exploration":
            if self.grid[node[0]][node[1]] not in ["S", "G"]:

                self.canvas.itemconfig(self.canvas_cells[node[0]][node[1]], fill="lightblue")
                self.root.update()
                time.sleep(0.1)  

# --- Pathfinding Algorithms ---

    def a_star(self):
        self.clear_path()
        start, goal = self.find_start_and_goal()
        if start is None or goal is None:
            return
            
        came_from = self.pathfinding.a_star(start, goal, self.visualize_exploration)
        self.reconstruct_path(came_from, start, goal, "A*")

    def BFS(self):
        self.clear_path()
        start, goal = self.find_start_and_goal()
        if start is None or goal is None:
            return
            
        came_from = self.pathfinding.bfs(start, goal, self.visualize_exploration)
        self.reconstruct_path(came_from, start, goal, "BFS")

    def dijkstra(self):
        self.clear_path()
        start, goal = self.find_start_and_goal()
        if start is None or goal is None:
            return
            
        came_from = self.pathfinding.dijkstra(start, goal, self.visualize_exploration)
        self.reconstruct_path(came_from, start, goal, "Dijkstra")

    def DFS(self):
        self.clear_path()
        start, goal = self.find_start_and_goal()
        if start is None or goal is None:
            return
        came_from = self.pathfinding.dfs(start, goal, self.visualize_exploration)
        self.reconstruct_path(came_from, start, goal, "DFS")

# --- Reinforcement Learning ---

    def RL(self):
        self.clear_path()
        start, goal = self.find_start_and_goal()
        if start is None or goal is None:
            return
        came_from = self.reinforcementlearning.RLPathfinder(start, goal, self.visualize_exploration)

if __name__ == "__main__":
    app = VisualGridEnv()