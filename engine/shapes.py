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
        
    def update_vertices(self):
        """Update vertices based on current position"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        
        # Update the vertices (x, y, z) of the cube based on current position
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

class InteractiveCube(Cube):
    def __init__(self, position=None, size=1.0, color=None, mass=10.0, friction=0.3, is_movable=True):
        super().__init__(position, size, color)
        
        # Physics properties
        self.mass = mass  # Mass in kg
        self.friction = friction  # Friction coefficient (0-1)
        self.is_movable = is_movable  # Whether the object can be moved
        
        # Dynamic properties
        self.velocity = np.array([0.0, 0.0, 0.0])  # Current velocity vector
        self.acceleration = np.array([0.0, 0.0, 0.0])  # Current acceleration vector
        self.force = np.array([0.0, 0.0, 0.0])  # Current force applied
        
        # Set a slightly different color to distinguish interactive objects
        if color is None:
            # Default to a light blue for interactive objects
            self.colors = [[0.3, 0.5, 0.9]] * len(self.vertices)
    
    def apply_force(self, force_vector):
        """Apply a force to the object"""
        if self.is_movable:
            self.force += np.array(force_vector)
    
    def update(self, dt):
        """Update the object's physics state"""
        if not self.is_movable:
            return
        
        # Calculate acceleration (F = ma, so a = F/m)
        self.acceleration = self.force / self.mass
        
        # Update velocity (v = v0 + at)
        self.velocity += self.acceleration * dt
        
        # Apply friction to slow down the object
        if np.linalg.norm(self.velocity) > 0:
            friction_force = -self.friction * self.velocity
            self.velocity += friction_force * dt
            
            # Stop the object if it's moving very slowly
            if np.linalg.norm(self.velocity) < 0.01:
                self.velocity = np.array([0.0, 0.0, 0.0])
        
        # Update position (p = p0 + vt)
        self.position += self.velocity * dt
        
        # Update vertices to reflect new position
        self.update_vertices()
        
        # Reset force for next frame
        self.force = np.array([0.0, 0.0, 0.0]) 

class Triangle(Shape):
    def __init__(self, position=None, size=1.0, height=None, color=None):
        super().__init__(position)
        
        # Size represents the side length of the base
        self.size = size
        
        # Height of the triangle (if None, use an equilateral triangle height)
        if height is None:
            # For an equilateral triangle, height = side_length * sqrt(3)/2
            self.height = size * np.sqrt(3) / 2
        else:
            self.height = height
            
        # Default color (white)
        if color is None:
            color = [1.0, 1.0, 1.0]
            
        # Calculate vertices
        half_size = size / 2
        
        # Define the vertices (x, y, z) of the triangle
        # Base is on the xz plane, apex points up in y direction
        self.vertices = [
            # Base vertices
            [-half_size + self.position[0], self.position[1], half_size + self.position[2]],  # Front left
            [half_size + self.position[0], self.position[1], half_size + self.position[2]],   # Front right
            [0 + self.position[0], self.position[1], -half_size + self.position[2]],          # Back
            
            # Apex vertex
            [0 + self.position[0], self.height + self.position[1], 0 + self.position[2]]      # Top
        ]
        
        # Define colors for each vertex
        self.colors = [color] * len(self.vertices)
        
        # Define the faces (indices of vertices)
        self.faces = [
            # Base face (triangle)
            [0, 1, 2],
            # Side faces (triangles)
            [0, 1, 3],  # Front face
            [1, 2, 3],  # Right face
            [2, 0, 3]   # Left face
        ]
    
    def get_faces(self):
        return self.faces
        
    def update_vertices(self):
        """Update vertices based on current position"""
        half_size = self.size / 2
        
        # Update the vertices (x, y, z) of the triangle based on current position
        self.vertices = [
            # Base vertices
            [-half_size + self.position[0], self.position[1], half_size + self.position[2]],  # Front left
            [half_size + self.position[0], self.position[1], half_size + self.position[2]],   # Front right
            [0 + self.position[0], self.position[1], -half_size + self.position[2]],          # Back
            
            # Apex vertex
            [0 + self.position[0], self.height + self.position[1], 0 + self.position[2]]      # Top
        ]

class InteractiveTriangle(Triangle):
    def __init__(self, position=None, size=1.0, height=None, color=None, mass=10.0, friction=0.3, is_movable=True):
        super().__init__(position, size, height, color)
        
        # Physics properties
        self.mass = mass  # Mass in kg
        self.friction = friction  # Friction coefficient (0-1)
        self.is_movable = is_movable  # Whether the object can be moved
        
        # Dynamic properties
        self.velocity = np.array([0.0, 0.0, 0.0])  # Current velocity vector
        self.acceleration = np.array([0.0, 0.0, 0.0])  # Current acceleration vector
        self.force = np.array([0.0, 0.0, 0.0])  # Current force applied
        
        # Set a slightly different color to distinguish interactive objects
        if color is None:
            # Default to a light green for interactive triangles
            self.colors = [[0.3, 0.9, 0.5]] * len(self.vertices)
    
    def apply_force(self, force_vector):
        """Apply a force to the object"""
        if self.is_movable:
            self.force += np.array(force_vector)
    
    def update(self, dt):
        """Update the object's physics state"""
        if not self.is_movable:
            return
        
        # Calculate acceleration (F = ma, so a = F/m)
        self.acceleration = self.force / self.mass
        
        # Update velocity (v = v0 + at)
        self.velocity += self.acceleration * dt
        
        # Apply friction to slow down the object
        if np.linalg.norm(self.velocity) > 0:
            friction_force = -self.friction * self.velocity
            self.velocity += friction_force * dt
            
            # Stop the object if it's moving very slowly
            if np.linalg.norm(self.velocity) < 0.01:
                self.velocity = np.array([0.0, 0.0, 0.0])
        
        # Update position (p = p0 + vt)
        self.position += self.velocity * dt
        
        # Update vertices to reflect new position
        self.update_vertices()
        
        # Reset force for next frame
        self.force = np.array([0.0, 0.0, 0.0]) 

class Sphere(Shape):
    def __init__(self, position=None, radius=1.0, color=None, resolution=16):
        super().__init__(position)
        self.radius = radius
        self.resolution = resolution  # Controls the detail of the sphere
        
        # Default color (white)
        if color is None:
            color = [1.0, 1.0, 1.0]
        
        # For a sphere, we'll store the color but not pre-compute vertices
        # The vertices will be generated during rendering using gluSphere
        self.color = color
        
        # Store a single color for the entire sphere
        self.colors = [color]
    
    def get_bounding_box(self):
        """Return the bounding box of the sphere as (min_x, min_y, min_z, max_x, max_y, max_z)"""
        return (
            self.position[0] - self.radius,
            self.position[1] - self.radius,
            self.position[2] - self.radius,
            self.position[0] + self.radius,
            self.position[1] + self.radius,
            self.position[2] + self.radius
        )

class InteractiveSphere(Sphere):
    def __init__(self, position=None, radius=1.0, color=None, resolution=16, mass=10.0, friction=0.3, is_movable=True):
        super().__init__(position, radius, color, resolution)
        
        # Physics properties
        self.mass = mass  # Mass in kg
        self.friction = friction  # Friction coefficient (0-1)
        self.is_movable = is_movable  # Whether the object can be moved
        
        # Dynamic properties
        self.velocity = np.array([0.0, 0.0, 0.0])  # Current velocity vector
        self.acceleration = np.array([0.0, 0.0, 0.0])  # Current acceleration vector
        self.force = np.array([0.0, 0.0, 0.0])  # Current force applied
        
        # Set a slightly different color to distinguish interactive objects
        if color is None:
            # Default to a light purple for interactive spheres
            self.color = [0.7, 0.3, 0.9]
            self.colors = [[0.7, 0.3, 0.9]]
    
    def apply_force(self, force_vector):
        """Apply a force to the object"""
        if self.is_movable:
            self.force += np.array(force_vector)
    
    def update(self, dt):
        """Update the object's physics state"""
        if not self.is_movable:
            return
        
        # Calculate acceleration (F = ma, so a = F/m)
        self.acceleration = self.force / self.mass
        
        # Update velocity (v = v0 + at)
        self.velocity += self.acceleration * dt
        
        # Apply friction to slow down the object
        if np.linalg.norm(self.velocity) > 0:
            friction_force = -self.friction * self.velocity
            self.velocity += friction_force * dt
            
            # Stop the object if it's moving very slowly
            if np.linalg.norm(self.velocity) < 0.01:
                self.velocity = np.array([0.0, 0.0, 0.0])
        
        # Update position (p = p0 + vt)
        self.position += self.velocity * dt
        
        # Reset force for next frame
        self.force = np.array([0.0, 0.0, 0.0])