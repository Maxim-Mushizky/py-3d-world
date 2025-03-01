import numpy as np
from engine.shapes import Plane, Cube, Rectangle, InteractiveCube, Triangle, InteractiveTriangle, Sphere, InteractiveSphere

class World:
    def __init__(self):
        self.objects = []
        self.setup_world()
    
    def setup_world(self):
        # Add ground plane with more natural color
        ground = Plane(position=[0, 0, 0], width=150.0, depth=150.0, color=[0.2, 0.6, 0.2])  # More natural green
        self.objects.append(ground)
        
        # Create a more organized and visually appealing world
        
        # === TERRAIN FEATURES ===
        
        # Add hills in the distance
        self._create_hills()
        
        # Add a small lake
        self._create_lake(position=[-25, 0.05, -15], size=15)
        
        # === MAIN STRUCTURES ===
        
        # Central structure - a small castle/fort
        self._create_castle(position=[0, 0, -20], size=6.0)
        
        # Platforms for jumping practice arranged in a path
        self._create_platform_path(start_pos=[8, 0, 8], count=5)
        
        # === DECORATIVE ELEMENTS ===
        
        # Create a forest area with different types of trees
        self._create_forest(area=[-40, -40, 40, 40], count=20)
        
        # Create a stone circle
        self._create_stone_circle(position=[20, 0, -25], radius=8, stone_count=8)
        
        # === INTERACTIVE OBJECTS ===
        
        # Add a few interactive cubes with different properties
        self._add_interactive_cubes()
        
        # Add interactive spheres (fewer and more strategically placed)
        self._add_interactive_spheres()
    
    def _create_hills(self):
        """Create distant hills for visual interest"""
        hill_positions = [
            [-50, 0, -50],
            [-40, 0, -60],
            [-60, 0, -40],
            [50, 0, -50],
            [40, 0, -60],
            [60, 0, -40],
            [-50, 0, 50],
            [-40, 0, 60],
            [-60, 0, 40],
            [50, 0, 50],
            [40, 0, 60],
            [60, 0, 40],
        ]
        
        for pos in hill_positions:
            # Randomize hill size and color slightly
            size = 10 + np.random.rand() * 8
            height = 8 + np.random.rand() * 6
            
            # Create a hill using a triangle
            hill = Triangle(
                position=pos,
                size=size,
                height=height,
                color=[0.2, 0.4 + np.random.rand() * 0.2, 0.1]  # Varied green-brown
            )
            self.objects.append(hill)
    
    def _create_lake(self, position, size):
        """Create a small lake"""
        lake = Plane(
            position=position,
            width=size,
            depth=size,
            color=[0.1, 0.3, 0.7]  # Blue water
        )
        self.objects.append(lake)
        
        # Add a few rocks around the lake
        for i in range(6):
            angle = i * np.pi / 3
            rock_pos = [
                position[0] + np.cos(angle) * (size/2 + 1),
                position[1] + 0.5,
                position[2] + np.sin(angle) * (size/2 + 1)
            ]
            
            rock_size = 0.5 + np.random.rand() * 0.8
            rock = Cube(
                position=rock_pos,
                size=rock_size,
                color=[0.5, 0.5, 0.5]  # Gray
            )
            self.objects.append(rock)
    
    def _create_castle(self, position, size):
        """Create a small castle/fort structure"""
        # Base platform
        base = Cube(
            position=[position[0], position[1] + size/4, position[2]],
            size=[size * 2, size/2, size * 2],
            color=[0.6, 0.6, 0.6]  # Gray stone
        )
        self.objects.append(base)
        
        # Main building
        main_building = Cube(
            position=[position[0], position[1] + size/2 + size/4, position[2]],
            size=[size * 1.5, size, size * 1.5],
            color=[0.7, 0.6, 0.5]  # Tan stone
        )
        self.objects.append(main_building)
        
        # Towers at corners
        tower_positions = [
            [position[0] + size * 0.6, position[1], position[2] + size * 0.6],
            [position[0] + size * 0.6, position[1], position[2] - size * 0.6],
            [position[0] - size * 0.6, position[1], position[2] + size * 0.6],
            [position[0] - size * 0.6, position[1], position[2] - size * 0.6]
        ]
        
        for tower_pos in tower_positions:
            tower = Cube(
                position=[tower_pos[0], tower_pos[1] + size, tower_pos[2]],
                size=[size/3, size*1.5, size/3],
                color=[0.65, 0.55, 0.45]  # Slightly different tan
            )
            self.objects.append(tower)
            
            # Tower top
            tower_top = Triangle(
                position=[tower_pos[0], tower_pos[1] + size*1.5, tower_pos[2]],
                size=size/2,
                height=size/2,
                color=[0.8, 0.2, 0.2]  # Red roof
            )
            self.objects.append(tower_top)
    
    def _create_platform_path(self, start_pos, count):
        """Create a path of platforms for jumping practice"""
        current_pos = list(start_pos)
        
        for i in range(count):
            # Vary height slightly for each platform
            height = 1.0 + (i * 0.5)
            
            # Create platform
            platform = Cube(
                position=[current_pos[0], height/2, current_pos[2]],
                size=[4.0 - i * 0.4, height, 4.0 - i * 0.4],
                color=[0.5, 0.5 + i * 0.1, 0.7]  # Increasingly blue
            )
            self.objects.append(platform)
            
            # Move to next position in a spiral pattern
            angle = (i + 1) * np.pi / 2
            distance = 6 + i * 0.5
            current_pos[0] += np.cos(angle) * distance
            current_pos[2] += np.sin(angle) * distance
    
    def _create_forest(self, area, count):
        """Create a forest with different types of trees"""
        min_x, min_z, max_x, max_z = area
        
        for _ in range(count):
            # Random position within the area
            pos_x = min_x + np.random.rand() * (max_x - min_x)
            pos_z = min_z + np.random.rand() * (max_z - min_z)
            
            # Skip if too close to center or other important areas
            if (abs(pos_x) < 15 and abs(pos_z) < 15) or \
               (pos_x > -30 and pos_x < -20 and pos_z > -20 and pos_z < -10) or \
               (pos_x > 15 and pos_x < 25 and pos_z > -30 and pos_z < -20):
                continue
            
            # Randomly choose tree type
            tree_type = np.random.choice(['pine', 'oak', 'birch'])
            
            if tree_type == 'pine':
                self._create_pine_tree([pos_x, 0, pos_z])
            elif tree_type == 'oak':
                self._create_oak_tree([pos_x, 0, pos_z])
            else:
                self._create_birch_tree([pos_x, 0, pos_z])
    
    def _create_pine_tree(self, position):
        """Create a pine tree (tall with multiple triangle layers)"""
        # Tree trunk
        trunk = Cube(
            position=[position[0], 3.0, position[2]],
            size=[0.8, 6.0, 0.8],
            color=[0.45, 0.3, 0.05]  # Dark brown
        )
        self.objects.append(trunk)
        
        # Tree foliage - multiple layers of triangles
        for i in range(3):
            layer_size = 4.0 - i * 0.8
            layer_height = 2.5 - i * 0.5
            
            foliage = Triangle(
                position=[position[0], 3.0 + i * 2.0, position[2]],
                size=layer_size,
                height=layer_height,
                color=[0.0, 0.4 + i * 0.1, 0.0]  # Green, getting lighter at top
            )
            self.objects.append(foliage)
    
    def _create_oak_tree(self, position):
        """Create an oak tree (shorter trunk with a large foliage cube)"""
        # Tree trunk
        trunk = Cube(
            position=[position[0], 2.0, position[2]],
            size=[1.0, 4.0, 1.0],
            color=[0.5, 0.35, 0.05]  # Brown
        )
        self.objects.append(trunk)
        
        # Tree foliage - large cube
        foliage = Cube(
            position=[position[0], 5.5, position[2]],
            size=4.5,
            color=[0.2, 0.5, 0.1]  # Dark green
        )
        self.objects.append(foliage)
    
    def _create_birch_tree(self, position):
        """Create a birch tree (thin white trunk with a smaller foliage)"""
        # Tree trunk
        trunk = Cube(
            position=[position[0], 2.5, position[2]],
            size=[0.6, 5.0, 0.6],
            color=[0.9, 0.9, 0.8]  # White/light gray
        )
        self.objects.append(trunk)
        
        # Tree foliage - smaller, lighter green
        foliage = Cube(
            position=[position[0], 6.0, position[2]],
            size=3.0,
            color=[0.4, 0.7, 0.2]  # Light green
        )
        self.objects.append(foliage)
    
    def _create_stone_circle(self, position, radius, stone_count):
        """Create a circle of standing stones"""
        for i in range(stone_count):
            angle = i * 2 * np.pi / stone_count
            stone_pos = [
                position[0] + np.cos(angle) * radius,
                position[1],
                position[2] + np.sin(angle) * radius
            ]
            
            # Create a tall stone
            stone = Cube(
                position=[stone_pos[0], position[1] + 2.0, stone_pos[2]],
                size=[1.0, 4.0, 1.0],
                color=[0.6, 0.6, 0.6]  # Gray
            )
            self.objects.append(stone)
    
    def _add_interactive_cubes(self):
        """Add interactive cubes to the world"""
        # Light cube - easy to push
        light_box = InteractiveCube(
            position=[-8, 0.75, 8],
            size=1.5,
            color=[0.9, 0.9, 0.2],  # Yellow
            mass=10.0,
            friction=0.2
        )
        self.objects.append(light_box)
        
        # Medium cube
        medium_box = InteractiveCube(
            position=[0, 0.75, 12],
            size=1.5,
            color=[0.2, 0.7, 0.9],  # Light blue
            mass=25.0,
            friction=0.3
        )
        self.objects.append(medium_box)
        
        # Heavy cube - hard to push
        heavy_box = InteractiveCube(
            position=[8, 0.75, 8],
            size=1.5,
            color=[0.8, 0.2, 0.2],  # Red
            mass=50.0,
            friction=0.4
        )
        self.objects.append(heavy_box)
    
    def _add_interactive_spheres(self):
        """Add interactive spheres to the world (sparser placement)"""
        # Small light sphere - very easy to push
        small_sphere = InteractiveSphere(
            position=[-12, 1.0, 0],
            radius=0.8,
            color=[0.3, 0.8, 0.9],  # Light blue
            mass=5.0,
            friction=0.1,
            resolution=24  # Higher resolution for smoother appearance
        )
        self.objects.append(small_sphere)
        
        # Medium sphere - moderate to push
        medium_sphere = InteractiveSphere(
            position=[12, 1.5, -12],
            radius=1.5,
            color=[0.7, 0.3, 0.9],  # Purple
            mass=20.0,
            friction=0.3,
            resolution=24
        )
        self.objects.append(medium_sphere)
        
        # Large heavy sphere - hard to push
        large_sphere = InteractiveSphere(
            position=[0, 2.0, -10],
            radius=2.0,
            color=[0.9, 0.5, 0.1],  # Orange
            mass=80.0,
            friction=0.4,
            resolution=32
        )
        self.objects.append(large_sphere)
    
    def get_objects(self):
        return self.objects
        
    def get_interactive_objects(self):
        """Return only the interactive objects in the world"""
        return [obj for obj in self.objects if isinstance(obj, (InteractiveCube, InteractiveTriangle, InteractiveSphere))] 