import numpy as np
from engine.shapes import Plane, Cube, Rectangle, InteractiveCube, Triangle, InteractiveTriangle

class World:
    def __init__(self):
        self.objects = []
        self.setup_world()
    
    def setup_world(self):
        # Add ground plane - positioned at y=0 to serve as the floor
        ground = Plane(position=[0, 0, 0], width=100.0, depth=100.0, color=[0.0, 0.6, 0.0])  # More vibrant green
        self.objects.append(ground)
        
        # Add some walls - positioned on the ground (y=0) with varying heights
        # Wall 1 - Red wall
        wall1 = Cube(position=[0, 2.5, -20], size=[40.0, 5.0, 1.0], color=[0.8, 0.2, 0.2])
        self.objects.append(wall1)
        
        # Wall 2 - Blue wall
        wall2 = Cube(position=[-20, 3.0, 0], size=[1.0, 6.0, 40.0], color=[0.2, 0.2, 0.8])
        self.objects.append(wall2)
        
        # Wall 3 - Yellow wall
        wall3 = Cube(position=[20, 2.0, 0], size=[1.0, 4.0, 40.0], color=[0.8, 0.8, 0.2])
        self.objects.append(wall3)
        
        # Add a few smaller objects on the ground
        # Small cube 1 - Purple
        cube1 = Cube(position=[5, 0.5, 5], size=1.0, color=[0.8, 0.0, 0.8])
        self.objects.append(cube1)
        
        # Small cube 2 - Cyan
        cube2 = Cube(position=[-5, 0.5, 5], size=1.0, color=[0.0, 0.8, 0.8])
        self.objects.append(cube2)
        
        # Add a platform for jumping practice
        platform1 = Cube(position=[-8, 2.0, -8], size=[4.0, 0.5, 4.0], color=[0.7, 0.4, 0.3])
        self.objects.append(platform1)
        
        # Add a single interactive cube - medium weight and friction
        medium_box = InteractiveCube(
            position=[0, 0.75, 3],
            size=1.5,
            color=[0.2, 0.6, 0.8],  # Blue
            mass=20.0,
            friction=0.3
        )
        self.objects.append(medium_box)
        
        # Add a single interactive triangle
        interactive_triangle = InteractiveTriangle(
            position=[3, 0, 0],
            size=2.5,
            height=2.0,
            color=[0.9, 0.3, 0.1],  # Orange-red
            mass=15.0,
            friction=0.2
        )
        self.objects.append(interactive_triangle)
    
    def get_objects(self):
        return self.objects
        
    def get_interactive_objects(self):
        """Return only the interactive objects in the world"""
        return [obj for obj in self.objects if isinstance(obj, (InteractiveCube, InteractiveTriangle))] 