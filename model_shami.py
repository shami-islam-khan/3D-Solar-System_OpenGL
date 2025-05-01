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

# for gravity
GRAVITY_FACTOR = 1.0  # Normal gravity (1.0 = default)
GRAVITY_STEP = 0.1    # How much to change gravity with each key press

# Planet/Sun Sizes (Approximate relative scale)
SUN_RADIUS = 30.0 # Reduced sun size for better viewing
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

moon_orbit_angle = 0.0  # Add with other orbit angles


# --- Moon Parameters ---
# Earth (already done)
MOON_RADIUS = 2.5
MOON_ORBIT_RADIUS = 15.0
MOON_ORBIT_SPEED = 0.02
MOON_MATERIAL = [0.7, 0.7, 0.7, 1.0]  # Gray (Earth's Moon)

# Mars (Phobos & Deimos)
PHOBOS_RADIUS = 1.2
PHOBOS_ORBIT_RADIUS = 9.0
PHOBOS_ORBIT_SPEED = 0.03
PHOBOS_MATERIAL = [0.5, 0.4, 0.3, 1.0]  # Dark gray

DEIMOS_RADIUS = 0.8
DEIMOS_ORBIT_RADIUS = 12.0
DEIMOS_ORBIT_SPEED = 0.025
DEIMOS_MATERIAL = [0.4, 0.3, 0.2, 1.0]  # Reddish-gray

# Jupiter (4 Galilean moons)
IO_RADIUS = 3.0
IO_ORBIT_RADIUS = 30.0
IO_ORBIT_SPEED = 0.04
IO_MATERIAL = [0.9, 0.6, 0.3, 1.0]  # Sulfur yellow

EUROPA_RADIUS = 2.8
EUROPA_ORBIT_RADIUS = 45.0
EUROPA_ORBIT_SPEED = 0.035
EUROPA_MATERIAL = [0.8, 0.8, 0.9, 1.0]  # Ice white

GANYMEDE_RADIUS = 4.0
GANYMEDE_ORBIT_RADIUS = 60.0
GANYMEDE_ORBIT_SPEED = 0.03
GANYMEDE_MATERIAL = [0.6, 0.6, 0.7, 1.0]  # Pale blue

CALLISTO_RADIUS = 3.8
CALLISTO_ORBIT_RADIUS = 75.0
CALLISTO_ORBIT_SPEED = 0.025
CALLISTO_MATERIAL = [0.5, 0.5, 0.5, 1.0]  # Gray

# Saturn (Titan - largest moon)
TITAN_RADIUS = 4.5
TITAN_ORBIT_RADIUS = 50.0
TITAN_ORBIT_SPEED = 0.02
TITAN_MATERIAL = [0.8, 0.6, 0.4, 1.0]  # Orange haze

# Uranus (Titania - largest moon)
TITANIA_RADIUS = 3.2
TITANIA_ORBIT_RADIUS = 40.0
TITANIA_ORBIT_SPEED = 0.015
TITANIA_MATERIAL = [0.7, 0.7, 0.8, 1.0]  # Icy blue

# Neptune (Triton - largest moon)
TRITON_RADIUS = 3.5
TRITON_ORBIT_RADIUS = 35.0
TRITON_ORBIT_SPEED = 0.018
TRITON_MATERIAL = [0.6, 0.7, 0.8, 1.0]  # Frozen nitrogen


# Moon orbit angles (add near other orbit angles)
phobos_orbit_angle = 0.0
deimos_orbit_angle = 0.0
io_orbit_angle = 0.0
europa_orbit_angle = 0.0
ganymede_orbit_angle = 0.0
callisto_orbit_angle = 0.0
titan_orbit_angle = 0.0
titania_orbit_angle = 0.0
triton_orbit_angle = 0.0

# Sun glow parameters
SUN_GLOW_LAYERS = 5
SUN_GLOW_RADIUS = SUN_RADIUS * 1.5
SUN_GLOW_COLORS = [
    [1.0, 0.9, 0.7, 0.8],  # Inner glow (bright)
    [1.0, 0.8, 0.6, 0.6],
    [1.0, 0.7, 0.5, 0.4],
    [1.0, 0.6, 0.4, 0.2],
    [1.0, 0.5, 0.3, 0.1]   # Outer glow (faint)
]


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
material_shininess = 50.0              # Material shininess exponent

# Planet Materials (Ambient and Diffuse properties)
# Using lists [R, G, B, Alpha]
MAT_SUN = [1.0, 0.8, 0.0, 1.0] # Sun is emissive, but use color when lighting off
MAT_MERCURY = [0.6, 0.6, 0.6, 1.0] # Grey
MAT_VENUS = [0.8, 0.7, 0.5, 1.0] # Yellowish-brown
MAT_EARTH = [0.2, 0.4, 0.8, 1.0] # Blue/Green dominant
MAT_MARS = [0.8, 0.3, 0.1, 1.0] # Reddish
MAT_JUPITER = [0.7, 0.6, 0.4, 1.0] # Orangey-brown bands
MAT_SATURN = [0.8, 0.75, 0.6, 1.0] # Pale yellow
MAT_SATURN_RING = [0.8, 0.7, 0.6, 0.7]  # Pale gold color with some transparency
MAT_URANUS = [0.6, 0.8, 0.9, 1.0] # Pale blue/cyan
MAT_NEPTUNE = [0.3, 0.5, 0.9, 1.0] # Deeper blue

# For day/night smooth
earth_rotation_angle = 0.0  # Separate from orbit angle
EARTH_ROTATION_SPEED = 0.5  # Slower default rotation (degrees per frame)

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
    global ring_quadric
    print("Initializing Scene...")
    initialize_stars()
    initialize_asteroids()

    # Create quadric for Saturn's rings
    ring_quadric = gluNewQuadric()
    gluQuadricNormals(ring_quadric, GLU_SMOOTH)
    gluQuadricTexture(ring_quadric, GL_TRUE)  # Enable if adding textures later
    print("Initialization Complete.")

# --- Drawing Functions ---

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen using bitmap fonts."""
    viewport = glGetIntegerv(GL_VIEWPORT)
    win_width, win_height = viewport[2], viewport[3]

    # Convert to percentage-based positioning if needed
    x_pos = x
    y_pos = y

    glColor3f(1.0, 1.0, 1.0) # White text
    glWindowPos2f(x_pos, y_pos)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_earth():
    glPushMatrix()
    glRotatef(math.degrees(earth_orbit_angle), 0, 1, 0)  # Orbit around Sun
    glTranslatef(EARTH_ORBIT_RADIUS, 0, 0)
    
    # Use the separate rotation angle
    glRotatef(earth_rotation_angle, 0, 1, 0)  # Rotates around Earth's axis
    
    # Smoother day/night effect with more slices
    slices = 36  # Increased from your original 10
    stacks = 36  # Increased from your original 10
    
    for i in range(0, 180, 5):  # More frequent latitude bands (5° steps)
        glBegin(GL_QUAD_STRIP)
        for j in range(0, 360, 5):  # More frequent longitude bands (5° steps)
            # Vertex 1
            x = EARTH_RADIUS * math.sin(math.radians(i)) * math.cos(math.radians(j))
            y = EARTH_RADIUS * math.cos(math.radians(i))
            z = EARTH_RADIUS * math.sin(math.radians(i)) * math.sin(math.radians(j))
            
            # Simple day/night based on x position (sun is at 0,0,0)
            if x > 0:  # Day side
                glColor3f(0.2, 0.4, 0.8)  # Ocean blue
            else:      # Night side
                glColor3f(0.05, 0.05, 0.1)  # Dark blue
            
            glVertex3f(x, y, z)
            
            # Vertex 2 (next latitude)
            x = EARTH_RADIUS * math.sin(math.radians(i+5)) * math.cos(math.radians(j))
            y = EARTH_RADIUS * math.cos(math.radians(i+5))
            z = EARTH_RADIUS * math.sin(math.radians(i+5)) * math.sin(math.radians(j))
            
            if x > 0:
                glColor3f(0.2, 0.4, 0.8)
            else:
                glColor3f(0.05, 0.05, 0.1)
                
            glVertex3f(x, y, z)
        glEnd()
    glPopMatrix()



def draw_starfield():
    """Draws the starfield using GL_POINTS."""
    # Lighting is off globally due to removal of glEnable(GL_LIGHTING)
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0) # White stars
    for x, y, z in stars:
        glVertex3f(x, y, z)
    glEnd()
    # No need to re-enable lighting as it's removed globally

def draw_orbit_lines():
    """Draws circular orbit lines for each planet."""
    # Lighting is off globally due to removal of glEnable(GL_LIGHTING)
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
    # No need to re-enable lighting as it's removed globally

def draw_asteroid_belt():
    """Draws the asteroid belt using GL_POINTS."""
    # Asteroids are affected by lighting, so keep it enabled - BUT LIGHTING IS OFF GLOBALLY NOW
    # glPointSize(2) # Asteroids as small points - kept
    glBegin(GL_POINTS)
    for asteroid in asteroids:
        # Use the material color defined for the asteroid - glMaterialfv has no effect if lighting is off
        # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, asteroid["color"]) # This call does nothing without lighting
        # Instead, set color directly using glColor3f for visibility without lighting
        glColor3f(asteroid["color"][0], asteroid["color"][1], asteroid["color"][2])
        # Draw the asteroid at its current position
        glVertex3f(asteroid["x"], asteroid["y"], asteroid["z"])
    glEnd()


def draw_saturn_with_rings():
    """Draws Saturn with its rings."""
    glPushMatrix()  # Push 1 - Saturn's position

    # Position Saturn in its orbit
    glRotatef(math.degrees(saturn_orbit_angle), 0, 1, 0)
    glTranslatef(SATURN_ORBIT_RADIUS, 0, 0)

    # Draw Saturn
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_SATURN) # This call does nothing without lighting
    glColor4fv(MAT_SATURN) # Set color directly for visibility
    glutSolidSphere(SATURN_RADIUS, SPHERE_SLICES, SPHERE_STACKS)

    # Draw rings
    glPushMatrix()  # Push 2 - Rings position
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_SATURN_RING) # Does nothing without lighting
    glColor4fv(MAT_SATURN_RING) # Set color directly for visibility

    # Enable blending for transparent rings - REMOVED as per user request (glEnable)
    # glEnable(GL_BLEND) # REMOVED
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # This function call is also ineffective without blending enabled

    # Rotate rings to match Saturn's axial tilt (about 26.7 degrees)
    glRotatef(-26.7, 0, 0, 1)

    # Draw the ring using a disk
    glRotatef(90, 1, 0, 0)  # Rotate to lie in XZ plane
    gluDisk(ring_quadric, SATURN_RING_INNER, SATURN_RING_OUTER, RING_SLICES, RING_LOOPS)

    # glDisable(GL_BLEND) # REMOVED (was paired with glEnable)
    glPopMatrix()  # Pop 2 - Rings position

    # Draw Titan (moon)
    glPushMatrix()  # Push 3 - Moon position
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, TITAN_MATERIAL) # Does nothing without lighting
    glColor4fv(TITAN_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(titan_orbit_angle), 0, 1, 0)
    glTranslatef(TITAN_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(TITAN_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()  # Pop 3 - Moon position

    glPopMatrix()  # Pop 1 - Saturn's position



def draw_sun_with_glow():
    """Draws the sun with a soft glowing edge effect."""
    # glDisable(GL_LIGHTING) # REMOVED (was paired with glEnable)

    # Draw glow layers (from outer to inner)
    for i in range(SUN_GLOW_LAYERS):
        radius = SUN_GLOW_RADIUS * (1.0 - i/SUN_GLOW_LAYERS)
        alpha = SUN_GLOW_COLORS[i][3]
        color = SUN_GLOW_COLORS[i]

        glPushMatrix()
        glColor4fv(color) # glColor is used when lighting is off
        glutSolidSphere(radius, SPHERE_SLICES*2, SPHERE_STACKS*2)  # Higher resolution for smooth glow
        glPopMatrix()

    # Draw the core sun
    glPushMatrix()
    glColor4fv(MAT_SUN) # glColor is used when lighting is off
    glutSolidSphere(SUN_RADIUS, SPHERE_SLICES*2, SPHERE_STACKS*2)
    glPopMatrix()

    # glEnable(GL_LIGHTING) # REMOVED (was paired with glDisable)


def draw_solar_system():
    """Draws the Sun and planets with lighting and materials."""
    global earth_orbit_angle, mars_orbit_angle, jupiter_orbit_angle, saturn_orbit_angle
    global mercury_orbit_angle, venus_orbit_angle, uranus_orbit_angle, neptune_orbit_angle

    # --- Sun (Source of Light) ---
    draw_sun_with_glow() # Note: Sun will not act as a light source without lighting enabled

    # --- Mercury ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_MERCURY) # Does nothing without lighting
    glColor4fv(MAT_MERCURY) # Set color directly for visibility
    glRotatef(math.degrees(mercury_orbit_angle), 0, 1, 0) # Rotate orbit
    glTranslatef(MERCURY_ORBIT_RADIUS, 0, 0)
    # Add self-rotation here if desired
    glutSolidSphere(MERCURY_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Venus ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_VENUS) # Does nothing without lighting
    glColor4fv(MAT_VENUS) # Set color directly for visibility
    glRotatef(math.degrees(venus_orbit_angle), 0, 1, 0)
    glTranslatef(VENUS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(VENUS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # --- Earth ---
    # Earth is drawn with manual per-vertex coloring in draw_earth()
    draw_earth()

    # --- Mars ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_MARS) # Does nothing without lighting
    glColor4fv(MAT_MARS) # Set color directly for visibility
    glRotatef(math.degrees(mars_orbit_angle), 0, 1, 0)
    glTranslatef(MARS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(MARS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)

    # Phobos
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, PHOBOS_MATERIAL) # Does nothing without lighting
    glColor4fv(PHOBOS_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(phobos_orbit_angle), 0, 1, 0)
    glTranslatef(PHOBOS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(PHOBOS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # Deimos
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, DEIMOS_MATERIAL) # Does nothing without lighting
    glColor4fv(DEIMOS_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(deimos_orbit_angle), 0, 1, 0)
    glTranslatef(DEIMOS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(DEIMOS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    glPopMatrix()  # Mars

    # --- Jupiter ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_JUPITER) # Does nothing without lighting
    glColor4fv(MAT_JUPITER) # Set color directly for visibility
    glRotatef(math.degrees(jupiter_orbit_angle), 0, 1, 0)
    glTranslatef(JUPITER_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(JUPITER_RADIUS, SPHERE_SLICES, SPHERE_STACKS)

    # Io
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, IO_MATERIAL) # Does nothing without lighting
    glColor4fv(IO_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(io_orbit_angle), 0, 1, 0)
    glTranslatef(IO_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(IO_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # Europa
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, EUROPA_MATERIAL) # Does nothing without lighting
    glColor4fv(EUROPA_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(europa_orbit_angle), 0, 1, 0)
    glTranslatef(EUROPA_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(EUROPA_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # Ganymede
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, GANYMEDE_MATERIAL) # Does nothing without lighting
    glColor4fv(GANYMEDE_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(ganymede_orbit_angle), 0, 1, 0)
    glTranslatef(GANYMEDE_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(GANYMEDE_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    # Callisto
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, CALLISTO_MATERIAL) # Does nothing without lighting
    glColor4fv(CALLISTO_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(callisto_orbit_angle), 0, 1, 0)
    glTranslatef(CALLISTO_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(CALLISTO_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    glPopMatrix()  # Jupiter

    # --- Saturn ---
    draw_saturn_with_rings() # Note: Rings will not be transparent without blending enabled


    # --- Uranus ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_URANUS) # Does nothing without lighting
    glColor4fv(MAT_URANUS) # Set color directly for visibility
    glRotatef(math.degrees(uranus_orbit_angle), 0, 1, 0)
    glTranslatef(URANUS_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(URANUS_RADIUS, SPHERE_SLICES, SPHERE_STACKS)

    # Titania
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, TITANIA_MATERIAL) # Does nothing without lighting
    glColor4fv(TITANIA_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(titania_orbit_angle), 0, 1, 0)
    glTranslatef(TITANIA_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(TITANIA_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    glPopMatrix()  # Uranus

    # --- Neptune ---
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, MAT_NEPTUNE) # Does nothing without lighting
    glColor4fv(MAT_NEPTUNE) # Set color directly for visibility
    glRotatef(math.degrees(neptune_orbit_angle), 0, 1, 0)
    glTranslatef(NEPTUNE_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(NEPTUNE_RADIUS, SPHERE_SLICES, SPHERE_STACKS)

    # Triton
    glPushMatrix()
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, TRITON_MATERIAL) # Does nothing without lighting
    glColor4fv(TRITON_MATERIAL) # Set color directly for visibility
    glRotatef(math.degrees(triton_orbit_angle), 0, 1, 0)
    glTranslatef(TRITON_ORBIT_RADIUS, 0, 0)
    glutSolidSphere(TRITON_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()

    glPopMatrix()  # Neptune

# --- Setup Functions ---

def setup_lighting():
    """Configures OpenGL lighting. NOTE: Lighting will not be active without glEnable(GL_LIGHTING)."""
    # glEnable(GL_LIGHTING)      # REMOVED - Lighting calculations are off
    # glEnable(GL_LIGHT0)        # Enable light source 0 (the Sun) - This call does nothing without lighting enabled

    # Set light properties - These calls do nothing without lighting enabled
    glLightfv(GL_LIGHT0, GL_POSITION, sun_light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_light_diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, sun_light_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_light_specular) # Add specular component

    # Configure how light affects materials globally - These calls do nothing without lighting enabled
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE) # More realistic specular highlights

    # Set global material properties (can be overridden per object) - These calls do nothing without lighting enabled
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, material_shininess)

    # Enable normalization of normals (important for scaled objects, good practice) - REMOVED (glEnable)
    # glEnable(GL_NORMALIZE) # REMOVED
    # Use smooth shading for nicer visuals - glShadeModel affects rendering regardless of lighting
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
    global camera_pos, GRAVITY_FACTOR, EARTH_ROTATION_SPEED  # Add EARTH_ROTATION_SPEED here

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

    # Add these at the end of the function (before the redraw call):
    elif key == b'g':  # Increase gravity (faster orbits)
        GRAVITY_FACTOR = min(2.0, GRAVITY_FACTOR + GRAVITY_STEP)
    elif key == b'h':  # Decrease gravity (slower orbits)
        GRAVITY_FACTOR = max(0.1, GRAVITY_FACTOR - GRAVITY_STEP)


    elif key == b',':  # Slow down rotation
        EARTH_ROTATION_SPEED = max(0.1, EARTH_ROTATION_SPEED - 0.1)
    elif key == b'.':  # Speed up rotation
        EARTH_ROTATION_SPEED = min(5.0, EARTH_ROTATION_SPEED + 0.1)

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
    global earth_rotation_angle  # Add this with other globals
    global earth_orbit_angle, mars_orbit_angle, jupiter_orbit_angle, saturn_orbit_angle
    global mercury_orbit_angle, venus_orbit_angle, uranus_orbit_angle, neptune_orbit_angle
    global moon_orbit_angle, phobos_orbit_angle, deimos_orbit_angle
    global io_orbit_angle, europa_orbit_angle, ganymede_orbit_angle, callisto_orbit_angle
    global titan_orbit_angle, titania_orbit_angle, triton_orbit_angle

    # Update planet orbital angles
    earth_rotation_angle = (earth_rotation_angle + EARTH_ROTATION_SPEED * GRAVITY_FACTOR) % 360.0
    mercury_orbit_angle = (mercury_orbit_angle + MERCURY_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    venus_orbit_angle = (venus_orbit_angle + VENUS_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    earth_orbit_angle = (earth_orbit_angle + EARTH_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    mars_orbit_angle = (mars_orbit_angle + MARS_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    jupiter_orbit_angle = (jupiter_orbit_angle + JUPITER_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    saturn_orbit_angle = (saturn_orbit_angle + SATURN_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    uranus_orbit_angle = (uranus_orbit_angle + URANUS_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    neptune_orbit_angle = (neptune_orbit_angle + NEPTUNE_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)

    # Update moon orbits (also affected by gravity)
    moon_orbit_angle = (moon_orbit_angle + MOON_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    phobos_orbit_angle = (phobos_orbit_angle + PHOBOS_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    deimos_orbit_angle = (deimos_orbit_angle + DEIMOS_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    io_orbit_angle = (io_orbit_angle + IO_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    europa_orbit_angle = (europa_orbit_angle + EUROPA_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    ganymede_orbit_angle = (ganymede_orbit_angle + GANYMEDE_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    callisto_orbit_angle = (callisto_orbit_angle + CALLISTO_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    titan_orbit_angle = (titan_orbit_angle + TITAN_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    titania_orbit_angle = (titania_orbit_angle + TITANIA_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)
    triton_orbit_angle = (triton_orbit_angle + TRITON_ORBIT_SPEED * GRAVITY_FACTOR) % (2 * math.pi)

    # Update asteroid positions
    for asteroid in asteroids:
        asteroid["angle"] = (asteroid["angle"] + ASTEROID_ORBIT_SPEED * (ASTEROID_BELT_INNER_RADIUS / asteroid["distance"]) * GRAVITY_FACTOR) % (2 * math.pi)
        asteroid["x"] = asteroid["distance"] * math.cos(asteroid["angle"])
        asteroid["z"] = asteroid["distance"] * math.sin(asteroid["angle"])

    glutPostRedisplay()


# def reshape(width, height):
#     """Handle window resize events while maintaining aspect ratio"""
#     # Prevent division by zero
#     if height == 0:
#         height = 1
#     # Set viewport to cover the entire window
#     glViewport(0, 0, width, height)
#     # Set the aspect ratio of the clipping volume to match the viewport
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     # Calculate aspect ratio
#     aspect = float(width) / float(height)
#     # Adjust the field of view if needed to prevent distortion
#     adjusted_fov = FOV_Y
#     if aspect > 1.0:  # Wider than tall
#         adjusted_fov = FOV_Y / aspect
#     gluPerspective(adjusted_fov, aspect, NEAR_CLIP, FAR_CLIP)
#     glMatrixMode(GL_MODELVIEW)


def reshape(width, height):
    """Handle window resize while maintaining fixed aspect ratio"""
    # Calculate target aspect ratio (same as initial window)
    target_aspect = float(WINDOW_WIDTH) / float(WINDOW_HEIGHT)

    # Compute new viewport dimensions
    if width/height > target_aspect:
        # Window is wider than target - pillarbox
        new_width = int(height * target_aspect)
        glViewport((width - new_width)//2, 0, new_width, height)
    else:
        # Window is taller than target - letterbox
        new_height = int(width / target_aspect)
        glViewport(0, (height - new_height)//2, width, new_height)

    # Maintain original projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, target_aspect, NEAR_CLIP, FAR_CLIP)
    glMatrixMode(GL_MODELVIEW)


def display():
    """The main display function called by GLUT."""
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.0, 1.0) # Black background

    # Set up camera and lighting for this frame
    setupCamera()
    setup_lighting() # Note: Lighting is not active without glEnable(GL_LIGHTING)

    # Draw scene components
    draw_starfield()
    draw_orbit_lines()
    draw_asteroid_belt()
    draw_solar_system()

    # Get current viewport dimensions for text positioning
    viewport = glGetIntegerv(GL_VIEWPORT)
    win_width, win_height = viewport[2], viewport[3]

    # For text drawing - use fixed coordinates based on original window size
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # Fixed coordinates
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw your text using original coordinates
    # draw_text(10, WINDOW_HEIGHT-20, "Solar System Simulation") # Replaced by the line below

    # Update the text display to include gravity controls
    draw_text(10, win_height - 20, "Solar System Simulation - Gravity: {:.1f}x".format(GRAVITY_FACTOR))
    draw_text(10, 10, "WASDQE: Move | Z/X: Zoom | G/H: Change Gravity | ESC: Exit")

    # Restore previous states
    # glEnable(GL_DEPTH_TEST) # REMOVED (restoring feature that was removed)
    # glEnable(GL_LIGHTING) # REMOVED (restoring feature that was removed)
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
    # Request double buffering, RGB color, and depth buffer (depth buffer is requested but not enabled)
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

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT) # This seems redundant after the reshape function is registered

    glutReshapeFunc(reshape)

    print("Starting GLUT Main Loop...")
    glutMainLoop() # Start the event processing loop

if __name__ == "__main__":
    main()