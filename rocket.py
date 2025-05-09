# Imports
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math
import random

scene_mode = 0

# Add these new variables under the "Rocket state" section
repair_mode = False
broken_parts = []  # Stores positions of broken components
REPAIR_TIME = 15  # Seconds
repair_timer = 0
repair_progress = 0
REPAIR_ITEMS_NEEDED = 3
MAX_REPAIR_ITEMS = 3  # Maximum simultaneous repair items
REPAIR_SPAWN_INTERVAL = 2.0
last_repair_spawn = 0  # Time of last repair item spawn

# Add to the constants section
REPAIR_ITEM_RADIUS = 10.0
REPAIR_ITEM_COLOR = [0.0, 1.0, 0.0]  # Green
REPAIR_HUD_COLOR = [0.2, 0.8, 0.2]  # Green

mission_start_time = None  # Time when the mission starts
mission_complete = False  # Flag to indicate mission completion

mission_planet_pos = None  # Position of the mission planet
MISSION_PLANET_RADIUS = 50.0  # Radius of the mission planet
MISSION_PLANET_DISTANCE = 2000.0  # Distance in front of the rocket

meteors = []  # List to store meteor positions
MAX_METEORS = 80  # Maximum number of meteors
METEOR_SPAWN_DISTANCE = 2000  # Distance ahead of the rocket to spawn meteors
METEOR_RADIUS = 25.0  # Radius of meteors
rocket_health = 10  # Rocket's health points
game_over = False  # Game over state

stars_mode_1 = []  # List to store stars for scene mode 1
MAX_STARS = 60  # Maximum number of stars in front of the rocket
STAR_SPAWN_DISTANCE = 200  # Distance in front of the rocket to spawn stars
STAR_DESPAWN_DISTANCE = 10  # Distance behind the rocket to despawn stars

# Rocket state
rocket_pos = [0.0, 20.0, 175.0]  # Initial position (x, y, z)
rocket_velocity = [0.0, 0.0, 0.0]  # Velocity (x, y, z)
rocket_speed = 1  # Speed of the rocket
movement = 0.5
rocket_movement = {"w": True, "s": False, "a": False, "d": False, "q": False, "e": False}  # Movement state

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
# if scene_mode == 0:
#   camera_pos = [0.0, 40.0, EARTH_ORBIT_RADIUS + 60.0] # Start slightly further back
#   camera_target = [0.0, 0.0, 0.0] # Look at the origin (Sun)
# elif scene_mode == 1:
#   camera_pos = [rocket_pos[0], rocket_pos[1] + 20.0, rocket_pos[2] + 50.0]  # Start above and behind the rocket
#   camera_target = rocket_pos[:]  # Look at the rocket

# Camera for scene mode 0 (solar system)
camera_pos = [0.0, 40.0, EARTH_ORBIT_RADIUS + 60.0]
camera_target = [0.0, 0.0, 0.0]

# Camera for scene mode 1 (rocket mode)
camera_pos_mode_1 = [rocket_pos[0], rocket_pos[1] + 20 , rocket_pos[2] + 70]  # Start above and behind the rocket
camera_target_mode_1 = rocket_pos[:]

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

def generate_stars_mode_1():
    """Generates stars in front of the rocket."""
    global stars_mode_1

    while len(stars_mode_1) < MAX_STARS:
        # Generate random positions in front of the rocket
        x = rocket_pos[0] + random.uniform(-100, 100)  # Random x offset
        y = rocket_pos[1] + random.uniform(-100, 100)  # Random y offset
        z = rocket_pos[2] - random.uniform(0, STAR_SPAWN_DISTANCE)  # Random z offset in front of the rocket
        #z = rocket_pos[2] - random.uniform(STAR_SPAWN_DISTANCE - 50, STAR_SPAWN_DISTANCE)  # In front of the rocket

        stars_mode_1.append([x, y, z])  # Add the star to the list

def generate_meteors():
    """Generates meteors randomly ahead of the rocket."""
    global meteors

    while len(meteors) < MAX_METEORS:
        x = rocket_pos[0] + random.uniform(-1000, 1000)  # Random x offset
        y = rocket_pos[1] + random.uniform(-1000, 1000)  # Random y offset
        z = rocket_pos[2] - random.uniform(200, METEOR_SPAWN_DISTANCE)  # Random z offset ahead of the rocket
        meteors.append([x, y, z])

def generate_closer_meteors():
    """Generates meteors randomly ahead of the rocket."""
    global meteors

    while len(meteors) < 10:
        x = rocket_pos[0] + random.uniform(-50, 50)  # Random x offset
        y = rocket_pos[1] + random.uniform(-50, 50)  # Random y offset
        z = rocket_pos[2] - random.uniform(200, METEOR_SPAWN_DISTANCE)  # Random z offset ahead of the rocket
        meteors.append([x, y, z])

def generate_repair_items():
    """Generates repair items ahead of the rocket"""
    global broken_parts, last_repair_spawn
    
    current_time = time.time()
    if current_time - last_repair_spawn > REPAIR_SPAWN_INTERVAL:
        last_repair_spawn = current_time
        while len(broken_parts) < MAX_REPAIR_ITEMS:
            x = rocket_pos[0] + random.uniform(-150, 150)
            y = rocket_pos[1] + random.uniform(-150, 150)
            z = rocket_pos[2] - random.uniform(200, 800)
            broken_parts.append([x, y, z])

def start_repair_minigame():
    """Initialize repair game elements"""
    global repair_mode, repair_timer, repair_progress
    repair_mode = True
    repair_timer = time.time()
    repair_progress = 0
    broken_parts.clear()  # Start with empty list

# def start_repair_minigame():
#     """Initialize repair game elements"""
#     global repair_mode, broken_parts, repair_timer, repair_progress
#     repair_mode = True
#     repair_timer = time.time()
#     repair_progress = 0
    
#     # Spawn repair items using meteor-style positioning
#     broken_parts = []
#     for _ in range(REPAIR_ITEMS_NEEDED):
#         x = rocket_pos[0] + random.uniform(-50, 50)
#         y = rocket_pos[1] + random.uniform(-50, 50)
#         z = rocket_pos[2] - random.uniform(150, 300)  # Spawn in front of rocket
#         broken_parts.append([x, y, z])

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


# def draw_rocket():
#     global rocket_pos

#     glPushMatrix()
#     glTranslatef(*rocket_pos)  # Move to the rocket's position
#     glColor3f(0.0, 0.2, 0.9)  # Red color
#     glutSolidSphere(5.0, 20, 20)  # Rocket body (sphere for simplicity)
#     glTranslatef(0.0, 0.0, 10.0)  # Move down for the body
#     glColor3f(0.0, 0.0, 0.3)
#     glutSolidSphere(2.0, 20, 20)  # Rocket tip
#     glPopMatrix()

def draw_rocket():
    global rocket_pos

    glPushMatrix()
    glTranslatef(*rocket_pos)  # Position in world space
    
    # Rotate entire rocket model to face along Z-axis
    glRotatef(185, 1, 0, 0)  # Pivot model from Y-up to Z-forward
    
    # Main body (cylinder along Z-axis)
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glutSolidCylinder(2.5, 30.0, 32, 32)  # Height along Z-axis
    glPopMatrix()

    # Nose cone (front of rocket)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 30.0)  # Move to tip along Z-axis
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCone(2.5, 8.0, 32, 32)
    glPopMatrix()

    # Engine nozzle (base of rocket)
    glPushMatrix()
    glTranslatef(0.0, 0.0, -2.0)  # Behind main body
    glColor3f(0.3, 0.3, 0.3)
    glutSolidCylinder(3.0, 2.0, 32, 32)
    glPopMatrix()

    # Fins (radial placement around Z-axis)
    glColor3f(0.0, 0.5, 0.0)
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120, 0, 0, 1)  # Rotate around Z-axis
        glTranslatef(2.5, 0.0, 0.0)  # Offset from center
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        glVertex3f(0, 0, 8)
        glEnd()
        glPopMatrix()

    # Window (mid-body)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 22.0)  # Position along Z-axis
    glColor3f(0.0, 0.0, 1.0)
    glutSolidSphere(1.5, 32, 32)
    glPopMatrix()

    # Decorative stripes
    glColor3f(1.0, 0.5, 0.0)
    for z in [5.0, 15.0, 25.0]:  # Positions along Z-axis
        glPushMatrix()
        glTranslatef(0.0, 0.0, z)
        glutSolidTorus(0.2, 2.6, 16, 16)
        glPopMatrix()

    glPopMatrix()


def draw_stars_mode_1():
    """Draws stars for scene mode 1."""
    global stars_mode_1

    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)  # White stars

    for star in stars_mode_1:
        glVertex3f(star[0], star[1], star[2])  # Draw each star

    glEnd()

def draw_meteors():
    """Draws the meteors."""
    global meteors

    glColor3f(0.3, 0.1, 0.1)  # Red color for meteors
    for meteor in meteors:
        glPushMatrix()
        glTranslatef(*meteor)
        glutSolidSphere(METEOR_RADIUS, 20, 20)
        glPopMatrix()

def draw_mission_planet():
    """Draws the mission planet."""
    global mission_planet_pos

    if mission_planet_pos:
        glPushMatrix()
        glTranslatef(*mission_planet_pos)  # Position the planet
        glColor4f(0.8, 0.3, 0.1, 1.0)  # Blue color for the mission planet
        glutSolidSphere(MISSION_PLANET_RADIUS, 32, 32)  # Render the planet
        glPopMatrix()

# def draw_repair_items():
#     """Draw repair items using meteor visualization"""
#     glColor3f(REPAIR_ITEM_COLOR[0], REPAIR_ITEM_COLOR[1], REPAIR_ITEM_COLOR[2])  # Color for repair items
#     for part in broken_parts:
#         glPushMatrix()
#         glTranslatef(*part)
#         glutSolidSphere(REPAIR_ITEM_RADIUS, 20, 20)
#         glPopMatrix()

def draw_repair_items():
    """Draw complex animated repair items with multiple components"""
    current_time = time.time()
    
    for part in broken_parts:
        glPushMatrix()
        glTranslatef(*part)
        
        # Base pulsating sphere
        pulse = math.sin(current_time * 8) * 0.2 + 1.0
        glPushMatrix()
        glScalef(pulse, pulse, pulse)
        glColor3f(0.0, 1.0, 0.2)  # Bright green core
        glutSolidSphere(REPAIR_ITEM_RADIUS * 0.8, 32, 32)
        glPopMatrix()
        
        # Rotating inner cube
        glPushMatrix()
        glRotatef(current_time * 180, 1, 1, 0)  # Rotate on two axes
        glColor3f(0.8, 1.0, 0.8)  # Light green
        glutWireCube(REPAIR_ITEM_RADIUS * 1.2)
        glPopMatrix()
        
        # Outer wireframe sphere with phase-shifted pulse
        glPushMatrix()
        glScalef(1.2 + math.sin(current_time * 6) * 0.1, 
                1.2 + math.cos(current_time * 6) * 0.1, 
                1.2 + math.sin(current_time * 6) * 0.1)
        glColor3f(1.0, 0.6, 0.0)  # Orange glow
        glutWireSphere(REPAIR_ITEM_RADIUS * 1.3, 16, 16)
        glPopMatrix()
        
        # Floating particles around the item
        glPointSize(3)
        glBegin(GL_POINTS)
        glColor3f(0.4, 1.0, 0.4)  # Bright green particles
        for i in range(20):
            angle = math.radians(i * 18 + current_time * 180)
            radius = REPAIR_ITEM_RADIUS * 1.5
            x = radius * math.cos(angle) * math.sin(current_time * 4)
            y = radius * math.sin(angle) * math.sin(current_time * 4)
            z = radius * math.cos(current_time * 4)
            glVertex3f(x, y, z)
        glEnd()
        
        glPopMatrix()

def draw_repair_hud():
    """Show repair progress and timer"""
    # Timer bar
    elapsed = time.time() - repair_timer
    time_left = REPAIR_TIME - elapsed
    progress_width = (time_left/REPAIR_TIME) * 200
    
    glColor3f(*REPAIR_HUD_COLOR)
    glBegin(GL_QUADS)
    glVertex2f(50, WINDOW_HEIGHT-50)
    glVertex2f(50 + progress_width, WINDOW_HEIGHT-50)
    glVertex2f(50 + progress_width, WINDOW_HEIGHT-30)
    glVertex2f(50, WINDOW_HEIGHT-30)
    glEnd()
    
    # Progress text
    draw_text(50, WINDOW_HEIGHT-80, 
             f"Repairs: {repair_progress}/{REPAIR_ITEMS_NEEDED}")

def draw_game_over():
    """Displays the game over message."""
    draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "GAME OVER", font=GLUT_BITMAP_HELVETICA_18)
    draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 30, "Press ESC to Exit", font=GLUT_BITMAP_HELVETICA_18)


def check_repair_collision():
    """Meteor-style collision detection"""
    global repair_progress, broken_parts
    for part in broken_parts[:]:
        dx = rocket_pos[0] - part[0]
        dy = rocket_pos[1] - part[1]
        dz = rocket_pos[2] - part[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < REPAIR_ITEM_RADIUS + 15:  # Similar collision range to meteors
            repair_progress += 1
            broken_parts.remove(part)
  

def update_stars_mode_1():
    """Updates the stars for scene mode 1."""
    global stars_mode_1

    # Remove stars that are behind the rocket
    stars_mode_1 = [star for star in stars_mode_1 if star[2] < rocket_pos[2] - STAR_DESPAWN_DISTANCE]

    # Generate new stars to maintain the count
    generate_stars_mode_1()

def update_meteors():
    """Updates the meteors and removes those behind the rocket."""
    global meteors

    # Remove meteors that are behind the rocket
    meteors = [meteor for meteor in meteors if meteor[2] < rocket_pos[2] - STAR_DESPAWN_DISTANCE]

    # Generate new meteors to maintain the count
    generate_meteors()
    generate_closer_meteors()

def update_repair_items():
    """Updates repair items and removes old ones"""
    global broken_parts
    
    # Remove items behind the rocket
    broken_parts = [part for part in broken_parts if part[2] < rocket_pos[2] - STAR_DESPAWN_DISTANCE]
    
    # Generate new items
    generate_repair_items()

def check_collisions():
    """Checks for collisions between the rocket and meteors."""
    global rocket_health, game_over, repair_mode

    for meteor in meteors:
        distance = math.sqrt(
            (rocket_pos[0] - meteor[0])**2 +
            (rocket_pos[1] - meteor[1])**2 +
            (rocket_pos[2] - meteor[2])**2
        )
        if distance < METEOR_RADIUS:  # Collision threshold (rocket radius + meteor radius)
            rocket_health -= 1
            meteors.remove(meteor)  # Remove the meteor after collision
            if rocket_health <= -1:
                game_over = True
                break
    if rocket_health <= 3 and not repair_mode and not game_over:
        start_repair_minigame()

def check_mission_completion():
    """Checks if the rocket has reached the mission planet."""
    global mission_complete

    if mission_planet_pos:
        distance = math.sqrt(
            (rocket_pos[0] - mission_planet_pos[0])**2 +
            (rocket_pos[1] - mission_planet_pos[1])**2 +
            (rocket_pos[2] - mission_planet_pos[2])**2
        )
        if distance < MISSION_PLANET_RADIUS:  # Rocket has reached the planet
            mission_complete = True
            print("Mission Complete!")  # Debug message
            glutPostRedisplay()

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

# def setupCamera():
#     """Sets up the projection and modelview matrices for the camera."""
#     # Projection Matrix
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     gluPerspective(FOV_Y, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), NEAR_CLIP, FAR_CLIP)

#     # ModelView Matrix
#     glMatrixMode(GL_MODELVIEW)
#     glLoadIdentity()
#     cx, cy, cz = camera_pos
#     tx, ty, tz = camera_target
#     ux, uy, uz = camera_up
#     gluLookAt(cx, cy, cz, tx, ty, tz, ux, uy, uz)
def setupCamera():
    """Sets up the projection and modelview matrices for the camera."""
    global camera_pos, camera_target
    global camera_pos_mode_1, camera_target_mode_1

    # Select the appropriate camera position and target based on the scene mode
    if scene_mode == 0:
        cx, cy, cz = camera_pos
        tx, ty, tz = camera_target
    elif scene_mode == 1:
        cx, cy, cz = camera_pos_mode_1
        tx, ty, tz = camera_target_mode_1

    # Set up the camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), NEAR_CLIP, FAR_CLIP)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    ux, uy, uz = camera_up
    gluLookAt(cx, cy, cz, tx, ty, tz, ux, uy, uz)

# --- GLUT Callback Functions ---

def keyboardUpListener(key, x, y):
    global rocket_movement
    
    if scene_mode == 1:  # Rocket controls only in scene mode 1
      if key == b'w':  # Stop moving forward
          rocket_movement["q"] = False
      elif key == b's':  # Stop moving backward
          rocket_movement["e"] = False
      elif key == b'a':  # Stop moving left
          rocket_movement["a"] = False
      elif key == b'd':  # Stop moving right
          rocket_movement["d"] = False
    #   elif key == b'q':  # Stop moving up
    #       rocket_movement["w"] = False

def keyboardListener(key, x, y):
    """Handles standard keyboard input."""
    global camera_pos, GRAVITY_FACTOR, EARTH_ROTATION_SPEED,scene_mode,rocket_movement  # Add EARTH_ROTATION_SPEED here

    x_cam, y_cam, z_cam = camera_pos

    # Basic WASD for translation on X/Z plane, Q/E for up/down
    if scene_mode == 1:  # Rocket controls only in scene mode 1
        if key == b'w':  # Move forward
            rocket_movement["q"] = True
        elif key == b's':  # Move backward
            rocket_movement["e"] = True
        elif key == b'a':  # Move left
            rocket_movement["a"] = True
        elif key == b'd':  # Move right
            rocket_movement["d"] = True
        # elif key == b'q':  # Move up
        #     if rocket_movement["w"] == False:  # Only allow up movement if not moving forward
        #         rocket_movement["w"] = True
        #     elif rocket_movement["w"] == True:
        #         rocket_movement["w"] = False

    elif scene_mode == 0:
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

        # Add these at the end of the function (before the redraw call):
        elif key == b'g':  # Increase gravity (faster orbits)
            GRAVITY_FACTOR = min(2.0, GRAVITY_FACTOR + GRAVITY_STEP)
        elif key == b'h':  # Decrease gravity (slower orbits)
            GRAVITY_FACTOR = max(0.1, GRAVITY_FACTOR - GRAVITY_STEP)


        elif key == b',':  # Slow down rotation
            EARTH_ROTATION_SPEED = max(0.1, EARTH_ROTATION_SPEED - 0.1)
        elif key == b'.':  # Speed up rotation
            EARTH_ROTATION_SPEED = min(5.0, EARTH_ROTATION_SPEED + 0.1)

    if key == b'\x1b':  # Escape key
        glutLeaveMainLoop()
    elif key == b'p':  # Toggle scene mode
        scene_mode = 1 if scene_mode == 0 else 0  # Toggle between 0 and 1

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
    global scene_mode,rocket_pos,rocket_movement,rocket_velocity, camera_pos_mode_1, camera_target_mode_1, movement  # Add this to control scene mode
    global game_over, mission_complete, mission_start_time, mission_planet_pos, repair_mode, rocket_health
    # Only update orbits if scene_mode is 0 (full solar system)
    if scene_mode == 0:
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

        # Update moon orbits
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
    
    elif scene_mode == 1 and not game_over and not mission_complete:  # Rocket controls only in scene mode 1
        if rocket_movement["w"]:
            rocket_pos[2] -= rocket_speed  # Move forward
        if rocket_movement["s"]:
            rocket_pos[2] += rocket_speed  # Move backward
        if rocket_movement["a"]:
            rocket_pos[0] -= movement  # Move left
        if rocket_movement["d"]:
            rocket_pos[0] += movement  # Move right
        if rocket_movement["q"]:
            rocket_pos[1] += movement  # Move up
        if rocket_movement["e"]:
            rocket_pos[1] -= movement  # Move down
        if mission_start_time is None:
            mission_start_time = time.time() # Record the start time
        
        if not mission_complete:
            elapsed_time = time.time() - mission_start_time
            if elapsed_time >= 120 and mission_planet_pos is None:  # 2 minutes have passed
                mission_planet_pos = [
                    rocket_pos[0],  # Same x-coordinate as the rocket
                    rocket_pos[1],  # Same y-coordinate as the rocket
                    rocket_pos[2] - MISSION_PLANET_DISTANCE  # Far ahead of the rocket
                ]

    
        check_mission_completion()
        
        # Update camera to follow the rocket
        camera_target_mode_1 = rocket_pos[:]  # Camera looks at the rocket
        camera_pos_mode_1 = [rocket_pos[0], rocket_pos[1] + 05.0 , rocket_pos[2] + 50.0]  # Position camera above and behind the rocket

        update_stars_mode_1()
        update_meteors()
        check_collisions()
    
    if scene_mode == 1:
        if mission_complete or game_over:
            return
    if repair_mode:
        # Check timer
        update_repair_items()
        
        # Check timer
        if time.time() - repair_timer > REPAIR_TIME:
            repair_mode = False
            rocket_health = 0
            game_over = True
        
        # Check completion
        if repair_progress >= REPAIR_ITEMS_NEEDED:
            repair_mode = False
            rocket_health += 2
            if rocket_health > 10: 
                rocket_health = 10
        
        check_repair_collision()
        glutPostRedisplay()




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
    if scene_mode == 0:
        # Full solar system
        draw_starfield()
        draw_orbit_lines()
        draw_asteroid_belt()
        draw_solar_system()
    elif scene_mode == 1:
        draw_stars_mode_1()
        draw_rocket()
        draw_meteors()
        draw_mission_planet()
        # Draw health points
        draw_text(10, WINDOW_HEIGHT - 40, f"Number of hits it can take: {rocket_health}", font=GLUT_BITMAP_HELVETICA_18)
        if game_over:
            draw_game_over()
            return
        if repair_mode:
            draw_repair_items()
            draw_repair_hud()

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
    if scene_mode == 0:
        draw_text(10, win_height - 20, "Solar System Simulation - Gravity: {:.1f}x".format(GRAVITY_FACTOR))
        draw_text(10, 10, "WASDQE: Move | Z/X: Zoom | G/H: Change Gravity | ESC: Exit")
    if scene_mode == 1:
      if mission_complete:
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "MISSION COMPLETE!", font=GLUT_BITMAP_HELVETICA_18)
        draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 30, "Press ESC to Exit", font=GLUT_BITMAP_HELVETICA_18)
        
        # --- Add these lines to restore matrices BEFORE returning ---
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glutSwapBuffers()
        return  # Exit after restoring matrices

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
    glutKeyboardUpFunc(keyboardUpListener)
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