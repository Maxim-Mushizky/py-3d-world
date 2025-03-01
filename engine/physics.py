import numpy as np
import math
import time
from engine.shapes import InteractiveCube, InteractiveTriangle, InteractiveSphere, Plane, Cube, Rectangle

class PhysicsEngine:
    def __init__(self, collision_detector):
        self.collision_detector = collision_detector
        # Store a reference to the world from the collision detector
        self.world = self.collision_detector.world
        
        # Physics parameters
        self.gravity = 9.8  # m/s²
        self.jump_force = 5.0  # Initial upward velocity when jumping
        self.terminal_velocity = 20.0  # Maximum falling speed
        
        # Player state
        self.velocity = np.array([0.0, 0.0, 0.0])  # Current velocity vector
        self.on_ground = True  # Whether the player is on the ground
        self.jumping = False  # Whether the player is currently jumping
        self.jump_cooldown = 0.0  # Time until player can jump again
        
        # Movement smoothing
        self.movement_smoothing = 0.8  # Higher values = more smoothing
        
        # Timing
        self.last_update = time.time()
        
        # Debug
        self.debug = True
        self.last_debug_time = 0
        
        # Ground state
        self.ground_stabilization_timer = 0.0
        self.ground_stabilization_period = 0.5  # Time to stabilize on ground
        
        # Force player to be on ground at start
        self.force_on_ground = True
        
        # Platform state
        self.standing_on_platform = False
        self.platform_height = 0.0
        self.last_platform_height = 0.0
        
        # Last jump time
        self.last_jump_time = 0
        
        # Landing state
        self.just_landed = False
        self.landing_position = None
        
        # Default eye height (ground level)
        self.default_eye_height = 1.7
        
        # Maximum time in air before forced landing
        self.max_air_time = 2.0  # seconds
        
        # Interactive object parameters
        self.player_mass = 70.0  # kg
        self.player_push_strength = 500.0  # Force applied when pushing objects
        self.interactive_objects = []  # List of interactive objects in the world
    
    @property
    def time_since_jump(self):
        """Calculate and return the time since the last jump."""
        return time.time() - self.last_jump_time
    
    def update(self, position, movement_dir, jump_requested):
        """Update physics and return the new position."""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Cap delta time to prevent large jumps after pauses
        dt = min(dt, 0.1)
        
        # Reset landing state
        self.just_landed = False
        self.landing_position = None
        
        # Store previous state
        was_on_ground = self.on_ground
        was_jumping = self.jumping
        was_on_platform = self.standing_on_platform
        prev_position = np.copy(position)
        
        # Calculate time since last jump
        time_since_jump = current_time - self.last_jump_time
        
        # For the first few frames, force the player to be on ground
        if self.force_on_ground:
            self.on_ground = True
            # After 1 second, stop forcing on_ground
            if current_time - self.last_update > 1.0:
                self.force_on_ground = False
        
        # CRITICAL FIX: Force landing if we've been in the air too long and are at ground level
        if self.jumping and time_since_jump > self.max_air_time:
            if self.debug:
                print(f"DEBUG: Forcing landing after {time_since_jump:.2f} seconds in air (max: {self.max_air_time}s)")
            self.jumping = False
            self.on_ground = True
            self.velocity[1] = 0
            self.jump_cooldown = 0.0  # Reset jump cooldown to allow jumping again
        
        # CRITICAL FIX: If we're at ground level and have been jumping for a while, land
        if self.jumping and abs(position[1] - self.default_eye_height) < 0.1 and time_since_jump > 0.5:
            if self.debug:
                print(f"DEBUG: Landing at ground level after {time_since_jump:.2f} seconds in air")
            self.jumping = False
            self.on_ground = True
            self.velocity[1] = 0
            self.jump_cooldown = 0.0  # Reset jump cooldown to allow jumping again
            self.just_landed = True
            self.landing_position = np.copy(position)
        
        # If we're jumping, we're definitely not on the ground
        # until we've been falling for a while and actually hit something
        if self.jumping:
            self.on_ground = False
            if self.debug and current_time - self.last_debug_time > 0.5:
                print(f"DEBUG: In air while jumping, height: {position[1]:.2f}, time since jump: {time_since_jump:.2f}s")
        else:
            # Only check for ground if we're not jumping
            # If we're at the default eye height (1.7) or very close to it, we're on the ground
            if abs(position[1] - self.default_eye_height) < 0.1:
                self.on_ground = True
                self.standing_on_platform = False
                self.platform_height = 0.0
                if self.debug and current_time - self.last_debug_time > 0.5:
                    print(f"DEBUG: On ground at default eye height ({position[1]:.2f})")
            else:
                # Otherwise, check if we're standing on an object using the collision detector
                ground_check_result = self.collision_detector.check_ground(position)
                self.on_ground = ground_check_result
                
                # Check if we're standing on a platform
                self.standing_on_platform = self.collision_detector._standing_on_object is not None and hasattr(self.collision_detector._standing_on_object, 'position')
                
                # Get the platform height from the collision detector
                if self.standing_on_platform:
                    self.last_platform_height = self.platform_height
                    self.platform_height = self.collision_detector._standing_height
                    if self.debug and current_time - self.last_debug_time > 0.5:
                        print(f"DEBUG: Standing on platform at height {self.platform_height:.2f}")
        
        # CRITICAL FIX: Only consider landing if we were jumping, have negative velocity,
        # and have been in the air for a significant amount of time
        if not was_on_ground and self.on_ground and was_jumping:
            if time_since_jump > 0.5 and self.velocity[1] <= 0:
                self.jumping = False
                self.jump_cooldown = 0.0  # Reset jump cooldown to allow jumping again
                self.just_landed = True
                self.landing_position = np.copy(position)
                
                if self.debug:
                    print(f"DEBUG: Actually landed at position {position[1]:.2f} after {time_since_jump:.2f} seconds in air")
            else:
                # Force still in air if we haven't been jumping long enough
                self.on_ground = False
                if self.debug:
                    print(f"DEBUG: Prevented false landing detection, only {time_since_jump:.2f} seconds since jump")
        
        # Update stabilization timer
        if self.ground_stabilization_timer > 0:
            self.ground_stabilization_timer -= dt
        
        # ENHANCED DEBUG OUTPUT (every 0.5 seconds to avoid spam)
        if self.debug and current_time - self.last_debug_time > 0.5:
            self.last_debug_time = current_time
            print(f"===== PHYSICS DEBUG =====")
            print(f"Position: {position}, Height: {position[1]:.2f}")
            print(f"State: on_ground={self.on_ground}, jumping={self.jumping}, on_platform={self.standing_on_platform}")
            print(f"Velocity: {self.velocity}, Y-velocity: {self.velocity[1]:.2f}")
            print(f"Jump requested: {jump_requested}, Jump cooldown: {self.jump_cooldown:.2f}")
            print(f"Time since last jump: {time_since_jump:.2f}s")
            if self.standing_on_platform:
                print(f"Platform height: {self.platform_height:.2f}")
            print(f"========================")
        
        # FIXED JUMP HANDLING
        if jump_requested and self.on_ground and self.jump_cooldown <= 0:
            self.velocity[1] = self.jump_force
            self.jumping = True
            self.on_ground = False  # Immediately set not on ground when jumping
            self.jump_cooldown = 0.3  # Cooldown to prevent repeated jumps
            self.last_jump_time = current_time
            
            if self.debug:
                print(f"DEBUG: JUMP INITIATED! Velocity set to {self.velocity[1]:.2f}")
                if self.standing_on_platform:
                    print(f"DEBUG: Jumping from platform at height {self.platform_height:.2f}")
        elif jump_requested:
            if self.jump_cooldown > 0:
                if self.debug:
                    print(f"DEBUG: Jump requested but on cooldown: {self.jump_cooldown:.2f}")
            elif not self.on_ground:
                if self.debug:
                    print(f"DEBUG: Jump requested but not on ground! Height: {position[1]:.2f}")
        
        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        
        # Apply horizontal movement with smoothing
        self.velocity[0] = self.velocity[0] * self.movement_smoothing + movement_dir[0] * (1 - self.movement_smoothing)
        self.velocity[2] = self.velocity[2] * self.movement_smoothing + movement_dir[2] * (1 - self.movement_smoothing)
        
        # FIXED GRAVITY APPLICATION
        # Apply gravity when not on ground or when jumping
        if not self.on_ground or self.jumping:
            # Apply gravity
            self.velocity[1] -= self.gravity * dt
            
            # Cap falling speed
            if self.velocity[1] < -self.terminal_velocity:
                self.velocity[1] = -self.terminal_velocity
                
            if self.debug and current_time - self.last_debug_time > 0.5:
                print(f"DEBUG: Applying gravity, velocity Y = {self.velocity[1]:.2f}")
        else:
            # Reset vertical velocity when on ground
            self.velocity[1] = 0
            if self.debug and current_time - self.last_debug_time > 0.5:
                print(f"DEBUG: On ground, resetting vertical velocity")
        
        # Calculate new position based on velocity
        new_position = np.copy(position)
        
        # Apply velocity to position
        new_position += self.velocity * dt
        
        # Check for collisions with interactive objects and apply forces
        self.handle_interactive_object_collisions(position, new_position, movement_dir, dt)
        
        # Check for collisions and adjust position
        adjusted_position = self.collision_detector.check_collision(position, new_position)
        
        # If we hit something, reset the corresponding velocity component
        if not np.array_equal(new_position, adjusted_position):
            # Check which components were adjusted
            for i in range(3):
                if new_position[i] != adjusted_position[i]:
                    self.velocity[i] = 0
            
            # If we hit the ground, reset jumping state
            if adjusted_position[1] != new_position[1] and new_position[1] < adjusted_position[1]:
                # Only consider it landing if we were actually falling AND in the air for a while
                if self.velocity[1] < 0 and time_since_jump > 0.5:
                    self.on_ground = True
                    self.jumping = False
                    self.jump_cooldown = 0.0  # Reset jump cooldown when landing
                    self.just_landed = True
                    self.landing_position = np.copy(adjusted_position)
                    
                    if self.debug:
                        print(f"DEBUG: Collision detected! Landing at height {adjusted_position[1]:.2f}")
                else:
                    if self.debug:
                        print(f"DEBUG: Collision detected but ignoring landing (time in air: {time_since_jump:.2f}s)")
        
        # CRITICAL FIX: Ensure we stay in the air for a minimum time after jumping
        # This is the most important fix to prevent false landing detection
        if time_since_jump < 0.5 and self.jumping:
            # Force not on ground for at least 0.5 seconds after jumping
            self.on_ground = False
            if self.debug and current_time - self.last_debug_time > 0.5:
                print(f"DEBUG: Forcing in-air state for {0.5 - time_since_jump:.2f} more seconds")
        
        # CRITICAL FIX: If we're significantly above the default eye height and not on a platform,
        # we can't be on the ground
        if position[1] > self.default_eye_height + 0.5 and not self.standing_on_platform:
            if self.on_ground:
                if self.debug:
                    print(f"DEBUG: Correcting ground detection - we're at height {position[1]:.2f} which is too high to be on ground")
                self.on_ground = False
        
        # CRITICAL FIX: If we're at ground level and have been in the air for a while, force landing
        if abs(adjusted_position[1] - self.default_eye_height) < 0.05 and time_since_jump > 0.5 and self.jumping:
            self.jumping = False
            self.on_ground = True
            self.velocity[1] = 0
            self.jump_cooldown = 0.0  # Reset jump cooldown to allow jumping again
            
            if self.debug:
                print(f"DEBUG: Forced landing at ground level after {time_since_jump:.2f}s in air")
        
        # Log position changes for debugging
        if self.debug and abs(adjusted_position[1] - prev_position[1]) > 0.01:
            print(f"DEBUG: Height changed from {prev_position[1]:.2f} to {adjusted_position[1]:.2f}, delta: {adjusted_position[1] - prev_position[1]:.2f}")
            if self.jumping:
                print(f"Camera position during jump: {adjusted_position}, Physics jumping: {self.jumping}")
        
        # Update all interactive objects
        self.update_interactive_objects(dt, position, movement_dir)
        
        return adjusted_position
    
    def set_interactive_objects(self, objects):
        """Set the list of interactive objects to track"""
        self.interactive_objects = [obj for obj in objects if isinstance(obj, (InteractiveCube, InteractiveTriangle, InteractiveSphere))]
        if self.debug:
            print(f"DEBUG: Tracking {len(self.interactive_objects)} interactive objects")
    
    def handle_interactive_object_collisions(self, position, new_position, movement_dir, dt):
        """Handle collisions with interactive objects and apply forces."""
        # Skip if no interactive objects
        if not self.interactive_objects:
            return
        
        # Calculate movement vector
        movement_vector = new_position - position
        
        # Skip if not moving
        if np.linalg.norm(movement_vector) < 0.001:
            return
        
        # Normalize movement vector
        if np.linalg.norm(movement_vector) > 0:
            movement_vector = movement_vector / np.linalg.norm(movement_vector)
        
        # Check each interactive object
        for obj in self.interactive_objects:
            # Calculate distance to object
            obj_pos = np.array(obj.position)
            distance_vector = obj_pos - new_position
            
            # Only consider horizontal distance for collision
            distance_vector[1] = 0
            distance = np.linalg.norm(distance_vector)
            
            # Check if we're close enough to interact
            interaction_radius = 2.0  # Distance at which player can push objects
            
            if distance < interaction_radius:
                # Calculate push direction (from player to object)
                if np.linalg.norm(distance_vector) > 0:
                    push_dir = distance_vector / np.linalg.norm(distance_vector)
                else:
                    push_dir = np.array([1.0, 0.0, 0.0])  # Default direction if directly on top
                
                # Calculate dot product to see if we're moving toward the object
                dot_product = np.dot(movement_vector, push_dir)
                
                # Only push if moving toward the object
                if dot_product > 0.3:  # Threshold to determine if we're moving toward the object
                    # Calculate push force based on movement speed and player strength
                    push_strength = self.player_push_strength * dot_product
                    
                    # Scale force based on mass ratio (heavier objects are harder to push)
                    mass_factor = min(1.0, self.player_mass / obj.mass)
                    push_strength *= mass_factor
                    
                    # Apply force to object
                    force = push_dir * push_strength
                    
                    # Only apply horizontal force (no vertical pushing)
                    force[1] = 0
                    
                    # Apply the force to the object
                    obj.apply_force(force)
                    
                    # Debug output
                    if self.debug and np.linalg.norm(force) > 100:
                        print(f"DEBUG: Applied force {np.linalg.norm(force):.1f} to object at {obj.position}")
                    
                    # Update the object's physics
                    obj.update(dt)
                    
                    # Check for collisions between this object and other objects
                    self._handle_object_object_collisions(obj, dt)
    
    def _handle_object_object_collisions(self, obj, dt):
        """Handle collisions between interactive objects."""
        # Skip if no interactive objects
        if not self.interactive_objects:
            return
        
        # Get object position and size
        obj_pos = np.array(obj.position)
        
        # For cubes, use width/height/depth
        if isinstance(obj, InteractiveCube):
            obj_size = np.array([obj.width, obj.height, obj.depth])
        # For triangles, use size as an approximation
        elif isinstance(obj, InteractiveTriangle):
            obj_size = np.array([obj.size, obj.height, obj.size])
        else:
            return  # Unsupported object type
        
        # Check collision with each other interactive object
        for other_obj in self.interactive_objects:
            # Skip self
            if other_obj is obj:
                continue
            
            # Get other object position and size
            other_pos = np.array(other_obj.position)
            
            # For cubes, use width/height/depth
            if isinstance(other_obj, InteractiveCube):
                other_size = np.array([other_obj.width, other_obj.height, other_obj.depth])
            # For triangles, use size as an approximation
            elif isinstance(other_obj, InteractiveTriangle):
                other_size = np.array([other_obj.size, other_obj.height, other_obj.size])
            else:
                continue  # Unsupported object type
            
            # Calculate distance between objects
            distance_vector = other_pos - obj_pos
            
            # Calculate collision bounds (half sizes)
            obj_half_size = obj_size / 2
            other_half_size = other_size / 2
            
            # Check for collision in each dimension
            collision_x = abs(distance_vector[0]) < (obj_half_size[0] + other_half_size[0])
            collision_y = abs(distance_vector[1]) < (obj_half_size[1] + other_half_size[1])
            collision_z = abs(distance_vector[2]) < (obj_half_size[2] + other_half_size[2])
            
            # If collision in all dimensions, objects are colliding
            if collision_x and collision_y and collision_z:
                # Calculate collision normal (direction from obj to other_obj)
                if np.linalg.norm(distance_vector) > 0:
                    collision_normal = distance_vector / np.linalg.norm(distance_vector)
                else:
                    collision_normal = np.array([1.0, 0.0, 0.0])  # Default if objects are at same position
                
                # Calculate overlap in each dimension
                overlap_x = (obj_half_size[0] + other_half_size[0]) - abs(distance_vector[0])
                overlap_y = (obj_half_size[1] + other_half_size[1]) - abs(distance_vector[1])
                overlap_z = (obj_half_size[2] + other_half_size[2]) - abs(distance_vector[2])
                
                # Find minimum overlap dimension
                min_overlap = min(overlap_x, overlap_y, overlap_z)
                
                # Resolve collision by moving objects apart
                if min_overlap == overlap_x:
                    # X-axis collision
                    separation_vector = np.array([collision_normal[0] * overlap_x, 0, 0])
                elif min_overlap == overlap_y:
                    # Y-axis collision
                    separation_vector = np.array([0, collision_normal[1] * overlap_y, 0])
                else:
                    # Z-axis collision
                    separation_vector = np.array([0, 0, collision_normal[2] * overlap_z])
                
                # Calculate mass ratio for collision response
                total_mass = obj.mass + other_obj.mass
                obj_mass_ratio = other_obj.mass / total_mass
                other_mass_ratio = obj.mass / total_mass
                
                # Move objects apart based on mass ratio
                if obj.is_movable:
                    obj.position -= separation_vector * obj_mass_ratio
                    obj.update_vertices()
                
                if other_obj.is_movable:
                    other_obj.position += separation_vector * other_mass_ratio
                    other_obj.update_vertices()
                
                # Calculate impulse for collision response
                relative_velocity = other_obj.velocity - obj.velocity
                velocity_along_normal = np.dot(relative_velocity, collision_normal)
                
                # Only resolve if objects are moving toward each other
                if velocity_along_normal < 0:
                    # Calculate restitution (bounciness)
                    restitution = 0.3  # Medium bounce
                    
                    # Calculate impulse scalar
                    impulse_scalar = -(1 + restitution) * velocity_along_normal
                    impulse_scalar /= (1 / obj.mass) + (1 / other_obj.mass)
                    
                    # Apply impulse
                    impulse = collision_normal * impulse_scalar
                    
                    if obj.is_movable:
                        obj.velocity -= impulse / obj.mass
                    
                    if other_obj.is_movable:
                        other_obj.velocity += impulse / other_obj.mass
                
                # Debug output
                if self.debug:
                    print(f"DEBUG: Collision between objects at {obj.position} and {other_obj.position}")
    
    def update_interactive_objects(self, dt, player_position=None, player_direction=None):
        """Update all interactive objects in the world."""
        # Use the already stored interactive objects instead of trying to get them from world
        if not hasattr(self, 'interactive_objects') or self.interactive_objects is None:
            self.interactive_objects = []
            return
        
        # Update each object's physics
        for obj in self.interactive_objects:
            # Check if object is below the world (fallen through)
            if obj.position[1] < -10:
                # Reset position to above ground
                obj.position[1] = 5.0
                obj.velocity = np.array([0.0, 0.0, 0.0])
                if self.debug:
                    print(f"DEBUG: Object fell through world, resetting position: {obj.position}")
                continue
            
            # Apply gravity if the object is not on the ground
            on_ground = False
            
            # Check if object is on the ground plane
            if abs(obj.position[1] - (obj.radius if isinstance(obj, InteractiveSphere) else obj.height/2)) < 0.1:
                on_ground = True
                # Stop vertical movement
                obj.velocity[1] = 0
            else:
                # Check for collisions with other objects that might be supporting this object
                # Use the world from the collision detector
                for other_obj in self.world.get_objects():
                    if other_obj is obj:
                        continue
                    
                    # For spheres, check if they're resting on another object
                    if isinstance(obj, InteractiveSphere):
                        # Check if sphere is resting on a plane
                        if isinstance(other_obj, Plane) and other_obj.position[1] == 0:
                            if abs(obj.position[1] - obj.radius) < 0.1:
                                on_ground = True
                                # Ensure sphere doesn't sink into the ground
                                obj.position[1] = obj.radius
                                # Stop vertical movement
                                obj.velocity[1] = 0
                                break
                        
                        # Check if sphere is resting on a cube or rectangle
                        elif isinstance(other_obj, (Cube, Rectangle)):
                            # Calculate top of the supporting object
                            if isinstance(other_obj, Cube):
                                top_height = other_obj.position[1] + other_obj.height/2
                            else:  # Rectangle
                                top_height = other_obj.position[1] + other_obj.height
                            
                            # Calculate horizontal distance to object center
                            horizontal_distance = np.sqrt(
                                (obj.position[0] - other_obj.position[0])**2 + 
                                (obj.position[2] - other_obj.position[2])**2
                            )
                            
                            # Check if sphere is above the object horizontally
                            if isinstance(other_obj, Cube):
                                half_width = other_obj.width/2
                                half_depth = other_obj.depth/2
                                is_above_horizontally = (
                                    abs(obj.position[0] - other_obj.position[0]) <= half_width + obj.radius and
                                    abs(obj.position[2] - other_obj.position[2]) <= half_depth + obj.radius
                                )
                            else:  # Rectangle
                                half_width = other_obj.width/2
                                half_depth = other_obj.depth/2
                                is_above_horizontally = (
                                    abs(obj.position[0] - other_obj.position[0]) <= half_width + obj.radius and
                                    abs(obj.position[2] - other_obj.position[2]) <= half_depth + obj.radius
                                )
                            
                            # Check if sphere is at the right height
                            if is_above_horizontally and abs(obj.position[1] - obj.radius - top_height) < 0.1:
                                on_ground = True
                                # Ensure sphere doesn't sink into the object
                                obj.position[1] = top_height + obj.radius
                                # Stop vertical movement
                                obj.velocity[1] = 0
                                break
            
            if not on_ground:
                obj.apply_force(np.array([0, -self.gravity * obj.mass, 0]))
            
            # Check for collisions with the player
            if player_position is not None and self._check_player_object_collision(player_position, obj):
                # Calculate push direction (from player to object)
                push_dir = obj.position - player_position
                push_dir[1] = 0  # Only push horizontally
                
                # Normalize the direction
                distance = np.linalg.norm(push_dir)
                if distance > 0:
                    push_dir = push_dir / distance
                else:
                    # If player is exactly at object center, use player's direction
                    push_dir = player_direction
                    push_dir[1] = 0  # Only push horizontally
                    push_dir = push_dir / np.linalg.norm(push_dir) if np.linalg.norm(push_dir) > 0 else np.array([1, 0, 0])
                
                # Apply force to the object (stronger if player is moving toward it)
                dot_product = np.dot(player_direction, push_dir)
                force_multiplier = 1.0 + max(0, dot_product)  # More force when moving toward object
                
                # Apply the push force
                push_force = push_dir * self.player_push_strength * force_multiplier
                obj.apply_force(push_force)
                
                if self.debug:
                    print(f"Pushing object with force: {push_force}, dot product: {dot_product:.2f}")
            
            # Update the object's physics
            obj.update(dt)
            
            # Check for collisions with other objects
            for other_obj in self.interactive_objects:
                if obj != other_obj:
                    self._handle_object_object_collision(obj, other_obj)
    
    def _check_player_object_collision(self, player_position, obj):
        """Check if the player is colliding with an interactive object."""
        # For cubes, check if player is within the cube's bounds plus player radius
        if isinstance(obj, InteractiveCube):
            # Calculate the distance from player to cube center
            distance = np.linalg.norm(player_position - obj.position)
            
            # Calculate the maximum distance for collision (half diagonal of cube + player radius)
            half_diagonal = np.sqrt(obj.width**2 + obj.height**2 + obj.depth**2) / 2
            max_distance = half_diagonal + self.collision_detector.player_radius
            
            return distance < max_distance
        
        # For triangles, use a simple radius check (not accurate but simple)
        elif isinstance(obj, InteractiveTriangle):
            # Calculate the distance from player to triangle center
            distance = np.linalg.norm(player_position - obj.position)
            
            # Use the size of the triangle as an approximation
            max_distance = obj.size + self.collision_detector.player_radius
            
            return distance < max_distance
        
        # For spheres, check if player is within the sphere's radius plus player radius
        elif isinstance(obj, InteractiveSphere):
            # Calculate the distance from player to sphere center
            distance = np.linalg.norm(player_position - obj.position)
            
            # Calculate the maximum distance for collision (sphere radius + player radius)
            max_distance = obj.radius + self.collision_detector.player_radius
            
            return distance < max_distance
        
        return False
    
    def _handle_object_object_collision(self, obj1, obj2):
        """Handle collision between two interactive objects."""
        # Calculate vector between object centers
        direction = obj2.position - obj1.position
        
        # Calculate distance between objects
        distance = np.linalg.norm(direction)
        
        # Determine collision threshold based on object types
        collision_threshold = 0
        
        # For cubes, use half the sum of their diagonals
        if isinstance(obj1, InteractiveCube) and isinstance(obj2, InteractiveCube):
            diagonal1 = np.sqrt(obj1.width**2 + obj1.height**2 + obj1.depth**2) / 2
            diagonal2 = np.sqrt(obj2.width**2 + obj2.height**2 + obj2.depth**2) / 2
            collision_threshold = diagonal1 + diagonal2
        
        # For triangles, use their sizes
        elif isinstance(obj1, InteractiveTriangle) and isinstance(obj2, InteractiveTriangle):
            collision_threshold = obj1.size + obj2.size
        
        # For spheres, use their radii
        elif isinstance(obj1, InteractiveSphere) and isinstance(obj2, InteractiveSphere):
            collision_threshold = obj1.radius + obj2.radius
        
        # For mixed types, use a combination
        elif isinstance(obj1, InteractiveCube) and isinstance(obj2, InteractiveTriangle):
            diagonal1 = np.sqrt(obj1.width**2 + obj1.height**2 + obj1.depth**2) / 2
            collision_threshold = diagonal1 + obj2.size
        elif isinstance(obj1, InteractiveTriangle) and isinstance(obj2, InteractiveCube):
            diagonal2 = np.sqrt(obj2.width**2 + obj2.height**2 + obj2.depth**2) / 2
            collision_threshold = obj1.size + diagonal2
        elif isinstance(obj1, InteractiveCube) and isinstance(obj2, InteractiveSphere):
            diagonal1 = np.sqrt(obj1.width**2 + obj1.height**2 + obj1.depth**2) / 2
            collision_threshold = diagonal1 + obj2.radius
        elif isinstance(obj1, InteractiveSphere) and isinstance(obj2, InteractiveCube):
            diagonal2 = np.sqrt(obj2.width**2 + obj2.height**2 + obj2.depth**2) / 2
            collision_threshold = obj1.radius + diagonal2
        elif isinstance(obj1, InteractiveTriangle) and isinstance(obj2, InteractiveSphere):
            collision_threshold = obj1.size + obj2.radius
        elif isinstance(obj1, InteractiveSphere) and isinstance(obj2, InteractiveTriangle):
            collision_threshold = obj1.radius + obj2.size
        
        # Check if objects are colliding
        if distance < collision_threshold:
            # Normalize direction
            if distance > 0:
                direction = direction / distance
            else:
                # If objects are at the same position, use a default direction
                direction = np.array([1, 0, 0])
            
            # Calculate overlap
            overlap = collision_threshold - distance
            
            # Calculate impulse based on masses and velocities
            relative_velocity = obj2.velocity - obj1.velocity
            velocity_along_normal = np.dot(relative_velocity, direction)
            
            # Only resolve if objects are moving toward each other
            if velocity_along_normal < 0:
                # Calculate impulse scalar
                restitution = 0.8  # Bounciness factor (0-1)
                impulse_scalar = -(1 + restitution) * velocity_along_normal
                impulse_scalar /= (1 / obj1.mass) + (1 / obj2.mass)
                
                # Apply impulse
                impulse = direction * impulse_scalar
                
                # Update velocities
                if obj1.is_movable:
                    obj1.velocity -= (impulse / obj1.mass)
                if obj2.is_movable:
                    obj2.velocity += (impulse / obj2.mass)
                
                # Separate objects to prevent sticking
                if obj1.is_movable and obj2.is_movable:
                    # Move both objects
                    separation = direction * overlap * 0.5
                    obj1.position -= separation
                    obj2.position += separation
                elif obj1.is_movable:
                    # Only move obj1
                    obj1.position -= direction * overlap
                elif obj2.is_movable:
                    # Only move obj2
                    obj2.position += direction * overlap 