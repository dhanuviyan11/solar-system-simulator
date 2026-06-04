import pygame
import math
import random

pygame.init()

# Window
WIDTH, HEIGHT = 1400, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulator")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
JUPITER_COLOR=(210, 180, 140)

# Font
font = pygame.font.SysFont("Arial", 16)

# Background stars
stars = []
for _ in range(250):
    stars.append(
        (
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.randint(1, 3)
        )
    )

# Camera
camera_x = 0
camera_y = 0
zoom = 1
# Time controls
simulation_speed = 1
paused = False

class Planet:
    AU = 1
    G = 0.25
    TIMESTEP = 0.12

    def __init__(self, x, y, radius, color, mass, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = name
        self.orbit = []
        self.sun = False
        self.x_vel = 0
        self.y_vel = 0
        # Moon/orbit system
        self.angle = 0
        self.orbit_radius = 0
        self.orbit_speed = 0
        self.center_planet = None

    def draw(self, win):
        global camera_x, camera_y, zoom
        # Orbit trail
        orbit_points = []
        for point in self.orbit:
            x = (point[0] + camera_x) * zoom
            y = (point[1] + camera_y) * zoom
            orbit_points.append((x, y))
        if len(orbit_points) > 1:
            pygame.draw.lines(win, self.color, False, orbit_points, 2)
        # Planet rendering
        screen_x = (self.x + camera_x) * zoom
        screen_y = (self.y + camera_y) * zoom
        if self.name == "Jupiter":
            pygame.draw.circle(win, (230, 200, 160), (int(screen_x), int(screen_y)), max(1, int((self.radius)*zoom)))
        pygame.draw.circle(win, self.color, (int(screen_x), int(screen_y)), max(1, int(self.radius * zoom)))
        # Labels
        if self.name != "Asteroid":
            label = font.render(self.name, True, WHITE)
            win.blit(label, (screen_x + self.radius + 5, screen_y - self.radius))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        if distance == 0:
            return 0, 0
        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        # Moon orbit system
        if self.center_planet:
            self.angle += self.orbit_speed
            self.x = (self.center_planet.x + math.cos(self.angle) * self.orbit_radius)
            self.y = (self.center_planet.y + math.sin(self.angle) * self.orbit_radius)
            self.orbit.append((self.x, self.y))
            if len(self.orbit) > 300:
                self.orbit.pop(0)
            return
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            # Only orbit the Sun
            if not planet.sun:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))
        if len(self.orbit) > 500:
            self.orbit.pop(0)
class Asteroid(Planet):
    def __init__(self, x, y, radius, color, mass):
        super().__init__(x, y, radius, color, mass, "Asteroid")

def draw_window():
    WIN.fill(BLACK)
    # Stars
    for star in stars:
        pygame.draw.circle(WIN, WHITE, (star[0], star[1]), star[2])
    # Draw planets
    for planet in planets:
        planet.draw(WIN)
    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw(WIN)
    # HUD
    hud_text = [
        f"Zoom: {zoom:.2f}",
        f"Camera_x: {camera_x:.2f}",
        f"Camera_y: {camera_y:.2f}",
        f"FPS: {int(clock.get_fps())}",
        f"Simulation_speed: {simulation_speed}x",
        f"Paused: {paused}"
    ]
    for i, text in enumerate(hud_text):
        render = font.render(text, True, WHITE)
        WIN.blit(render, (10, 10 + i * 20))
    if selected_planet:
        panel_x=WIDTH-260
        panel_y=20
        pygame.draw.rect(WIN, (30, 30, 30), (panel_x, panel_y, 240, 180))
        info=[f"Name: {selected_planet.name}", f"Mass: {selected_planet.mass}", f"X: {selected_planet.x:.2f}", f"Y: {selected_planet.y:.2f}", f"X_vel: {selected_planet.x_vel:.2f}", f"Y_vel: {selected_planet.y_vel:.2f}"]
        for i, text in enumerate(info):
            render=font.render(text, True, WHITE)
            WIN.blit(render, (panel_x + 10, panel_y + 10 + i *20))
    pygame.display.update()

clock = pygame.time.Clock()
# Sun
sun = Planet(WIDTH // 2, HEIGHT // 2, 30, YELLOW, 5000, "Sun")
sun.sun = True

# Mercury
mercury = Planet(WIDTH // 2 - 120, HEIGHT // 2, 5, DARK_GREY, 5, "Mercury")
mercury.y_vel = -2.8

# Venus
venus = Planet(WIDTH // 2 - 180, HEIGHT // 2, 8, ORANGE, 8, "Venus")
venus.y_vel = -2.3

# Earth
earth = Planet(WIDTH // 2 - 260, HEIGHT // 2, 10, BLUE, 10, "Earth")
earth.y_vel = -1.9

# Moon
moon = Planet(earth.x - 25, earth.y, 3, WHITE, 1, "Moon")
moon.center_planet = earth
moon.orbit_radius = 25
moon.orbit_speed = 0.05

# Mars
mars = Planet(WIDTH // 2 - 340, HEIGHT // 2, 7, RED, 7, "Mars")
mars.y_vel = -1.6

# Jupiter
jupiter=Planet(WIDTH//520, HEIGHT//2, 18, JUPITER_COLOR, 250, "Jupiter")
jupiter.y_vel=-1.3

asteroids=[]
for _ in range(120):
    angle=random.uniform(0, 2*math.pi)
    distance=470
    x=sun.x + math.cos(angle) * distance
    y=sun.y + math.sin(angle) * distance
    asteroid=Asteroid(x, y, 2, DARK_GREY, 1)
    orbital_speed=random.uniform(1.22, 1.32)
    asteroid.x_vel=math.sin(angle) * orbital_speed
    asteroid.y_vel=-math.cos(angle) * orbital_speed
    asteroids.append(asteroid)

planets = [sun, mercury, venus, earth, moon, mars, jupiter]

selected_planet=None
follow_planet=None
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            # Pause
            if event.key == pygame.K_SPACE:
                paused = not paused
            # Faster simulation
            if event.key == pygame.K_UP:
                simulation_speed += 1
            # Slower simulation
            if event.key == pygame.K_DOWN:
                simulation_speed = max(1, simulation_speed - 1)
            if event.key == pygame.K_ESCAPE:
                follow_planet=None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y=pygame.mouse.get_pos()
            for planet in planets:
                screen_x = (planet.x + camera_x)*zoom
                screen_y = (planet.y + camera_y)*zoom
                distance=math.sqrt((mouse_x-screen_x)**2+(mouse_y-screen_y)**2)
                if distance<planet.radius*zoom:
                    selected_planet=planet
                    follow_planet=planet

    # Camera controls
    keys = pygame.key.get_pressed()
    camera_speed = 10 / zoom
    if keys[pygame.K_a]:
        camera_x += camera_speed
    if keys[pygame.K_d]:
        camera_x -= camera_speed
    if keys[pygame.K_w]:
        camera_y += camera_speed
    if keys[pygame.K_s]:
        camera_y -= camera_speed
    # Zoom controls
    if keys[pygame.K_q]:
        zoom *= 1.01
    if keys[pygame.K_e]:
        zoom /= 1.01
    # Physics updates
    if not paused:
        for _ in range(simulation_speed):
            for planet in planets:
                planet.update_position(planets)
            for asteroid in asteroids:
                asteroid.update_position([sun])
    if follow_planet:
        camera_x = WIDTH/2/zoom-follow_planet.x
        camera_y = HEIGHT/2/zoom-follow_planet.y
    draw_window()           
pygame.quit()