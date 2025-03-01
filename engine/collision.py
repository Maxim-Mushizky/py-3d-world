import numpy as np
from engine.shapes import Cube, Plane, Rectangle, Triangle, InteractiveTriangle, InteractiveCube
import time

class CollisionDetector:
    def __init__(self, world):
        self.world = world
        self.player_radius = 0.5  # Player collision radius (horizontal)
        self.player_height = 1.7  # Player height for vertical collisions
        self.debug = True  # Enable debug output
        self.last_debug_time = 0  # Last time debug message was printed
        self.ground_collision_threshold = 0.05  # Threshold for ground collision detection
        self.ground_check_distance = 0.2  # Distance to check below player for ground
        self._on_ground_last_check = False  # Track if we were on ground in last check
        self._standing_on_object = None  # Track which object we're standing on
        self._standing_height = 0.0  # Height of the object we're standing on
    
    def check_collision(self, position, new_position):
        """
        Check if moving from position to new_position would cause a collision.
        Returns the adjusted position if collision would occur.
        """
        # If no movement, no collision
        if np.array_equal(position, new_position):
            return new_position
        
        # Store previous standing object
        previous_standing_object = self._standing_on_object
        previous_standing_height = self._standing_height
        
        # Reset standing on object for this check
        self._standing_on_object = None
        self._standing_height = 0.0
        
        # Check collisions with all objects in the world
        adjusted_position = np.copy(new_position)
        
        for obj in self.world.get_objects():
            if isinstance(obj, (Cube, Rectangle, InteractiveCube)):
                if self._check_object_collision(obj, position, adjusted_position):
                    # Collision detected, adjust position
                    adjusted_position = self._resolve_object_collision(obj, position, adjusted_position)
                    
                    # If we adjusted the Y position upward, we might be standing on this object
                    if adjusted_position[1] > new_position[1]:
                        self._standing_on_object = obj
                        self._on_ground_last_check = True
                        
                        # Store the height of the object we're standing on
                        if isinstance(obj, Cube):
                            self._standing_height = obj.position[1] + obj.height/2
                        elif isinstance(obj, Rectangle):
                            self._standing_height = obj.position[1] + obj.height
                        
                        if self.debug and time.time() - self.last_debug_time > 1.0:
                            self.last_debug_time = time.time()
                            print(f"Standing on object at position {adjusted_position}, object height: {self._standing_height}")
            elif isinstance(obj, (Triangle, InteractiveTriangle)):
                if self._check_triangle_collision(obj, position, adjusted_position):
                    # Collision detected, adjust position
                    adjusted_position = self._resolve_triangle_collision(obj, position, adjusted_position)
                    
                    # If we adjusted the Y position upward, we might be standing on this object
                    if adjusted_position[1] > new_position[1]:
                        self._standing_on_object = obj
                        self._on_ground_last_check = True
                        
                        # Store the height of the object we're standing on
                        self._standing_height = obj.position[1] + obj.height
                        
                        if self.debug and time.time() - self.last_debug_time > 1.0:
                            self.last_debug_time = time.time()
                            print(f"Standing on triangle at position {adjusted_position}, object height: {self._standing_height}")
            elif isinstance(obj, Plane):
                # For planes, we only check if we're trying to go below the ground
                if obj.position[1] == 0 and adjusted_position[1] < self.player_height:
                    # Only adjust if we're significantly below the expected height
                    if self.player_height - adjusted_position[1] > self.ground_collision_threshold:
                        # Ground collision, keep player at eye height
                        # Only print debug message occasionally to reduce spam
                        current_time = time.time()
                        if self.debug and current_time - self.last_debug_time > 1.0:
                            self.last_debug_time = current_time
                            print(f"Ground collision detected! Adjusting height from {adjusted_position[1]} to {self.player_height}")
                        adjusted_position[1] = self.player_height
                        
                        # If we hit the ground, we're definitely on the ground
                        self._on_ground_last_check = True
                        self._standing_on_object = obj
                        self._standing_height = 0.0
        
        # If we were standing on an object before but not now, check if we're still close enough
        # This helps prevent "falling off" platforms when just moving around on them
        if previous_standing_object and not self._standing_on_object:
            player_feet = adjusted_position[1] - self.player_height
            if abs(player_feet - previous_standing_height) < 0.2:  # Small threshold
                self._standing_on_object = previous_standing_object
                self._standing_height = previous_standing_height
                self._on_ground_last_check = True
                
                # Adjust position to stay on the platform
                adjusted_position[1] = previous_standing_height + self.player_height
                
                if self.debug and time.time() - self.last_debug_time > 1.0:
                    self.last_debug_time = time.time()
                    print(f"Maintaining position on platform at height: {previous_standing_height}")
        
        # Check if we're way above the ground with no platform - apply gravity
        if adjusted_position[1] > self.player_height + 0.1 and not self._standing_on_object:
            # We're in the air and not standing on anything
            if self.debug and time.time() - self.last_debug_time > 1.0:
                self.last_debug_time = time.time()
                print(f"In air at height {adjusted_position[1]}, not standing on any object")
            self._on_ground_last_check = False
        
        return adjusted_position
    
    def _check_object_collision(self, obj, position, new_position):
        """Check if player would collide with an object when moving from position to new_position."""
        if isinstance(obj, (Cube, InteractiveCube)):
            return self._check_cube_collision(obj, position, new_position)
        elif isinstance(obj, Rectangle):
            return self._check_rectangle_collision(obj, position, new_position)
        return False
    
    def _check_cube_collision(self, cube, position, new_position):
        """Check if player would collide with a cube when moving from position to new_position."""
        # Get cube dimensions
        half_width = cube.width / 2
        half_height = cube.height / 2
        half_depth = cube.depth / 2
        
        # Cube boundaries (min and max points)
        cube_min = np.array([
            cube.position[0] - half_width,
            cube.position[1] - half_height,
            cube.position[2] - half_depth
        ])
        
        cube_max = np.array([
            cube.position[0] + half_width,
            cube.position[1] + half_height,
            cube.position[2] + half_depth
        ])
        
        # Expand cube by player radius for collision detection
        cube_min[0] -= self.player_radius
        cube_min[2] -= self.player_radius
        cube_max[0] += self.player_radius
        cube_max[2] += self.player_radius
        
        # Check if new position would be inside the expanded cube
        # We only check X and Z for horizontal movement
        horizontal_collision = (
            new_position[0] >= cube_min[0] and new_position[0] <= cube_max[0] and
            new_position[2] >= cube_min[2] and new_position[2] <= cube_max[2]
        )
        
        # Check vertical collision only if we're within the horizontal bounds
        # and if the player's feet or head would be inside the cube
        vertical_collision = False
        if horizontal_collision:
            player_feet = new_position[1] - self.player_height
            player_head = new_position[1]
            
            vertical_collision = (
                (player_feet <= cube_max[1] and player_feet >= cube_min[1]) or
                (player_head <= cube_max[1] and player_head >= cube_min[1]) or
                (player_feet <= cube_min[1] and player_head >= cube_max[1])
            )
            
            # Check if we're landing on top of the cube
            if not vertical_collision and player_feet <= cube_max[1] + 0.1 and player_feet >= cube_max[1] - 0.1:
                # We're very close to the top of the cube, consider it a landing
                if self.debug and time.time() - self.last_debug_time > 1.0:
                    self.last_debug_time = time.time()
                    print(f"Landing on cube! Player feet: {player_feet}, Cube top: {cube_max[1]}")
                vertical_collision = True
        
        return horizontal_collision and vertical_collision
    
    def _check_rectangle_collision(self, rect, position, new_position):
        """Check if player would collide with a rectangle when moving from position to new_position."""
        # Get rectangle dimensions
        half_width = rect.width / 2
        half_depth = rect.depth / 2
        
        # Rectangle boundaries (min and max points)
        rect_min = np.array([
            rect.position[0] - half_width,
            rect.position[1],  # Bottom of rectangle
            rect.position[2] - half_depth
        ])
        
        rect_max = np.array([
            rect.position[0] + half_width,
            rect.position[1] + rect.height,  # Top of rectangle
            rect.position[2] + half_depth
        ])
        
        # Expand rectangle by player radius for collision detection
        rect_min[0] -= self.player_radius
        rect_min[2] -= self.player_radius
        rect_max[0] += self.player_radius
        rect_max[2] += self.player_radius
        
        # Check if new position would be inside the expanded rectangle
        # We only check X and Z for horizontal movement
        horizontal_collision = (
            new_position[0] >= rect_min[0] and new_position[0] <= rect_max[0] and
            new_position[2] >= rect_min[2] and new_position[2] <= rect_max[2]
        )
        
        # Check vertical collision only if we're within the horizontal bounds
        # and if the player's feet or head would be inside the rectangle
        vertical_collision = False
        if horizontal_collision:
            player_feet = new_position[1] - self.player_height
            player_head = new_position[1]
            
            vertical_collision = (
                (player_feet <= rect_max[1] and player_feet >= rect_min[1]) or
                (player_head <= rect_max[1] and player_head >= rect_min[1]) or
                (player_feet <= rect_min[1] and player_head >= rect_max[1])
            )
            
            # Check if we're landing on top of the rectangle
            if not vertical_collision and player_feet <= rect_max[1] + 0.1 and player_feet >= rect_max[1] - 0.1:
                # We're very close to the top of the rectangle, consider it a landing
                if self.debug and time.time() - self.last_debug_time > 1.0:
                    self.last_debug_time = time.time()
                    print(f"Landing on rectangle! Player feet: {player_feet}, Rectangle top: {rect_max[1]}")
                vertical_collision = True
        
        return horizontal_collision and vertical_collision
    
    def _resolve_object_collision(self, obj, position, new_position):
        """Resolve collision with an object by adjusting the new position."""
        if isinstance(obj, Cube):
            return self._resolve_cube_collision(obj, position, new_position)
        elif isinstance(obj, Rectangle):
            return self._resolve_rectangle_collision(obj, position, new_position)
        return new_position
    
    def _resolve_cube_collision(self, cube, position, new_position):
        """Resolve collision with a cube by adjusting the new position."""
        # If we're already colliding at the current position, allow some movement
        if self._check_cube_collision(cube, position, position):
            # Calculate direction away from cube center
            direction = position - np.array(cube.position)
            direction[1] = 0  # Only consider horizontal direction
            
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                
                # Move slightly away from cube
                return position + direction * 0.1
            else:
                # If we're exactly at the center, move in any direction
                return position + np.array([0.1, 0, 0])
        
        # Get cube dimensions
        half_width = cube.width / 2
        half_height = cube.height / 2
        half_depth = cube.depth / 2
        
        # Cube boundaries (min and max points)
        cube_min = np.array([
            cube.position[0] - half_width,
            cube.position[1] - half_height,
            cube.position[2] - half_depth
        ])
        
        cube_max = np.array([
            cube.position[0] + half_width,
            cube.position[1] + half_height,
            cube.position[2] + half_depth
        ])
        
        # Check if we're landing on top of the cube
        player_feet = new_position[1] - self.player_height
        if (new_position[0] >= cube_min[0] - self.player_radius and 
            new_position[0] <= cube_max[0] + self.player_radius and
            new_position[2] >= cube_min[2] - self.player_radius and 
            new_position[2] <= cube_max[2] + self.player_radius and
            player_feet <= cube_max[1] + 0.1 and 
            player_feet >= cube_max[1] - 0.1):
            
            # We're landing on top of the cube, adjust height
            adjusted_pos = np.copy(new_position)
            adjusted_pos[1] = cube_max[1] + self.player_height
            return adjusted_pos
        
        # Calculate movement direction
        movement = new_position - position
        
        # Try to slide along walls by preserving as much movement as possible
        # First try X movement only
        x_only = np.copy(position)
        x_only[0] = new_position[0]
        
        if not self._check_cube_collision(cube, position, x_only):
            return x_only
        
        # Then try Z movement only
        z_only = np.copy(position)
        z_only[2] = new_position[2]
        
        if not self._check_cube_collision(cube, position, z_only):
            return z_only
        
        # If both fail, stay at current position
        return position
    
    def _resolve_rectangle_collision(self, rect, position, new_position):
        """Resolve collision with a rectangle by adjusting the new position."""
        # Get rectangle dimensions
        half_width = rect.width / 2
        half_depth = rect.depth / 2
        
        # Rectangle boundaries (min and max points)
        rect_min = np.array([
            rect.position[0] - half_width,
            rect.position[1],  # Bottom of rectangle
            rect.position[2] - half_depth
        ])
        
        rect_max = np.array([
            rect.position[0] + half_width,
            rect.position[1] + rect.height,  # Top of rectangle
            rect.position[2] + half_depth
        ])
        
        # Check if we're landing on top of the rectangle
        player_feet = new_position[1] - self.player_height
        if (new_position[0] >= rect_min[0] - self.player_radius and 
            new_position[0] <= rect_max[0] + self.player_radius and
            new_position[2] >= rect_min[2] - self.player_radius and 
            new_position[2] <= rect_max[2] + self.player_radius and
            player_feet <= rect_max[1] + 0.1 and 
            player_feet >= rect_max[1] - 0.1):
            
            # We're landing on top of the rectangle, adjust height
            adjusted_pos = np.copy(new_position)
            adjusted_pos[1] = rect_max[1] + self.player_height
            return adjusted_pos
        
        # If we're colliding with the sides, try to slide along walls
        # First try X movement only
        x_only = np.copy(position)
        x_only[0] = new_position[0]
        
        if not self._check_rectangle_collision(rect, position, x_only):
            return x_only
        
        # Then try Z movement only
        z_only = np.copy(position)
        z_only[2] = new_position[2]
        
        if not self._check_rectangle_collision(rect, position, z_only):
            return z_only
        
        # If both fail, stay at current position
        return position
    
    def check_ground(self, position):
        """Check if the player is on the ground."""
        # Cast a ray downward to check for ground
        ray_start = np.copy(position)
        ray_end = np.copy(position)
        ray_end[1] -= self.ground_check_distance
        
        # Check if ray intersects with any object
        for obj in self.world.get_objects():
            if isinstance(obj, Plane):
                # For ground plane, check if we're at the right height
                if obj.position[1] == 0 and abs(position[1] - self.player_height) < self.ground_collision_threshold:
                    self._standing_on_object = obj
                    self._standing_height = 0.0
                    return True
            elif isinstance(obj, Cube) or isinstance(obj, Rectangle):
                # Check if we're standing on top of the object
                if self._check_standing_on_object(obj, position):
                    # Store the object we're standing on
                    self._standing_on_object = obj
                    
                    # Store the height of the object
                    if isinstance(obj, Cube):
                        self._standing_height = obj.position[1] + obj.height/2
                    elif isinstance(obj, Rectangle):
                        self._standing_height = obj.position[1] + obj.height
                    
                    # Only print debug message occasionally to reduce spam
                    current_time = time.time()
                    if self.debug and current_time - self.last_debug_time > 1.0 and not self._on_ground_last_check:
                        self.last_debug_time = current_time
                        print(f"Ground check: Standing on object at height {self._standing_height}")
                    
                    self._on_ground_last_check = True
                    return True
        
        # If we reach here, we're not on the ground
        if self.debug and time.time() - self.last_debug_time > 1.0 and self._on_ground_last_check:
            self.last_debug_time = time.time()
            print("Ground check: Not on ground")
        
        self._on_ground_last_check = False
        return False
    
    def _check_standing_on_object(self, obj, position):
        """Check if the player is standing on top of an object."""
        player_feet = position[1] - self.player_height
        
        if isinstance(obj, Cube):
            # Get cube dimensions
            half_width = obj.width / 2
            half_depth = obj.depth / 2
            top_height = obj.position[1] + obj.height/2
            
            # Check if player is above the cube horizontally
            if (position[0] >= obj.position[0] - half_width - self.player_radius and
                position[0] <= obj.position[0] + half_width + self.player_radius and
                position[2] >= obj.position[2] - half_depth - self.player_radius and
                position[2] <= obj.position[2] + half_depth + self.player_radius):
                
                # Check if player's feet are at the right height
                # Use a larger threshold for standing detection to prevent falling through
                if abs(player_feet - top_height) < self.ground_collision_threshold * 4:
                    return True
        
        elif isinstance(obj, Rectangle):
            # Get rectangle dimensions
            half_width = obj.width / 2
            half_depth = obj.depth / 2
            top_height = obj.position[1] + obj.height
            
            # Check if player is above the rectangle horizontally
            if (position[0] >= obj.position[0] - half_width - self.player_radius and
                position[0] <= obj.position[0] + half_width + self.player_radius and
                position[2] >= obj.position[2] - half_depth - self.player_radius and
                position[2] <= obj.position[2] + half_depth + self.player_radius):
                
                # Check if player's feet are at the right height
                # Use a larger threshold for standing detection to prevent falling through
                if abs(player_feet - top_height) < self.ground_collision_threshold * 4:
                    return True
        
        return False
    
    def _check_triangle_collision(self, triangle, position, new_position):
        """Check if player would collide with a triangle when moving from position to new_position."""
        # Get triangle dimensions
        base_half_size = triangle.size / 2
        
        # Triangle boundaries (min and max points)
        # For simplicity, we'll use a bounding box for initial collision detection
        triangle_min = np.array([
            triangle.position[0] - base_half_size,
            triangle.position[1],  # Bottom of triangle
            triangle.position[2] - base_half_size
        ])
        
        triangle_max = np.array([
            triangle.position[0] + base_half_size,
            triangle.position[1] + triangle.height,  # Top of triangle
            triangle.position[2] + base_half_size
        ])
        
        # Expand triangle by player radius for collision detection
        triangle_min[0] -= self.player_radius
        triangle_min[2] -= self.player_radius
        triangle_max[0] += self.player_radius
        triangle_max[2] += self.player_radius
        
        # Check if new position would be inside the expanded bounding box
        # We only check X and Z for horizontal movement
        horizontal_collision = (
            new_position[0] >= triangle_min[0] and new_position[0] <= triangle_max[0] and
            new_position[2] >= triangle_min[2] and new_position[2] <= triangle_max[2]
        )
        
        # Check vertical collision only if we're within the horizontal bounds
        vertical_collision = False
        if horizontal_collision:
            player_feet = new_position[1] - self.player_height
            player_head = new_position[1]
            
            # Check if player's feet or head would be inside the triangle's height range
            vertical_collision = (
                (player_feet <= triangle_max[1] and player_feet >= triangle_min[1]) or
                (player_head <= triangle_max[1] and player_head >= triangle_min[1]) or
                (player_feet <= triangle_min[1] and player_head >= triangle_max[1])
            )
            
            # If we're within the bounding box, we need to do a more precise check
            # for the triangular shape, but only if we're not clearly above the triangle
            if vertical_collision:
                # For simplicity, we'll just check if we're above the apex of the triangle
                # If we're above the apex, we're definitely not colliding
                if player_feet > triangle.position[1] + triangle.height:
                    vertical_collision = False
            
            # Check if we're landing on top of the triangle
            if not vertical_collision and player_feet <= triangle_max[1] + 0.1 and player_feet >= triangle_max[1] - 0.1:
                # We're very close to the top of the triangle, consider it a landing
                if self.debug and time.time() - self.last_debug_time > 1.0:
                    self.last_debug_time = time.time()
                    print(f"Landing on triangle! Player feet: {player_feet}, Triangle top: {triangle_max[1]}")
                vertical_collision = True
        
        return horizontal_collision and vertical_collision
    
    def _resolve_triangle_collision(self, triangle, position, new_position):
        """Resolve collision with a triangle by adjusting the new position."""
        # If we're already colliding at the current position, allow some movement
        if self._check_triangle_collision(triangle, position, position):
            # Calculate direction away from triangle center
            direction = position - np.array(triangle.position)
            direction[1] = 0  # Only consider horizontal direction
            
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                
                # Move slightly away from triangle
                return position + direction * 0.1
            else:
                # If we're exactly at the center, move in any direction
                return position + np.array([0.1, 0, 0])
        
        # Get triangle dimensions
        base_half_size = triangle.size / 2
        
        # Triangle boundaries (min and max points)
        triangle_min = np.array([
            triangle.position[0] - base_half_size,
            triangle.position[1],  # Bottom of triangle
            triangle.position[2] - base_half_size
        ])
        
        triangle_max = np.array([
            triangle.position[0] + base_half_size,
            triangle.position[1] + triangle.height,  # Top of triangle
            triangle.position[2] + base_half_size
        ])
        
        # Calculate player dimensions
        player_feet = new_position[1] - self.player_height
        player_head = new_position[1]
        
        # Adjusted position starts as the new position
        adjusted_position = np.copy(new_position)
        
        # Check if we're colliding with the top of the triangle
        if (player_feet <= triangle_max[1] + 0.1 and player_feet >= triangle_max[1] - 0.1 and
            adjusted_position[0] >= triangle_min[0] and adjusted_position[0] <= triangle_max[0] and
            adjusted_position[2] >= triangle_min[2] and adjusted_position[2] <= triangle_max[2]):
            # We're landing on top of the triangle, adjust height
            adjusted_position[1] = triangle_max[1] + self.player_height
            return adjusted_position
        
        # Check if we're colliding with the sides of the triangle
        # For simplicity, we'll just push the player out horizontally
        if (player_feet <= triangle_max[1] and player_head >= triangle_min[1] and
            adjusted_position[0] >= triangle_min[0] and adjusted_position[0] <= triangle_max[0] and
            adjusted_position[2] >= triangle_min[2] and adjusted_position[2] <= triangle_max[2]):
            
            # Calculate direction from triangle center to player (horizontal only)
            direction = np.array([adjusted_position[0] - triangle.position[0], 0, adjusted_position[2] - triangle.position[2]])
            
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                
                # Push player out horizontally
                adjusted_position[0] = triangle.position[0] + direction[0] * (base_half_size + self.player_radius + 0.1)
                adjusted_position[2] = triangle.position[2] + direction[2] * (base_half_size + self.player_radius + 0.1)
            
        return adjusted_position 