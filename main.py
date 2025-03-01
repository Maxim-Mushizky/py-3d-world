import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import sys
from engine.renderer import Renderer
from engine.camera import Camera
from engine.shapes import Rectangle
from engine.world import World
from engine.collision import CollisionDetector
from engine.physics import PhysicsEngine

def main():
    # Initialize pygame
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Game Engine")
    
    # Set up OpenGL
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Create world, camera, and renderer
    world = World()
    collision_detector = CollisionDetector(world)
    physics_engine = PhysicsEngine(collision_detector)
    camera = Camera(physics_engine)
    renderer = Renderer(world)
    
    # Game loop variables
    clock = pygame.time.Clock()
    running = True
    
    # Lock mouse to center of screen
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    # Debug flag
    debug = True
    last_debug_time = 0
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F3:
                    # Toggle debug mode
                    debug = not debug
                    print(f"Debug mode: {'ON' if debug else 'OFF'}")
        
        # Update camera (handles input and movement)
        camera.update()
        
        # Debug output
        current_time = pygame.time.get_ticks() / 1000
        if debug and current_time - last_debug_time > 1.0:
            last_debug_time = current_time
            print(f"Camera position: {camera.position}")
            print(f"FPS: {clock.get_fps():.1f}")
        
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render the scene
        renderer.render(camera)
        
        # Swap the buffers
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 