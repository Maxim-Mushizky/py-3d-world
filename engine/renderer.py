import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from engine.shapes import Rectangle, Plane, Cube, Triangle, InteractiveTriangle, InteractiveCube, Sphere, InteractiveSphere
import time

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
                'position': (5.0, 15.0, 5.0, 1.0),  # Higher position for better shadow projection
                'ambient': (0.2, 0.2, 0.2, 1.0),
                'diffuse': (0.9, 0.9, 0.9, 1.0),
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
        
        # Shadow settings
        self.shadows_enabled = True
        self.show_light_sources = True
        
        # HUD settings
        self.show_hud = True
        self.font = pygame.font.SysFont('Arial', 18)
        self.hud_color = (255, 255, 255)
        self.hud_bg_color = (0, 0, 0, 128)  # Semi-transparent black
        
        # Initialize OpenGL settings and lighting
        self.setup_opengl()
        self.setup_lighting()
    
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
    
    def update(self, dt):
        """Update time-based effects."""
        self.time += dt
        
        # No more light rotation - keep lights in fixed positions
        # Fill light in a fixed position
        self.lights['fill']['position'] = (-8.0, 5.0, -3.0, 1.0)
        
        # Update the light position in OpenGL
        glLight(GL_LIGHT1, GL_POSITION, self.lights['fill']['position'])
        
        # Main light in a fixed position
        self.lights['main']['position'] = (5.0, 15.0, 5.0, 1.0)
        glLight(GL_LIGHT0, GL_POSITION, self.lights['main']['position'])
    
    def render(self, camera):
        """Render the entire scene."""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up the camera view
        glLoadIdentity()
        camera.apply()
        
        # Draw a simple skybox
        self.render_skybox()
        
        # First pass: Render all objects normally
        for obj in self.world.get_objects():
            self._render_object(obj)
        
        # Second pass: Render shadows if enabled
        if self.shadows_enabled:
            self.render_shadows()
        
        # Draw light sources as small spheres for visualization
        if self.show_light_sources:
            self._draw_light_sources()
            
        # Render HUD if enabled
        if self.show_hud:
            self.render_hud(camera)
    
    def render_shadows(self):
        """Render shadows for all objects."""
        # Save current state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Disable lighting for shadows
        glDisable(GL_LIGHTING)
        
        # Disable depth writing but keep depth testing
        glDepthMask(GL_FALSE)
        
        # Enable blending for semi-transparent shadows
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set shadow color (semi-transparent black)
        glColor4f(0.0, 0.0, 0.0, 0.4)  # Slightly less opaque for better blending
        
        # Draw each object's shadow
        for obj in self.world.get_objects():
            # Skip the ground plane for shadows
            if isinstance(obj, Plane):
                continue
            
            # Draw a simple shadow directly below the object
            glPushMatrix()
            
            # Translate to the object's x,z position but at y=0.01 (just above ground)
            glTranslatef(obj.position[0], 0.01, obj.position[2])
            
            # Scale the shadow based on the object's height
            # Higher objects cast larger shadows
            shadow_scale = 1.0 + (obj.position[1] * 0.1)
            
            # For cubes and rectangles, we'll draw a simple quad shadow
            if isinstance(obj, (Cube, InteractiveCube)):
                self._render_cube_flat_shadow(obj, shadow_scale)
            elif isinstance(obj, Rectangle):
                self._render_rectangle_flat_shadow(obj, shadow_scale)
            elif isinstance(obj, (Triangle, InteractiveTriangle)):
                self._render_triangle_flat_shadow(obj, shadow_scale)
            elif isinstance(obj, (Sphere, InteractiveSphere)):
                self._render_sphere_flat_shadow(obj, shadow_scale)
            
            glPopMatrix()
        
        # Restore state
        glPopAttrib()
    
    def _render_cube_flat_shadow(self, cube, scale_factor):
        """Render a simple flat shadow for a cube."""
        # Calculate shadow size based on cube dimensions
        width = cube.width * scale_factor
        depth = cube.depth * scale_factor
        
        # Draw a simple quad for the shadow
        glBegin(GL_QUADS)
        glVertex3f(-width/2, 0.0, -depth/2)
        glVertex3f(-width/2, 0.0, depth/2)
        glVertex3f(width/2, 0.0, depth/2)
        glVertex3f(width/2, 0.0, -depth/2)
        glEnd()
    
    def _render_rectangle_flat_shadow(self, rect, scale_factor):
        """Render a simple flat shadow for a rectangle."""
        # Calculate shadow size based on rectangle dimensions
        width = rect.width * scale_factor
        depth = rect.depth * scale_factor
        
        # Draw a simple quad for the shadow
        glBegin(GL_QUADS)
        glVertex3f(-width/2, 0.0, -depth/2)
        glVertex3f(-width/2, 0.0, depth/2)
        glVertex3f(width/2, 0.0, depth/2)
        glVertex3f(width/2, 0.0, -depth/2)
        glEnd()
    
    def _render_triangle_flat_shadow(self, triangle, scale_factor):
        """Render a simple flat shadow for a triangle."""
        # For triangles, we'll project the base onto the ground
        # Get the base size of the triangle
        base_size = 0.0
        if hasattr(triangle, 'size'):
            base_size = triangle.size * scale_factor
        else:
            # Estimate from vertices
            base_size = 2.0 * scale_factor  # Default fallback
        
        # Draw a simple triangle shadow
        glBegin(GL_TRIANGLES)
        glVertex3f(-base_size/2, 0.0, -base_size/2)
        glVertex3f(base_size/2, 0.0, -base_size/2)
        glVertex3f(0.0, 0.0, base_size/2)
        glEnd()
    
    def _render_sphere_flat_shadow(self, sphere, scale_factor):
        """Render a simple flat shadow for a sphere."""
        # Calculate shadow size based on sphere radius
        radius = sphere.radius * scale_factor
        
        # Draw a simple circle for the shadow
        # We'll approximate a circle with a polygon
        glBegin(GL_POLYGON)
        segments = 32  # Number of segments to approximate the circle
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            glVertex3f(x, 0.0, z)
        glEnd()
    
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
        if isinstance(obj, (InteractiveCube, InteractiveTriangle, InteractiveSphere)):
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
        elif isinstance(obj, (Sphere, InteractiveSphere)):
            self._render_sphere(obj)
        
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
        
        # Draw the main plane
        glBegin(GL_QUADS)
        glNormal3f(0.0, 1.0, 0.0)  # Normal pointing up
        glVertex3f(-size, 0.0, -size)
        glVertex3f(-size, 0.0, size)
        glVertex3f(size, 0.0, size)
        glVertex3f(size, 0.0, -size)
        glEnd()
        
        # Draw a grid on the plane to make shadows more visible
        if hasattr(plane, 'color') and plane.color[1] > 0.5:  # Only draw grid on green ground
            self._draw_grid(size)
    
    def _draw_grid(self, size):
        """Draw a grid on the ground plane to make shadows more visible."""
        # Save current color
        current_color = glGetFloatv(GL_CURRENT_COLOR)
        
        # Set grid color (slightly darker than the plane)
        grid_color = (0.2, 0.4, 0.2, 1.0)
        glColor4fv(grid_color)
        
        # Disable lighting for the grid
        glDisable(GL_LIGHTING)
        
        # Draw grid lines
        glBegin(GL_LINES)
        
        # Draw lines along X axis
        step = 2.0
        for i in range(-int(size), int(size) + 1, int(step)):
            if i == 0:  # Make center lines thicker
                glEnd()
                glLineWidth(3.0)
                glBegin(GL_LINES)
                glVertex3f(i, 0.01, -size)
                glVertex3f(i, 0.01, size)
                glEnd()
                glLineWidth(1.0)
                glBegin(GL_LINES)
            else:
                glVertex3f(float(i), 0.01, -size)
                glVertex3f(float(i), 0.01, size)
        
        # Draw lines along Z axis
        for i in range(-int(size), int(size) + 1, int(step)):
            if i == 0:  # Make center lines thicker
                glEnd()
                glLineWidth(3.0)
                glBegin(GL_LINES)
                glVertex3f(-size, 0.01, i)
                glVertex3f(size, 0.01, i)
                glEnd()
                glLineWidth(1.0)
                glBegin(GL_LINES)
            else:
                glVertex3f(-size, 0.01, float(i))
                glVertex3f(size, 0.01, float(i))
        
        glEnd()
        
        # Restore lighting
        glEnable(GL_LIGHTING)
        
        # Restore original color
        glColor4fv(current_color)
    
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
    
    def _render_sphere(self, sphere):
        """Render a sphere object."""
        # Create a new quadric object
        quadric = gluNewQuadric()
        
        # Set the drawing style (GLU_FILL for solid, GLU_LINE for wireframe)
        gluQuadricDrawStyle(quadric, GLU_FILL)
        
        # Enable texture coordinates if needed
        gluQuadricTexture(quadric, GL_TRUE)
        
        # Generate normals for proper lighting
        gluQuadricNormals(quadric, GLU_SMOOTH)
        
        # Draw the sphere
        gluSphere(quadric, sphere.radius, sphere.resolution, sphere.resolution)
        
        # Delete the quadric object to free memory
        gluDeleteQuadric(quadric)
    
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
    
    def toggle_shadows(self):
        """Toggle shadows on/off."""
        self.shadows_enabled = not self.shadows_enabled
        return self.shadows_enabled
    
    def toggle_light_visualization(self):
        """Toggle light source visualization on/off."""
        self.show_light_sources = not self.show_light_sources
        return self.show_light_sources
    
    def render_hud(self, camera):
        """Render the heads-up display with player information."""
        # Switch to orthographic projection for 2D rendering
        self._setup_ortho_projection()
        
        # Get the display size
        display_size = pygame.display.get_surface().get_size()
        
        # Prepare HUD information
        position_text = f"Position: X: {camera.position[0]:.2f}, Y: {camera.position[1]:.2f}, Z: {camera.position[2]:.2f}"
        
        # Get player state from physics engine
        player_state = ""
        velocity_text = ""
        jump_info = ""
        
        if hasattr(camera, 'physics_engine'):
            physics = camera.physics_engine
            
            # Player state
            if physics.on_ground:
                player_state = "State: On Ground"
            elif physics.standing_on_platform:
                player_state = f"State: On Platform (Height: {physics.platform_height:.2f})"
            elif physics.jumping:
                player_state = "State: Jumping"
            else:
                player_state = "State: In Air"
            
            # Velocity information
            velocity = physics.velocity
            velocity_magnitude = np.linalg.norm(velocity)
            velocity_text = f"Velocity: {velocity_magnitude:.2f} m/s | X: {velocity[0]:.2f}, Y: {velocity[1]:.2f}, Z: {velocity[2]:.2f}"
            
            # Jump information
            current_time = time.time()
            time_since_jump = current_time - physics.last_jump_time
            jump_info = f"Jump Cooldown: {physics.jump_cooldown:.2f}s | Time Since Jump: {time_since_jump:.2f}s"
        
        # Camera direction
        look_dir = camera.get_direction()
        direction_text = f"Looking: X: {look_dir[0]:.2f}, Y: {look_dir[1]:.2f}, Z: {look_dir[2]:.2f}"
        
        # Game statistics
        fps_text = f"FPS: {pygame.time.Clock().get_fps():.1f}"
        objects_count = len(self.world.get_objects())
        interactive_count = len(self.world.get_interactive_objects())
        objects_text = f"Objects: {objects_count} (Interactive: {interactive_count})"
        
        # Shadow and lighting status
        shadow_status = "ON" if self.shadows_enabled else "OFF"
        lights_status = "ON" if self.show_light_sources else "OFF"
        status_text = f"Shadows: {shadow_status} | Lights: {lights_status}"
        
        # Render HUD elements with semi-transparent background
        y_pos = 10
        line_height = 25
        
        # Left side information (player stats)
        self._render_text(position_text, 10, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(player_state, 10, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(velocity_text, 10, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(direction_text, 10, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(jump_info, 10, y_pos, self.hud_color)
        
        # Right side information (game stats)
        right_x = display_size[0] - 250
        y_pos = 10
        self._render_text(fps_text, right_x, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(objects_text, right_x, y_pos, self.hud_color)
        y_pos += line_height
        self._render_text(status_text, right_x, y_pos, self.hud_color)
        
        # Add controls reminder at the bottom
        controls_text = "Controls: WASD = Move, Space = Jump, H = Toggle HUD, F3 = Debug, L = Lights, S = Shadows, R = Reset Objects, ESC = Quit"
        self._render_text(controls_text, 10, display_size[1] - 30, self.hud_color)
        
        # Restore perspective projection
        self._restore_projection()
    
    def _setup_ortho_projection(self):
        """Set up orthographic projection for 2D rendering."""
        # Save the current matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Switch to orthographic projection
        display_size = pygame.display.get_surface().get_size()
        glOrtho(0, display_size[0], display_size[1], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing and lighting for 2D elements
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
    
    def _restore_projection(self):
        """Restore the 3D projection matrix."""
        # Restore the projection matrix
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        # Restore the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # Re-enable depth testing and lighting
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def _render_text(self, text, x, y, color):
        """Render text at the specified position."""
        # Create a surface with the text
        text_surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Get the size of the text surface
        width, height = text_surface.get_size()
        
        # Draw a semi-transparent background
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(x - 5, y - 5)
        glVertex2f(x + width + 5, y - 5)
        glVertex2f(x + width + 5, y + height + 5)
        glVertex2f(x - 5, y + height + 5)
        glEnd()
        
        # Enable blending for transparent text
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw the text
        glRasterPos2f(x, y + height)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        # Disable blending
        glDisable(GL_BLEND)
    
    def toggle_hud(self):
        """Toggle the HUD display on/off."""
        self.show_hud = not self.show_hud
        return self.show_hud 