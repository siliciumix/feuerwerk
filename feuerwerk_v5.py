import pygame
import random
import math

# ====================== EINSTELLUNGEN ======================
WIDTH, HEIGHT = 1000, 700
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buntes Realistisches Feuerwerk v6")
clock = pygame.time.Clock()

# Farbpalette für Raketen
ROCKET_COLORS = [
    (255, 50, 50),      # Rot
    (50, 255, 50),      # Grün
    (60, 140, 255),     # Blau
    (255, 80, 255),     # Pink
    (255, 215, 50),     # Gold
    (180, 50, 255),     # Lila
    (255, 130, 30),     # Orange
    (40, 255, 220),     # Türkis
    (255, 100, 180),    # Rosa
]

# ====================== KLASSEN ======================

class Particle:
    def __init__(self, x, y, vx, vy, color, size=5, life=75):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = tuple(max(0, min(255, int(c))) for c in color)  # Farbe sicher machen
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = 0.175
        self.friction = 0.978

    def update(self):
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return

        alpha = int(255 * (self.life / self.max_life))
        
        # Farbe leicht aufhellen / verändern
        r = min(255, self.color[0] + 35)
        g = min(255, self.color[1] + 20)
        b = max(40, self.color[2] - 25)

        # Haupt-Partikel
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((r, g, b, alpha))
        surface.blit(s, (int(self.x - self.size // 2), int(self.y - self.size // 2)))

        # Glow-Effekt
        if self.life > self.max_life * 0.35:
            glow_size = int(self.size * 2.7)
            glow_alpha = int(65 * (self.life / self.max_life))
            
            glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            # Sichere Farbe für Glow
            glow_color = (*self.color[:3], glow_alpha)
            pygame.draw.circle(glow, glow_color, (glow_size, glow_size), glow_size)
            surface.blit(glow, (int(self.x - glow_size), int(self.y - glow_size)))


class Rocket:
    def __init__(self, x):
        self.x = float(x)
        self.y = float(HEIGHT + 25)
        self.vy = random.uniform(-14.8, -10.8)
        self.color = random.choice(ROCKET_COLORS)
        self.trail = []
        self.exploded = False

    def update(self):
        self.vy += 0.15
        self.y += self.vy

        self.trail.append((self.x, self.y))
        if len(self.trail) > 27:
            self.trail.pop(0)

        if self.vy >= -1.0 and not self.exploded:
            create_explosion(self.x, self.y, self.color)
            self.exploded = True

    def draw(self, surface):
        # Rauchschweif
        for i, (tx, ty) in enumerate(self.trail):
            progress = i / len(self.trail)
            alpha = int(160 * progress)
            size = int(4.5 * progress) + 2

            trail_color = (min(255, self.color[0] + 50),
                          min(255, self.color[1] + 50),
                          min(255, self.color[2] + 50))

            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((*trail_color, alpha))
            surface.blit(s, (int(tx - size // 2), int(ty - size // 2)))

        # Rakete
        pygame.draw.rect(surface, self.color,
                        (int(self.x - 2.5), int(self.y - 18), 5, 25))
        # Leuchtende Spitze
        pygame.draw.rect(surface, (255, 255, 220),
                        (int(self.x - 1.5), int(self.y - 22), 3, 9))


class Explosion:
    def __init__(self, x, y, base_color):
        self.particles = []
        num = random.randint(80, 130)

        for _ in range(num):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(2.1, 8.0)
            size = random.randint(3, 8)
            life = random.randint(55, 95)

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.3

            # Farbvariation
            color = (
                base_color[0] + random.randint(-50, 55),
                base_color[1] + random.randint(-45, 50),
                base_color[2] + random.randint(-45, 70)
            )

            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


# ====================== LISTEN ======================
rockets = []
explosions = []

def create_explosion(x, y, base_color):
    explosions.append(Explosion(x, y, base_color))


# ====================== HAUPTSCHLEIFE ======================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                rockets.append(Rocket(random.randint(80, WIDTH - 80)))
            if event.key == pygame.K_r:          # Reset
                rockets.clear()
                explosions.clear()

    # Automatische Raketen
    if random.random() < 0.058:
        for _ in range(random.randint(1, 4)):
            rockets.append(Rocket(random.randint(70, WIDTH - 70)))

    # Update
    for rocket in rockets[:]:
        rocket.update()
        if rocket.exploded:
            rockets.remove(rocket)

    for explosion in explosions[:]:
        explosion.update()
        if len(explosion.particles) == 0:
            explosions.remove(explosion)

    # Zeichnen
    screen.fill((4, 4, 22))   # Dunkler Nachthimmel

    # Raketen zeichnen
    for rocket in rockets:
        rocket.draw(screen)

    # Explosionen zeichnen
    for explosion in explosions:
        explosion.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()