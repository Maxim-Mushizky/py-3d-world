import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.shadow import *
from OpenGL.GL.ARB.depth_texture import *
import numpy as np
from engine.shapes import Rectangle, Plane, Cube, Triangle, InteractiveTriangle, InteractiveCube

class Renderer:
    def __init__(self, world):
        self.world = world
        
        # Material properties
        self.materials = {
            'default': {
                'ambient': (0.2, 0.2, 0.2, 1.0),
                'diffuse': (0.8, 0.8, 0.8, 1.0),
                'specular': (0.5, 0.5, 0.5, 1.0),
                'shininess': 50.0
            },
            'metal': {
                'ambient': (0.25, 0.25, 0.25, 1.0),
                'diffuse': (0.4, 0.4, 0.4, 1.0),
                'specular': (0.774597, 0.774597, 0.774597, 1.0),
                'shininess': 76.8
            },
            'plastic': {
                'ambient': (0.0, 0.0, 0.0, 1.0),
                'diffuse': (0.55, 0.55, 0.55, 1.0),
                'specular': (0.7, 0.7, 0.7, 1.0),
                'shininess': 32.0
            }
        }
        
        # Light positions and properties
        self.lights = {
            'main': {
                'position': (5.0, 10.0, 5.0, 1.0),
                'ambient': (0.2, 0.2, 0.2, 1.0),
                'diffuse': (0.8, 0.8, 0.8, 1.0),
                'specular': (1.0, 1.0, 1.0, 1.0)
            },
            'fill': {
                'position': (-8.0, 5.0, -3.0, 1.0),
                'ambient': (0.05, 0.05, 0.05, 1.0),
                'diffuse': (0.3, 0.3, 0.4, 1.0),
                'specular': (0.3, 0.3, 0.4, 1.0)
            }
        }
        
        # Time-based animation for lights
        self.time = 0
        
        # Shadow mapping
        self.shadow_enabled = True
        self.shadow_map_size = 1024  # Size of shadow map texture
        self.shadow_texture = None
        self.shadow_fbo = None
        
        # Initialize OpenGL settings and lighting
        self.setup_opengl()
        self.setup_lighting()
        self.setup_shadow_map()
    
    def setup_opengl(self):
        """Set up OpenGL rendering features."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        
        # Enable smooth shading
        glShadeModel(GL_SMOOTH)
        
        # Enable face culling for better performance
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable normalization of normals
        glEnable(GL_NORMALIZE)
        
        # Set up blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def setup_lighting(self):
        """Set up enhanced lighting for the scene."""
        glEnable(GL_LIGHTING)
        
        # Enable the first light (main light)
        glEnable(GL_LIGHT0)
        light = self.lights['main']
        glLight(GL_LIGHT0, GL_POSITION, light['position'])
        glLight(GL_LIGHT0, GL_AMBIENT, light['ambient'])
        glLight(GL_LIGHT0, GL_DIFFUSE, light['diffuse'])
        glLight(GL_LIGHT0, GL_SPECULAR, light['specular'])
        
        # Enable the second light (fill light)
        glEnable(GL_LIGHT1)
        light = self.lights['fill']
        glLight(GL_LIGHT1, GL_POSITION, light['position'])
        glLight(GL_LIGHT1, GL_AMBIENT, light['ambient'])
        glLight(GL_LIGHT1, GL_DIFFUSE, light['diffuse'])
        glLight(GL_LIGHT1, GL_SPECULAR, light['specular'])
        
        # Set up global ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
        
        # Enable color material for easier color management
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    
    def setup_shadow_map(self):
        """Set up shadow mapping."""
        try:
            # Check if shadow mapping is supported
            if not glInitDepthTextureARB() or not glInitShadowARB():
                print("Shadow mapping not supported, disabling shadows")
                self.shadow_enabled = False
                return
            
            # Create a texture for the shadow map
            self.shadow_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.shadow_texture)
            
            # Set up the shadow texture parameters
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 
                        self.shadow_map_size, self.shadow_map_size, 
                        0, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            # Set up comparison mode for shadow mapping
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE_ARB, GL_COMPARE_R_TO_TEXTURE_ARB)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC_ARB, GL_LEQUAL)
            
            # Create and set up the FBO for shadow mapping
            self.shadow_fbo = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.shadow_texture, 0)
            
            # Disable color buffer for shadow map
            glDrawBuffer(GL_NONE)
            glReadBuffer(GL_NONE)
            
            # Check if FBO is complete
            if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
                print("Framebuffer not complete, disabling shadows")
                self.shadow_enabled = False
            
            # Unbind the FBO
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            
            print("Shadow mapping initialized successfully")
            
        except Exception as e:
            print(f"Error setting up shadow mapping: {e}")
            self.shadow_enabled = False
    
    def update(self, dt):
        """Update time-based effects."""
        self.time += dt
        
        # Animate the fill light position for dynamic lighting
        angle = self.time * 0.2  # Slow rotation
        radius = 10.0
        x = np.sin(angle) * radius
        z = np.cos(angle) * radius
        self.lights['fill']['position'] = (x, 5.0, z, 1.0)
        
        # Update the light position in OpenGL
        glLight(GL_LIGHT1, GL_POSITION, self.lights['fill']['position'])
    
    def render(self, camera):
        """Render the entire scene."""
        if self.shadow_enabled:
            # First pass: Render from light's perspective to create shadow map
            self.render_shadow_map(camera)
        
        # Second pass: Render the scene normally with shadows
        self.render_scene(camera)
    
    def render_shadow_map(self, camera):
        """Render the scene from the light's perspective to create a shadow map."""
        if not self.shadow_enabled:
            return
            
        # Bind the shadow FBO
        glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)
        
        # Set viewport to shadow map size
        glViewport(0, 0, self.shadow_map_size, self.shadow_map_size)
        
        # Clear the depth buffer
        glClear(GL_DEPTH_BUFFER_BIT)
        
        # Disable lighting for shadow map generation
        glDisable(GL_LIGHTING)
        
        # Set up the light's perspective
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Use a perspective projection for the light
        light_pos = self.lights['main']['position']
        gluPerspective(45, 1.0, 1.0, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Position the "camera" at the light's position, looking at the center of the scene
        gluLookAt(
            light_pos[0], light_pos[1], light_pos[2],  # Light position
            0, 0, 0,                                   # Look at center
            0, 1, 0                                    # Up vector
        )
        
        # Save the light's modelview and projection matrices
        self.light_projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        self.light_modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        
        # Render all objects (for shadow map, we only need the depth)
        for obj in self.world.get_objects():
            # Skip rendering the skybox for shadows
            if isinstance(obj, Plane):
                continue
                
            glPushMatrix()
            glTranslatef(obj.position[0], obj.position[1], obj.position[2])
            
            if isinstance(obj, (Cube, InteractiveCube)):
                self._render_cube_shadow(obj)
            elif isinstance(obj, Rectangle):
                self._render_rectangle_shadow(obj)
            elif isinstance(obj, (Triangle, InteractiveTriangle)):
                self._render_triangle_shadow(obj)
                
            glPopMatrix()
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # Unbind the shadow FBO
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # Reset viewport to window size
        display_info = pygame.display.Info()
        glViewport(0, 0, display_info.current_w, display_info.current_h)
        
        # Re-enable lighting
        glEnable(GL_LIGHTING)
    
    def render_scene(self, camera):
        """Render the scene with shadows."""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up the camera view
        glLoadIdentity()
        camera.apply()
        
        # Draw a simple skybox
        self.render_skybox()
        
        if self.shadow_enabled:
            # Set up texture matrix for shadow projection
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.shadow_texture)
            
            # Set up texture coordinate generation
            glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
            glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
            glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
            glTexGeni(GL_Q, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
            
            # Enable texture coordinate generation
            glEnable(GL_TEXTURE_GEN_S)
            glEnable(GL_TEXTURE_GEN_T)
            glEnable(GL_TEXTURE_GEN_R)
            glEnable(GL_TEXTURE_GEN_Q)
            
            # Set up the texture matrix for shadow projection
            bias_matrix = np.array([
                0.5, 0.0, 0.0, 0.5,
                0.0, 0.5, 0.0, 0.5,
                0.0, 0.0, 0.5, 0.5,
                0.0, 0.0, 0.0, 1.0
            ], dtype=np.float32).reshape(4, 4)
            
            glMatrixMode(GL_TEXTURE)
            glLoadIdentity()
            glMultMatrixf(bias_matrix)
            glMultMatrixf(self.light_projection_matrix)
            glMultMatrixf(self.light_modelview_matrix)
            
            # Switch back to modelview matrix
            glMatrixMode(GL_MODELVIEW)
            
            # Enable shadow comparison
            glEnable(GL_TEXTURE_2D)
            
            # Set up alpha test to discard shadow fragments
            glAlphaFunc(GL_GREATER, 0.5)
            glEnable(GL_ALPHA_TEST)
        
        # Render all objects in the world
        for obj in self.world.get_objects():
            self._render_object(obj)
        
        if self.shadow_enabled:
            # Disable shadow mapping
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_TEXTURE_GEN_S)
            glDisable(GL_TEXTURE_GEN_T)
            glDisable(GL_TEXTURE_GEN_R)
            glDisable(GL_TEXTURE_GEN_Q)
            glDisable(GL_ALPHA_TEST)
            
            # Reset texture matrix
            glMatrixMode(GL_TEXTURE)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
        
        # Draw light sources as small spheres for visualization
        self._draw_light_sources()
    
    def _draw_light_sources(self):
        """Draw small spheres at light positions for visualization."""
        # Temporarily disable lighting to draw emissive light sources
        glDisable(GL_LIGHTING)
        
        for name, light in self.lights.items():
            glPushMatrix()
            
            # Position the sphere at the light position
            glTranslatef(light['position'][0], light['position'][1], light['position'][2])
            
            # Set the color to match the light's diffuse color
            glColor3f(light['diffuse'][0], light['diffuse'][1], light['diffuse'][2])
            
            # Draw a small sphere
            sphere = gluNewQuadric()
            gluSphere(sphere, 0.2, 16, 16)
            gluDeleteQuadric(sphere)
            
            glPopMatrix()
        
        # Re-enable lighting
        glEnable(GL_LIGHTING)
    
    def _set_material(self, material_name, color):
        """Set material properties for an object."""
        material = self.materials.get(material_name, self.materials['default'])
        
        # Set ambient and diffuse to the object's color
        ambient = (color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 1.0)
        diffuse = (color[0], color[1], color[2], 1.0)
        
        # Use the material's specular and shininess
        specular = material['specular']
        shininess = material['shininess']
        
        # Apply material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, shininess)
        
        # Set the base color
        glColor3f(color[0], color[1], color[2])
    
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
        
        # Choose material based on object type
        material = 'default'
        if isinstance(obj, (InteractiveCube, InteractiveTriangle)):
            material = 'metal'  # Interactive objects look metallic
        elif isinstance(obj, Plane):
            material = 'plastic'  # Ground looks like plastic
        
        # Set material properties
        self._set_material(material, color)
        
        # Render based on object type
        if isinstance(obj, (Cube, InteractiveCube)):
            self._render_cube(obj)
        elif isinstance(obj, Plane):
            self._render_plane(obj)
        elif isinstance(obj, Rectangle):
            self._render_rectangle(obj)
        elif isinstance(obj, (Triangle, InteractiveTriangle)):
            self._render_triangle(obj)
        
        glPopMatrix()
    
    def _render_cube_shadow(self, cube):
        """Render a cube for the shadow map (depth only)."""
        # Scale to the cube's dimensions
        glScalef(cube.width, cube.height, cube.depth)
        
        # Draw a unit cube
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
    
    def _render_rectangle_shadow(self, rect):
        """Render a rectangle for the shadow map (depth only)."""
        # Scale to the rectangle's dimensions
        glScalef(rect.width, rect.height, rect.depth)
        
        # Draw a unit rectangle
        glBegin(GL_QUADS)
        
        # Top face
        glVertex3f(-0.5, 0.0, -0.5)
        glVertex3f(-0.5, 0.0, 0.5)
        glVertex3f(0.5, 0.0, 0.5)
        glVertex3f(0.5, 0.0, -0.5)
        
        glEnd()
    
    def _render_triangle_shadow(self, triangle):
        """Render a triangle for the shadow map (depth only)."""
        # Draw the triangle using its vertices and faces
        glBegin(GL_TRIANGLES)
        
        # Get the vertices and faces
        vertices = triangle.vertices
        faces = triangle.faces
        
        # Draw each face
        for face in faces:
            # Get the vertices for this face
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]
            
            # Draw the face
            glVertex3f(v0[0] - triangle.position[0], v0[1] - triangle.position[1], v0[2] - triangle.position[2])
            glVertex3f(v1[0] - triangle.position[0], v1[1] - triangle.position[1], v1[2] - triangle.position[2])
            glVertex3f(v2[0] - triangle.position[0], v2[1] - triangle.position[1], v2[2] - triangle.position[2])
        
        glEnd()
    
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
    
    def _render_triangle(self, triangle):
        """Render a triangle object."""
        # Draw the triangle using its vertices and faces
        glBegin(GL_TRIANGLES)
        
        # Get the vertices and faces
        vertices = triangle.vertices
        faces = triangle.faces
        
        # Calculate normals for each face
        for face in faces:
            # Get the vertices for this face
            v0 = np.array(vertices[face[0]])
            v1 = np.array(vertices[face[1]])
            v2 = np.array(vertices[face[2]])
            
            # Calculate face normal using cross product
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            
            # Normalize the normal vector
            if np.linalg.norm(normal) > 0:
                normal = normal / np.linalg.norm(normal)
            
            # Set the normal for this face
            glNormal3f(normal[0], normal[1], normal[2])
            
            # Draw the face
            glVertex3f(v0[0] - triangle.position[0], v0[1] - triangle.position[1], v0[2] - triangle.position[2])
            glVertex3f(v1[0] - triangle.position[0], v1[1] - triangle.position[1], v1[2] - triangle.position[2])
            glVertex3f(v2[0] - triangle.position[0], v2[1] - triangle.position[1], v2[2] - triangle.position[2])
        
        glEnd()
    
    def render_skybox(self):
        """Render a gradient skybox."""
        # Save current matrix and disable depth test temporarily
        glPushMatrix()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Set clear color to a nice sky gradient
        glClearColor(0.4, 0.6, 0.9, 1.0)
        
        # Draw a distant backdrop for the sky
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Draw a gradient quad for the sky
        glBegin(GL_QUADS)
        # Top color (lighter blue)
        glColor3f(0.5, 0.7, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        
        # Bottom color (darker blue)
        glColor3f(0.2, 0.4, 0.8)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glEnd()
        
        # Restore projection matrix
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        # Restore settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix() 