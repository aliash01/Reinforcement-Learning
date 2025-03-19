import numpy as np
import random
import time

class RLPathfinder:
    def __init__(self, grid, grid_height, grid_width):
        self.grid = grid
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.actions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.action_names = ["Right", "Down", "Left", "Up"]

        self.q_table = {}

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

    def update_grid_reference(self, grid, grid_height, grid_width):
        """Update the grid reference when the grid is modified in the main application"""
        self.grid = grid
        self.grid_height = grid_height
        self.grid_width = grid_width
    
    def is_valid_position(self, position):
        """Check if a position is valid (within grid bounds and not an obstacle)"""
        i, j = position
        return (0 <= i < self.grid_height and 
                0 <= j < self.grid_width and 
                self.grid[i][j] != "X")

