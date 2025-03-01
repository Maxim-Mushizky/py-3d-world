import numpy as np
from OpenGL.GL import *

class Shape:
    def __init__(self, position=None):
        self.position = np.array(position if position is not None else [0, 0, 0], dtype=np.float32)
        self.vertices = []
        self.colors = []
    
    def get_vertices(self):
        return self.vertices
    
    def get_colors(self):
        return self.colors

class Rectangle(Shape):
    def __init__(self, position=None, width=1.0, height=1.0, color=None):
        super().__init__(position)
        self.width = width
        self.height = height
        
        # Default color (white)
        if color is None:
            color = [1.0, 1.0, 1.0]
        
        # Define the vertices of the rectangle
        half_width = width / 2
        half_height = height / 2
        
        # Define the vertices (x, y, z) of the rectangle
        self.vertices = [
            # Front face
            [-half_width + self.position[0], -half_height + self.position[1], 0.0 + self.position[2]],
            [half_width + self.position[0], -half_height + self.position[1], 0.0 + self.position[2]],
            [half_width + self.position[0], half_height + self.position[1], 0.0 + self.position[2]],
            [-half_width + self.position[0], half_height + self.position[1], 0.0 + self.position[2]],
            
            # Back face
            [-half_width + self.position[0], -half_height + self.position[1], -0.1 + self.position[2]],
            [half_width + self.position[0], -half_height + self.position[1], -0.1 + self.position[2]],
            [half_width + self.position[0], half_height + self.position[1], -0.1 + self.position[2]],
            [-half_width + self.position[0], half_height + self.position[1], -0.1 + self.position[2]],
        ]
        
        # Define colors for each vertex
        self.colors = [color] * len(self.vertices)
        
        # Define the faces (indices of vertices)
        self.faces = [
            # Front face
            [0, 1, 2, 3],
            # Back face
            [4, 5, 6, 7],
            # Left face
            [0, 3, 7, 4],
            # Right face
            [1, 2, 6, 5],
            # Top face
            [3, 2, 6, 7],
            # Bottom face
            [0, 1, 5, 4]
        ]
    
    def get_faces(self):
        return self.faces

class Plane(Shape):
    def __init__(self, position=None, width=100.0, depth=100.0, color=None):
        super().__init__(position)
        self.width = width
        self.depth = depth
        
        # Default color (green for ground)
        if color is None:
            color = [0.0, 0.8, 0.0]  # Green
        
        # Define the vertices of the plane
        half_width = width / 2
        half_depth = depth / 2
        
        # Define the vertices (x, y, z) of the plane
        self.vertices = [
            [-half_width + self.position[0], self.position[1], -half_depth + self.position[2]],
            [half_width + self.position[0], self.position[1], -half_depth + self.position[2]],
            [half_width + self.position[0], self.position[1], half_depth + self.position[2]],
            [-half_width + self.position[0], self.position[1], half_depth + self.position[2]],
        ]
        
        # Define colors for each vertex
        self.colors = [color] * len(self.vertices)

class Cube(Shape):
    def __init__(self, position=None, size=1.0, color=None):
        super().__init__(position)
        
        # Handle both uniform and non-uniform sizes
        if isinstance(size, (int, float)):
            self.width = size
            self.height = size
            self.depth = size
        elif isinstance(size, (list, tuple)) and len(size) == 3:
            self.width = size[0]
            self.height = size[1]
            self.depth = size[2]
        else:
            self.width = 1.0
            self.height = 1.0
            self.depth = 1.0
        
        # Default color (white)
        if color is None:
            color = [1.0, 1.0, 1.0]
        
        # Define the vertices of the cube
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        
        # Define the vertices (x, y, z) of the cube
        self.vertices = [
            # Front face
            [-half_width + self.position[0], -half_height + self.position[1], half_depth + self.position[2]],
            [half_width + self.position[0], -half_height + self.position[1], half_depth + self.position[2]],
            [half_width + self.position[0], half_height + self.position[1], half_depth + self.position[2]],
            [-half_width + self.position[0], half_height + self.position[1], half_depth + self.position[2]],
            
            # Back face
            [-half_width + self.position[0], -half_height + self.position[1], -half_depth + self.position[2]],
            [half_width + self.position[0], -half_height + self.position[1], -half_depth + self.position[2]],
            [half_width + self.position[0], half_height + self.position[1], -half_depth + self.position[2]],
            [-half_width + self.position[0], half_height + self.position[1], -half_depth + self.position[2]],
        ]
        
        # Define colors for each vertex
        self.colors = [color] * len(self.vertices)
        
        # Define the faces (indices of vertices)
        self.faces = [
            # Front face
            [0, 1, 2, 3],
            # Back face
            [4, 5, 6, 7],
            # Left face
            [0, 3, 7, 4],
            # Right face
            [1, 2, 6, 5],
            # Top face
            [3, 2, 6, 7],
            # Bottom face
            [0, 1, 5, 4]
        ]
    
    def get_faces(self):
        return self.faces 