import numpy as np
from engine.shapes import Plane, Cube, Rectangle

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
        
        # Add some smaller objects on the ground
        # Small cube 1 - Purple
        cube1 = Cube(position=[5, 0.5, 5], size=1.0, color=[0.8, 0.0, 0.8])
        self.objects.append(cube1)
        
        # Small cube 2 - Cyan
        cube2 = Cube(position=[-5, 0.5, 5], size=1.0, color=[0.0, 0.8, 0.8])
        self.objects.append(cube2)
        
        # Small cube 3 - Orange
        cube3 = Cube(position=[0, 0.5, 10], size=1.0, color=[1.0, 0.5, 0.0])
        self.objects.append(cube3)
        
        # Add a taller structure - like a tower
        tower = Cube(position=[10, 5.0, 10], size=[2.0, 10.0, 2.0], color=[0.5, 0.5, 0.5])
        self.objects.append(tower)
        
        # Add platforms at different heights for jumping practice
        platform1 = Cube(position=[-8, 2.0, -8], size=[4.0, 0.5, 4.0], color=[0.7, 0.4, 0.3])
        self.objects.append(platform1)
        
        platform2 = Cube(position=[8, 3.0, -8], size=[4.0, 0.5, 4.0], color=[0.3, 0.7, 0.4])
        self.objects.append(platform2)
        
        # Create a staircase of platforms for jumping practice
        for i in range(1, 6):
            step = Cube(
                position=[0, i * 1.0, 15 + i * 2], 
                size=[3.0, 0.5, 2.0], 
                color=[0.7, 0.7 - i * 0.1, i * 0.1]
            )
            self.objects.append(step)
        
        # Create a jumping challenge course
        # Starting platform
        start_platform = Cube(position=[-10, 1.0, -15], size=[4.0, 0.5, 4.0], color=[0.8, 0.8, 0.8])
        self.objects.append(start_platform)
        
        # Platforms with increasing gaps
        for i in range(1, 5):
            jump_platform = Cube(
                position=[-10 + i * (3 + i), 1.0, -15], 
                size=[3.0, 0.5, 3.0], 
                color=[0.8, 0.8 - i * 0.15, 0.8 - i * 0.15]
            )
            self.objects.append(jump_platform)
    
    def get_objects(self):
        return self.objects 