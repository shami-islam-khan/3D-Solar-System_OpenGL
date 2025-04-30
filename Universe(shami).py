# Imports
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math
import random

# --- Constants ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
FOV_Y = 60.0  # Field of View in Y direction
NEAR_CLIP = 0.1
FAR_CLIP = 5000.0 # Increased far clip to see Neptune clearly

# Planet/Sun Sizes (Approximate relative scale)
SUN_RADIUS = 40.0 # Reduced sun size for better viewing
MERCURY_RADIUS = 4.0
VENUS_RADIUS = 8.0
EARTH_RADIUS = 9.0
MARS_RADIUS = 7.0
JUPITER_RADIUS = 25.0
SATURN_RADIUS = 20.0
SATURN_RING_INNER = 25.0
SATURN_RING_OUTER = 35.0
URANUS_RADIUS = 15.0
NEPTUNE_RADIUS = 14.0

# Planet Orbital Radii
MERCURY_ORBIT_RADIUS = 70.0
VENUS_ORBIT_RADIUS = 100.0
EARTH_ORBIT_RADIUS = 150.0
MARS_ORBIT_RADIUS = 200.0
JUPITER_ORBIT_RADIUS = 300.0
SATURN_ORBIT_RADIUS = 400.0
URANUS_ORBIT_RADIUS = 470.0
NEPTUNE_ORBIT_RADIUS = 530.0

# Asteroid Belt Parameters
ASTEROID_BELT_INNER_RADIUS = 220.0
ASTEROID_BELT_OUTER_RADIUS = 280.0
NUM_ASTEROIDS = 250 # Increased for denser belt
ASTEROID_MIN_SIZE = 0.5
ASTEROID_MAX_SIZE = 2.5
ASTEROID_BELT_HEIGHT = 15.0 # Max deviation from ecliptic

# Starfield Parameters
NUM_STARS = 300
STARFIELD_RADIUS = 1500 # Make starfield larger

# Sphere Tessellation Quality
SPHERE_SLICES = 30
SPHERE_STACKS = 30
RING_SLICES = 50
RING_LOOPS = 5

# Rotation Speeds (radians per frame - adjusted for visual appeal)
MERCURY_ORBIT_SPEED = 0.0100
VENUS_ORBIT_SPEED = 0.0070
EARTH_ORBIT_SPEED = 0.0050
MARS_ORBIT_SPEED = 0.0040
JUPITER_ORBIT_SPEED = 0.0020
SATURN_ORBIT_SPEED = 0.0015
URANUS_ORBIT_SPEED = 0.0010
NEPTUNE_ORBIT_SPEED = 0.0008
ASTEROID_ORBIT_SPEED = 0.001 # Base speed for asteroid rotation

# Planet Self-Rotation Speeds (Degrees per frame)
EARTH_ROTATION_SPEED = 5.0 # Example: Earth rotates faster

# --- Scene Objects ---
stars = []
asteroids = []
ring_quadric = None # For Saturn's rings

# --- Simulation State ---
mercury_orbit_angle = 0.0
venus_orbit_angle = 0.0
earth_orbit_angle = 0.0
mars_orbit_angle = 0.0
jupiter_orbit_angle = 0.0
saturn_orbit_angle = 0.0
uranus_orbit_angle = 0.0
neptune_orbit_angle = 0.0

# --- Camera ---
# Initial camera position slightly above Earth's orbit plane, looking at the Sun
camera_pos = [0.0, 40.0, EARTH_ORBIT_RADIUS + 60.0] # Start slightly further back
camera_target = [0.0, 0.0, 0.0] # Look at the origin (Sun)
camera_up = [0.0, 1.0, 0.0] # Y is up
CAMERA_MOVE_SPEED = 10.0
CAMERA_ZOOM_SPEED = 10.0

# --- Lighting ---
sun_light_position = [0.0, 0.0, 0.0, 1.0]  # Positioned at the Sun (origin)
sun_light_diffuse = [1.0, 1.0, 0.9, 1.0]   # Sunlight color (slightly yellow)
sun_light_ambient = [0.1, 0.1, 0.1, 1.0]   # Minimal ambient light
sun_light_specular = [0.8, 0.8, 0.8, 1.0] # White specular highlights
material_specular = [1.0, 1.0, 1.0, 1.0] # Material specular reflection color (white)
material_shininess = 50.0                # Material shininess exponent

# Planet Materials (Ambient and Diffuse properties)
# Using lists [R, G, B, Alpha]
MAT_SUN = [1.0, 0.8, 0.0, 1.0] # Sun is emissive, but use color when lighting off
MAT_MERCURY = [0.6, 0.6, 0.6, 1.0] # Grey
MAT_VENUS = [0.8, 0.7, 0.5, 1.0] # Yellowish-brown
MAT_EARTH = [0.2, 0.4, 0.8, 1.0] # Blue/Green dominant
MAT_MARS = [0.8, 0.3, 0.1, 1.0] # Reddish
MAT_JUPITER = [0.7, 0.6, 0.4, 1.0] # Orangey-brown bands
MAT_SATURN = [0.8, 0.75, 0.6, 1.0] # Pale yellow
MAT_SATURN_RING = [0.6, 0.6, 0.5, 0.7] # Greyish, slightly transparent
MAT_URANUS = [0.6, 0.8, 0.9, 1.0] # Pale blue/cyan
MAT_NEPTUNE = [0.3, 0.5, 0.9, 1.0] # Deeper blue

# --- Initialization Functions ---

def initialize_stars():
    """Populates the 'stars' list with random 3D coordinates."""
    global stars
    stars = []
    for _ in range(NUM_STARS):
        # Distribute stars on the surface of a large sphere
        phi = random.uniform(0, 2 * math.pi)
        costheta = random.uniform(-1, 1)
        theta = math.acos(costheta)
        
        x = STARFIELD_RADIUS * math.sin(theta) * math.cos(phi)
        y = STARFIELD_RADIUS * math.sin(theta) * math.sin(phi)
        z = STARFIELD_RADIUS * math.cos(theta)
        stars.append((x, y, z))

def initialize_asteroids():
    """Populates the 'asteroids' list with positions, sizes, and colors."""
    global asteroids
    asteroids = []
    for _ in range(NUM_ASTEROIDS):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(ASTEROID_BELT_INNER_RADIUS, ASTEROID_BELT_OUTER_RADIUS)
        height = random.uniform(-ASTEROID_BELT_HEIGHT, ASTEROID_BELT_HEIGHT) # Deviation from Y=0 plane
        
        x = distance * math.cos(angle)
        z = distance * math.sin(angle)
        y = height
        
        size = random.uniform(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        color_val = random.uniform(0.3, 0.7)  # Grayish colors
        color = [color_val, color_val, color_val, 1.0]
        
        # Store initial angle and distance for rotation in idle()
        asteroids.append({
            "x": x, "y": y, "z": z,
            "size": size, "color": color,
            "angle": angle, "distance": distance, "height": y # Store orbital parameters
        })

def initialize_scene():
    """Initializes stars, asteroids, and Saturn's ring quadric."""
    global ring_quadric
    print("Initializing Scene...")
    initialize_stars()
    initialize_asteroids()
    ring_quadric = gluNewQuadric() # Create the quadric object once
    gluQuadricNormals(ring_quadric, GLU_SMOOTH) # Optional: improve lighting on rings
    print("Initialization Complete.")

# --- Drawing Functions ---

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen using bitmap fonts."""
    glColor3f(1.0, 1.0, 1.0) # White text
    glWindowPos2f(x, y)      # Use window coordinates
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_earth():
    glPushMatrix()
    glRotatef(math.degrees(earth_orbit_angle), 0, 1, 0)  # Orbit around Sun
    glTranslatef(EARTH_ORBIT_RADIUS, 0, 0)
    
    # Earth's rotation (day/night cycle)
    glRotatef(math.degrees(earth_orbit_angle * 50), 0, 1, 0)  # Faster rotation
    
    # Calculate Earth's position relative to Sun
    earth_pos = (
        EARTH_ORBIT_RADIUS * math.cos(earth_orbit_angle),
        0,
        EARTH_ORBIT_RADIUS * math.sin(earth_orbit_angle)
    )
    
    # Manual lighting calculation
    for i in range(0, 180, 10):  # Longitude slices
        glBegin(GL_QUAD_STRIP)
        for j in range(0, 360, 10):  # Latitude slices
            # Calculate vertex positions
            x = EARTH_RADIUS * math.sin(math.radians(i)) * math.cos(math.radians(j))
            y = EARTH_RADIUS * math.cos(math.radians(i))
            z = EARTH_RADIUS * math.sin(math.radians(i)) * math.sin(math.radians(j))
            
            # Calculate dot product for lighting (simplified)
            dot = -(x * earth_pos[0] + y * earth_pos[1] + z * earth_pos[2])
            dot = max(0, dot)  # Clamp to 0-1 range
            
            # Day side (blue/green)
            if dot > 0.1:
                glColor3f(0.2, 0.4, 0.8)  # Ocean blue
            # Twilight zone
            elif dot > 0.05:
                glColor3f(0.3, 0.5, 0.6)  # Darker blue
            # Night side
            else:
                glColor3f(0.05, 0.05, 0.1)  # Very dark
            
            glVertex3f(x, y, z)
            
            # Next latitude slice
            x = EARTH_RADIUS * math.sin(math.radians(i+10)) * math.cos(math.radians(j))
            y = EARTH_RADIUS * math.cos(math.radians(i+10))
            z = EARTH_RADIUS * math.sin(math.radians(i+10)) * math.sin(math.radians(j))
            
            # Recalculate dot product
            dot = -(x * earth_pos[0] + y * earth_pos[1] + z * earth_pos[2])
            dot = max(0, dot)
            
            if dot > 0.1:
                glColor3f(0.2, 0.4, 0.8)
            elif dot > 0.05:
                glColor3f(0.3, 0.5, 0.6)
            else:
                glColor3f(0.05, 0.05, 0.1)
            
            glVertex3f(x, y, z)
        glEnd()
    glPopMatrix()



def draw_starfield():
    """Draws the starfield using GL_POINTS."""
    glDisable(GL_LIGHTING) # Stars are not affected by light
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0) # White stars
    for x, y, z in stars:
        glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING) # Re-enable for other objects

def draw_orbit_lines():
    """Draws circular orbit lines for each planet."""
    glDisable(GL_LIGHTING) # Lines are not affected by light
    glLineWidth(1)
    glColor3f(0.3, 0.3, 0.3) # Dim grey lines
    
    orbit_radii = [
        MERCURY_ORBIT_RADIUS, VENUS_ORBIT_RADIUS, EARTH_ORBIT_RADIUS,
        MARS_ORBIT_RADIUS, JUPITER_ORBIT_RADIUS, SATURN_ORBIT_RADIUS,
        URANUS_ORBIT_RADIUS, NEPTUNE_ORBIT_RADIUS
    ]
    
    for radius in orbit_radii:
        glBegin(GL_LINE_LOOP)
        for i in range(100): # 100 segments for a smooth circle
            angle = i * 2 * math.pi / 100
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0, z) # Orbits are on the Y=0 plane
        glEnd()
    glEnable(GL_LIGHTING) # Re-enable for other objects

def draw_asteroid_belt():
    """Draws the asteroid belt using GL_POINTS."""
    # Asteroids are affected by lighting, so keep it enabled
    glPointSize(2) # Asteroids as small points
    glBegin(GL_POINTS)
    for asteroid in asteroids:
        # Use the material color defined for the asteroid
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, asteroid["color"])
        # Draw the asteroid at its current position
        glVertex3f(asteroid["x"], asteroid["y"], asteroid["z"])
    glEnd()
    

def draw_solar_system():
    """Draws the Sun and planets with lighting and materials."""
    global earth_orbit_angle, mars_orbit_angle, jupiter_orbit_angle, saturn_orbit_angle
    global mercury_orbit_angle, venus_orbit_angle, uranus_orbit_angle, neptune_orbit_angle

    # --- Sun (Source of Light) ---
    # Disable lighting for the sun itself, as it emits light
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glColor3fv(MAT_SUN[:3]) # Use glColor as it's not lit
    glutSolidSphere(SUN_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()
    glEnable(GL_LIGHTING) # Re-enable lighting for planets

    # --- Mercury ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_MERCURY)
    glRotatef(math.degrees(mercury_orbit_angle), 0, 1, 0) # Rotate orbit
    glTranslatef(MERCURY_ORBIT_RADIUS, 0, 0)
    # Add self-rotation here if desired
    glutSolidSphere(MERCURY_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Venus ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_VENUS)
    glRotatef(math.degrees(venus_orbit_angle), 0, 1, 0)
    glTranslatef(VENUS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(VENUS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Earth ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_EARTH)
    glRotatef(math.degrees(earth_orbit_angle), 0, 1, 0) # Orbit rotation
    glTranslatef(EARTH_ORBIT_RADIUS, 0, 0)
    glRotatef(earth_orbit_angle * EARTH_ROTATION_SPEED, 0, 1, 0.1) # Self-rotation (slight tilt)
    glutSolidSphere(EARTH_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Mars ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_MARS)
    glRotatef(math.degrees(mars_orbit_angle), 0, 1, 0)
    glTranslatef(MARS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(MARS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Jupiter ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_JUPITER)
    glRotatef(math.degrees(jupiter_orbit_angle), 0, 1, 0)
    glTranslatef(JUPITER_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(JUPITER_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Saturn ---
    glPushMatrix()
    # Planet
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_SATURN)
    glRotatef(math.degrees(saturn_orbit_angle), 0, 1, 0)
    glTranslatef(SATURN_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(SATURN_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    # Rings
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_SATURN_RING)
    glRotatef(90, 1, 0, 0) # Rotate coordinate system for rings
    # Use the pre-created quadric object
    gluDisk(ring_quadric, SATURN_RING_INNER, SATURN_RING_OUTER, RING_SLICES, RING_LOOPS)
    # Draw the other side of the disk (optional, if backface culling is off)
    # gluDisk(ring_quadric, SATURN_RING_INNER, SATURN_RING_OUTER, RING_SLICES, RING_LOOPS) # Draw back face? Check culling.
    glPopMatrix()

    # --- Uranus ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_URANUS)
    glRotatef(math.degrees(uranus_orbit_angle), 0, 1, 0)
    glTranslatef(URANUS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(URANUS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Neptune ---
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_NEPTUNE)
    glRotatef(math.degrees(neptune_orbit_angle), 0, 1, 0)
    glTranslatef(NEPTUNE_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(NEPTUNE_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

# --- Setup Functions ---

def setup_lighting():
    """Configures OpenGL lighting."""
    glEnable(GL_LIGHTING)       # Enable lighting calculations
    glEnable(GL_LIGHT0)         # Enable light source 0 (the Sun)
    
    # Set light properties
    glLightfv(GL_LIGHT0, GL_POSITION, sun_light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, sun_light_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_light_specular) # Add specular component
    
    # Configure how light affects materials globally
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE) # More realistic specular highlights
    
    # Set global material properties (can be overridden per object)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, material_shininess)
    
    # Enable normalization of normals (important for scaled objects, good practice)
    glEnable(GL_NORMALIZE)
    # Use smooth shading for nicer visuals
    glShadeModel(GL_SMOOTH)

def setupCamera():
    """Sets up the projection and modelview matrices for the camera."""
    # Projection Matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), NEAR_CLIP, FAR_CLIP)
    
    # ModelView Matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cx, cy, cz = camera_pos
    tx, ty, tz = camera_target
    ux, uy, uz = camera_up
    gluLookAt(cx, cy, cz, tx, ty, tz, ux, uy, uz)

# --- GLUT Callback Functions ---

def keyboardListener(key, x, y):
    """Handles standard keyboard input."""
    global camera_pos
    
    x_cam, y_cam, z_cam = camera_pos
    
    # Basic WASD for translation on X/Z plane, Q/E for up/down
    if key == b'w':
        z_cam -= CAMERA_MOVE_SPEED # Move forward
    elif key == b's':
        z_cam += CAMERA_MOVE_SPEED # Move backward
    elif key == b'a':
        x_cam -= CAMERA_MOVE_SPEED # Strafe left
    elif key == b'd':
        x_cam += CAMERA_MOVE_SPEED # Strafe right
    elif key == b'q': # Use Q for up
        y_cam += CAMERA_MOVE_SPEED # Move up
    elif key == b'e': # Use E for down
        y_cam -= CAMERA_MOVE_SPEED # Move down
    elif key == b'z': # Zoom in (move closer along view axis - simplified here)
         # A proper zoom would move towards the look-at point
         z_cam -= CAMERA_ZOOM_SPEED
    elif key == b'x': # Zoom out
         z_cam += CAMERA_ZOOM_SPEED
    elif key == b'\x1b': # Escape key
        glutLeaveMainLoop() # Exit the application

    camera_pos = [x_cam, y_cam, z_cam]
    glutPostRedisplay() # Request redraw after camera move


def specialKeyListener(key, x, y):
    """Handles special key input (arrows, function keys)."""
    # Example: Use arrow keys for rotation (more complex to implement)
    # if key == GLUT_KEY_UP:
    #     pass # Rotate camera up
    # elif key == GLUT_KEY_DOWN:
    #     pass # Rotate camera down
    # elif key == GLUT_KEY_LEFT:
    #     pass # Rotate camera left
    # elif key == GLUT_KEY_RIGHT:
    #     pass # Rotate camera right
    pass # Not implemented for now

def mouseListener(button, state, x, y):
    """Handles mouse button clicks."""
    # Example: Could be used for orbiting camera, selecting objects, etc.
    # if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
    #     print(f"Mouse Clicked at: ({x}, {y})")
    pass # Not implemented for now

def idle():
    """Called by GLUT when idle. Updates animation state."""
    global earth_orbit_angle, mars_orbit_angle, jupiter_orbit_angle, saturn_orbit_angle
    global mercury_orbit_angle, venus_orbit_angle, uranus_orbit_angle, neptune_orbit_angle
    global asteroids

    # Update planet orbital angles
    mercury_orbit_angle = (mercury_orbit_angle + MERCURY_ORBIT_SPEED) % (2 * math.pi)
    venus_orbit_angle = (venus_orbit_angle + VENUS_ORBIT_SPEED) % (2 * math.pi)
    earth_orbit_angle = (earth_orbit_angle + EARTH_ORBIT_SPEED) % (2 * math.pi)
    mars_orbit_angle = (mars_orbit_angle + MARS_ORBIT_SPEED) % (2 * math.pi)
    jupiter_orbit_angle = (jupiter_orbit_angle + JUPITER_ORBIT_SPEED) % (2 * math.pi)
    saturn_orbit_angle = (saturn_orbit_angle + SATURN_ORBIT_SPEED) % (2 * math.pi)
    uranus_orbit_angle = (uranus_orbit_angle + URANUS_ORBIT_SPEED) % (2 * math.pi)
    neptune_orbit_angle = (neptune_orbit_angle + NEPTUNE_ORBIT_SPEED) % (2 * math.pi)

    # Update asteroid positions based on their individual (simplified) orbits
    for asteroid in asteroids:
        # Simple circular orbit based on initial parameters
        asteroid["angle"] = (asteroid["angle"] + ASTEROID_ORBIT_SPEED * (ASTEROID_BELT_INNER_RADIUS / asteroid["distance"])) % (2 * math.pi)
        asteroid["x"] = asteroid["distance"] * math.cos(asteroid["angle"])
        asteroid["z"] = asteroid["distance"] * math.sin(asteroid["angle"])
        # Keep y (height) constant for simplicity, or add oscillation if desired

    glutPostRedisplay() # Request redraw

def display():
    """The main display function called by GLUT."""
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
    
    # Set up camera and lighting for this frame
    setupCamera()
    setup_lighting()
    
    # Draw scene components
    draw_starfield()
    draw_orbit_lines()
    draw_asteroid_belt()
    draw_solar_system()
    
    # Example: Draw some text info
    # Disable lighting and depth test for 2D text overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    draw_text(10, WINDOW_HEIGHT - 20, "Solar System Simulation")
    draw_text(10, 10, "WASDQE: Move Camera | Z/X: Zoom (simple) | ESC: Exit")
    
    # Restore previous states
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    # Swap buffers to show the rendered frame
    glutSwapBuffers()

# --- Main Function ---
def main():
    """Initializes GLUT, sets up callbacks, and starts the main loop."""
    glutInit()
    # Request double buffering, RGB color, and depth buffer
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100) # Position window
    wind = glutCreateWindow(b"OpenGL Solar System - Cleaned") # Window title

    # Register callback functions
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Initialize scene data (stars, asteroids)
    initialize_scene()

    # Enable necessary OpenGL features
    glEnable(GL_DEPTH_TEST) # Enable depth testing for 3D occlusion
    # Blending might be needed for transparency (like Saturn's rings if alpha < 1)
    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    print("Starting GLUT Main Loop...")
    glutMainLoop() # Start the event processing loop

if __name__ == "__main__":
    main()