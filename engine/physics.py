import numpy as np
import time
from engine.shapes import InteractiveCube, InteractiveTriangle

class PhysicsEngine:
    def __init__(self, collision_detector):
        self.collision_detector = collision_detector
        
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
            self.jump_cooldown = 0.0
        
        # CRITICAL FIX: If we're at ground level and have been jumping for a while, land
        if self.jumping and abs(position[1] - self.default_eye_height) < 0.1 and time_since_jump > 0.5:
            if self.debug:
                print(f"DEBUG: Landing at ground level after {time_since_jump:.2f} seconds in air")
            self.jumping = False
            self.on_ground = True
            self.velocity[1] = 0
            self.jump_cooldown = 0.0
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
                self.jump_cooldown = 0.0
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
            self.jump_cooldown = 0.0
            
            if self.debug:
                print(f"DEBUG: Forced landing at ground level after {time_since_jump:.2f}s in air")
        
        # Log position changes for debugging
        if self.debug and abs(adjusted_position[1] - prev_position[1]) > 0.01:
            print(f"DEBUG: Height changed from {prev_position[1]:.2f} to {adjusted_position[1]:.2f}, delta: {adjusted_position[1] - prev_position[1]:.2f}")
            if self.jumping:
                print(f"Camera position during jump: {adjusted_position}, Physics jumping: {self.jumping}")
        
        # Update all interactive objects
        self.update_interactive_objects(dt)
        
        return adjusted_position
    
    def set_interactive_objects(self, objects):
        """Set the list of interactive objects to track"""
        self.interactive_objects = [obj for obj in objects if isinstance(obj, (InteractiveCube, InteractiveTriangle))]
        if self.debug:
            print(f"DEBUG: Tracking {len(self.interactive_objects)} interactive objects")
    
    def handle_interactive_object_collisions(self, position, new_position, movement_dir, dt):
        """Handle collisions with interactive objects and apply forces"""
        # Only process if we have interactive objects and are moving
        if not self.interactive_objects or np.array_equal(position, new_position):
            return
        
        # Calculate movement direction and speed
        movement_vector = new_position - position
        movement_speed = np.linalg.norm(movement_vector)
        
        if movement_speed > 0:
            normalized_dir = movement_vector / movement_speed
        else:
            normalized_dir = np.array([0.0, 0.0, 0.0])
        
        # Check each interactive object for collision
        for obj in self.interactive_objects:
            if not obj.is_movable:
                continue
                
            # Calculate distance from player to object center
            obj_pos = np.array(obj.position)
            distance_vector = obj_pos - position
            
            # Only consider horizontal distance for pushing
            distance_vector[1] = 0
            distance = np.linalg.norm(distance_vector)
            
            # Check if we're close enough to interact (player radius + object size)
            player_radius = self.collision_detector.player_radius
            obj_radius = self._get_object_radius(obj)
            interaction_distance = player_radius + obj_radius + 0.1  # Small buffer
            
            if distance <= interaction_distance:
                # We're colliding with this object
                if self.debug and time.time() - self.last_debug_time > 0.5:
                    print(f"DEBUG: Colliding with interactive object at {obj_pos}")
                
                # Calculate push direction (from player to object)
                if np.linalg.norm(distance_vector) > 0:
                    push_dir = distance_vector / np.linalg.norm(distance_vector)
                else:
                    # If we're exactly at the center, use movement direction
                    push_dir = normalized_dir if np.linalg.norm(normalized_dir) > 0 else np.array([1.0, 0.0, 0.0])
                
                # Calculate push force based on player's movement speed and direction
                # Only apply force in the direction of player movement
                movement_alignment = np.dot(normalized_dir, push_dir)
                
                # If we're moving toward the object, apply force
                if movement_alignment > 0:
                    # Calculate force magnitude based on player mass, speed, and alignment
                    force_magnitude = self.player_push_strength * movement_speed * movement_alignment
                    
                    # Create force vector (only horizontal components)
                    force = push_dir * force_magnitude
                    force[1] = 0  # No vertical force from pushing
                    
                    # Apply the force to the object
                    obj.apply_force(force)
                    
                    if self.debug and time.time() - self.last_debug_time > 0.5:
                        print(f"DEBUG: Applied force {force} to object, speed: {movement_speed:.2f}, alignment: {movement_alignment:.2f}")
    
    def update_interactive_objects(self, dt):
        """Update all interactive objects"""
        for obj in self.interactive_objects:
            # Update object physics
            obj.update(dt)
            
            # Check for collisions with other objects
            self.handle_object_object_collisions(obj)
            
            # Check for collisions with the ground
            self.handle_object_ground_collision(obj)
    
    def handle_object_object_collisions(self, obj):
        """Handle collisions between interactive objects"""
        for other_obj in self.interactive_objects:
            if obj is other_obj:
                continue
                
            # Calculate distance between objects
            distance_vector = np.array(other_obj.position) - np.array(obj.position)
            distance = np.linalg.norm(distance_vector)
            
            # Calculate minimum distance for collision based on object types
            obj_radius = self._get_object_radius(obj)
            other_radius = self._get_object_radius(other_obj)
            min_distance = obj_radius + other_radius
            
            # Check for collision
            if distance < min_distance:
                # Objects are colliding, resolve collision
                if distance > 0:
                    # Calculate collision normal
                    collision_normal = distance_vector / distance
                else:
                    # If objects are at the same position, use a default normal
                    collision_normal = np.array([1.0, 0.0, 0.0])
                
                # Calculate overlap
                overlap = min_distance - distance
                
                # Move objects apart based on their masses
                total_mass = obj.mass + other_obj.mass
                if total_mass > 0:
                    # Move proportionally to mass
                    if obj.is_movable:
                        obj.position -= collision_normal * overlap * (other_obj.mass / total_mass)
                        obj.update_vertices()
                    
                    if other_obj.is_movable:
                        other_obj.position += collision_normal * overlap * (obj.mass / total_mass)
                        other_obj.update_vertices()
                
                # Exchange momentum (simplified elastic collision)
                if obj.is_movable and other_obj.is_movable:
                    # Calculate velocity along collision normal
                    v1 = np.dot(obj.velocity, collision_normal)
                    v2 = np.dot(other_obj.velocity, collision_normal)
                    
                    # Calculate new velocities (conservation of momentum and energy)
                    new_v1 = ((obj.mass - other_obj.mass) * v1 + 2 * other_obj.mass * v2) / total_mass
                    new_v2 = ((other_obj.mass - obj.mass) * v2 + 2 * obj.mass * v1) / total_mass
                    
                    # Apply new velocities along collision normal
                    obj.velocity += collision_normal * (new_v1 - v1)
                    other_obj.velocity += collision_normal * (new_v2 - v2)
    
    def _get_object_radius(self, obj):
        """Get the collision radius of an object based on its type"""
        from engine.shapes import InteractiveCube, InteractiveTriangle
        
        if isinstance(obj, InteractiveCube):
            # For cubes, use half the maximum of width and depth
            return max(obj.width, obj.depth) / 2
        elif isinstance(obj, InteractiveTriangle):
            # For triangles, use half the base size
            return obj.size / 2
        else:
            # Default fallback
            return 0.5
    
    def handle_object_ground_collision(self, obj):
        """Handle collisions between objects and the ground"""
        from engine.shapes import InteractiveCube, InteractiveTriangle
        
        # Check if object is below ground level
        if isinstance(obj, InteractiveCube):
            obj_bottom = obj.position[1] - obj.height / 2
        elif isinstance(obj, InteractiveTriangle):
            obj_bottom = obj.position[1]  # Triangle base is at position[1]
        else:
            obj_bottom = obj.position[1] - 0.5  # Default fallback
        
        if obj_bottom < 0:
            # Object is below ground, move it up
            if isinstance(obj, InteractiveCube):
                obj.position[1] = obj.height / 2
            elif isinstance(obj, InteractiveTriangle):
                obj.position[1] = 0  # Set base at ground level
            else:
                obj.position[1] = 0.5  # Default fallback
                
            obj.update_vertices()
            
            # Stop vertical movement and apply friction to horizontal movement
            obj.velocity[1] = 0
            
            # Apply ground friction to horizontal velocity
            ground_friction = 0.5  # Higher friction on ground
            horizontal_velocity = np.array([obj.velocity[0], 0, obj.velocity[2]])
            
            if np.linalg.norm(horizontal_velocity) > 0:
                friction_force = -ground_friction * horizontal_velocity
                obj.velocity[0] += friction_force[0]
                obj.velocity[2] += friction_force[2]
                
                # Stop if moving very slowly
                if np.linalg.norm(horizontal_velocity) < 0.05:
                    obj.velocity[0] = 0
                    obj.velocity[2] = 0 