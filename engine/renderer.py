import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from engine.shapes import Rectangle, Plane, Cube

class Renderer:
    def __init__(self, world):
        self.world = world
        self.setup_lighting()
    
    def setup_lighting(self):
        """Set up basic lighting for the scene."""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up light 0 position and properties
        glLight(GL_LIGHT0, GL_POSITION, (5.0, 10.0, 5.0, 1.0))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLight(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLight(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    
    def render(self, camera):
        """Render the entire scene."""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up the camera view
        glLoadIdentity()
        camera.apply()
        
        # Render all objects in the world
        for obj in self.world.get_objects():
            self._render_object(obj)
    
    def _render_object(self, obj):
        """Render a single object."""
        glPushMatrix()
        
        # Apply object position
        glTranslatef(obj.position[0], obj.position[1], obj.position[2])
        
        # Set default color (in case the object doesn't have a color attribute)
        default_color = (0.7, 0.7, 0.7)  # Light gray
        
        # Try to get the color from the object
        if hasattr(obj, 'color'):
            color = obj.color
        elif hasattr(obj, 'colors') and len(obj.colors) > 0:
            color = obj.colors[0]  # Use the first color
        else:
            color = default_color
        
        # Set object color
        glColor3f(color[0], color[1], color[2])
        
        # Render based on object type
        if obj.__class__.__name__ == 'Cube':
            self._render_cube(obj)
        elif obj.__class__.__name__ == 'Plane':
            self._render_plane(obj)
        elif obj.__class__.__name__ == 'Rectangle':
            self._render_rectangle(obj)
        
        glPopMatrix()
    
    def _render_cube(self, cube):
        """Render a cube object."""
        # Scale to the cube's dimensions
        glScalef(cube.width, cube.height, cube.depth)
        
        # Draw a unit cube
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
    
    def _render_plane(self, plane):
        """Render a plane object."""
        # Draw a large plane
        size = 50.0  # Size of the plane
        
        glBegin(GL_QUADS)
        glNormal3f(0.0, 1.0, 0.0)  # Normal pointing up
        glVertex3f(-size, 0.0, -size)
        glVertex3f(-size, 0.0, size)
        glVertex3f(size, 0.0, size)
        glVertex3f(size, 0.0, -size)
        glEnd()
    
    def _render_rectangle(self, rect):
        """Render a rectangle object."""
        # Scale to the rectangle's dimensions
        glScalef(rect.width, rect.height, rect.depth)
        
        # Draw a unit rectangle
        glBegin(GL_QUADS)
        
        # Top face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-0.5, 0.0, -0.5)
        glVertex3f(-0.5, 0.0, 0.5)
        glVertex3f(0.5, 0.0, 0.5)
        glVertex3f(0.5, 0.0, -0.5)
        
        glEnd()
    
    def render_skybox(self):
        # Save current matrix
        glPushMatrix()
        
        # Disable lighting for skybox
        glDisable(GL_LIGHTING)
        
        # Set clear color to sky blue
        glClearColor(0.5, 0.7, 1.0, 1.0)
        
        # Restore lighting
        glEnable(GL_LIGHTING)
        
        # Restore matrix
        glPopMatrix() 