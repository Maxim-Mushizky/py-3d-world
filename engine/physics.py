import numpy as np
import time

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
        
        return adjusted_position 