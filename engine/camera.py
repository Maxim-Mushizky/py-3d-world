import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from pygame.locals import *

class Camera:
    def __init__(self, physics_engine):
        # Camera position and orientation
        self.position = np.array([0.0, 1.7, 5.0])  # Start at eye level (1.7m)
        self.target = np.array([0.0, 1.7, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        
        # Camera parameters
        self.eye_height = 1.7  # Height of camera when standing
        self.crouch_height = 1.0  # Height of camera when crouching
        self.current_height = self.eye_height
        
        # Movement parameters
        self.speed = 5.0  # Movement speed in units per second
        self.sprint_multiplier = 1.5  # Speed multiplier when sprinting
        self.crouch_multiplier = 0.5  # Speed multiplier when crouching
        self.mouse_sensitivity = 0.2
        
        # Camera orientation angles
        self.yaw = -90.0  # Horizontal rotation (around Y axis)
        self.pitch = 0.0  # Vertical rotation (around X axis)
        self.pitch_limit = 89.0  # Maximum pitch angle (up/down)
        
        # Input state
        self.is_crouching = False
        self.is_sprinting = False
        self.space_pressed = False  # Track spacebar state for jump detection
        
        # Physics
        self.physics_engine = physics_engine
        
        # Debug
        self.debug = True
        
        # Platform state
        self.was_on_platform = False
        self.platform_transition = False
    
    def update(self):
        """Update camera position and orientation based on input."""
        # Get keyboard and mouse input
        keys = pygame.key.get_pressed()
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        
        # Update camera orientation based on mouse movement
        self._update_orientation(mouse_dx, mouse_dy)
        
        # Handle crouching
        self._handle_crouch(keys[K_LSHIFT])
        
        # Handle sprinting
        self._handle_sprint(keys[K_LCTRL])
        
        # Calculate movement direction based on keyboard input
        movement_dir = self._calculate_movement_direction(keys)
        
        # Check for jump request (only on initial press)
        current_space_state = keys[K_SPACE]
        jump_requested = current_space_state and not self.space_pressed
        if jump_requested and self.debug:
            print("Jump requested from camera")
        self.space_pressed = current_space_state
        
        # Store the current position
        old_position = np.copy(self.position)
        
        # Check if we were on a platform before
        was_on_platform = self.physics_engine.standing_on_platform
        
        # Apply physics to get new position
        new_position = self.physics_engine.update(self.position, movement_dir, jump_requested)
        
        # Check if we've transitioned to/from a platform
        platform_transition = was_on_platform != self.physics_engine.standing_on_platform
        
        # Always use the physics-calculated position
        self.position = new_position
        
        # Print debug info about jumping
        if self.debug and (jump_requested or self.physics_engine.jumping):
            print(f"Camera position during jump: {self.position}, Physics jumping: {self.physics_engine.jumping}")
        
        # If we just landed on a platform, make sure we use the landing position
        if self.physics_engine.just_landed and self.physics_engine.standing_on_platform:
            if self.physics_engine.landing_position is not None:
                # Use the landing position's height
                self.position[1] = self.physics_engine.landing_position[1]
                if self.debug:
                    print(f"Camera using landing position height: {self.position[1]}")
        
        # Update target based on new position and orientation angles
        self._update_target()
        
        # Print camera position periodically
        if self.debug and pygame.time.get_ticks() % 30 == 0:
            print(f"Camera position: {self.position}")
        
        # Update platform state
        self.was_on_platform = self.physics_engine.standing_on_platform
    
    def _update_orientation(self, mouse_dx, mouse_dy):
        """Update camera orientation based on mouse movement."""
        # Update yaw (left/right rotation)
        self.yaw += mouse_dx * self.mouse_sensitivity
        
        # Update pitch (up/down rotation) with constraints
        self.pitch -= mouse_dy * self.mouse_sensitivity
        
        # Clamp pitch to prevent flipping
        self.pitch = max(-self.pitch_limit, min(self.pitch_limit, self.pitch))
    
    def _update_target(self):
        """Update the target point based on camera position and orientation."""
        # Calculate direction vector from yaw and pitch
        direction = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ])
        
        # Set target to position + direction
        self.target = self.position + direction
    
    def _handle_crouch(self, crouch_key):
        """Handle crouching state and adjust camera height."""
        if crouch_key and not self.is_crouching:
            self.is_crouching = True
            self.current_height = self.crouch_height
        elif not crouch_key and self.is_crouching:
            self.is_crouching = False
            self.current_height = self.eye_height
    
    def _handle_sprint(self, sprint_key):
        """Handle sprinting state."""
        self.is_sprinting = sprint_key
    
    def _calculate_movement_direction(self, keys):
        """Calculate movement direction based on keyboard input."""
        # Calculate forward and right vectors based on yaw (ignoring pitch for movement)
        forward = np.array([
            math.cos(math.radians(self.yaw)),
            0,
            math.sin(math.radians(self.yaw))
        ])
        
        # Calculate right vector
        right = np.cross(forward, np.array([0, 1, 0]))
        
        # Normalize vectors
        forward = forward / np.linalg.norm(forward)
        right = right / np.linalg.norm(right)
        
        # Calculate movement direction
        movement_dir = np.zeros(3)
        
        if keys[K_w]:
            movement_dir += forward
        if keys[K_s]:
            movement_dir -= forward
        if keys[K_d]:
            movement_dir += right
        if keys[K_a]:
            movement_dir -= right
        
        # Normalize movement direction if it's not zero
        if np.linalg.norm(movement_dir) > 0:
            movement_dir = movement_dir / np.linalg.norm(movement_dir)
        
        # Apply speed modifiers
        speed = self.speed
        if self.is_sprinting:
            speed *= self.sprint_multiplier
        if self.is_crouching:
            speed *= self.crouch_multiplier
        
        # Scale by speed
        movement_dir *= speed
        
        return movement_dir
    
    def _get_forward_vector(self):
        """Get the normalized forward vector."""
        forward = self.target - self.position
        return forward / np.linalg.norm(forward)
    
    def _get_right_vector(self):
        """Get the normalized right vector."""
        forward = self._get_forward_vector()
        right = np.cross(forward, self.up)
        return right / np.linalg.norm(right)
    
    def apply(self):
        """Apply the camera transformation to the OpenGL matrix stack."""
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            self.target[0], self.target[1], self.target[2],
            self.up[0], self.up[1], self.up[2]
        )
    
    def get_direction(self):
        """Return the normalized direction vector that the camera is facing."""
        direction = self.target - self.position
        
        # Normalize the direction vector
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm
            
        return direction 