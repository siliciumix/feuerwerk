import pygame
import random
import math

# ====================== EINSTELLUNGEN ======================
WIDTH, HEIGHT = 1000, 700
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistisches Feuerwerk - Verbesserte Version")
clock = pygame.time.Clock()

# ====================== KLASSEN ======================

class Particle:
    def __init__(self, x, y, vx, vy, color, size=5, life=70):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = 0.18
        self.friction = 0.975

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
        
        # Transparenz berechnen
        alpha = int(255 * (self.life / self.max_life))
        
        # Leicht ins Orange/Gelb verfärben beim Altern
        brightness = max(80, int(255 * (self.life / self.max_life)))
        r = min(255, self.color[0] + 40)
        g = min(brightness, self.color[1] + 20)
        b = max(30, self.color[2] - 30)
        
        # Haupt-Partikel
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((r, g, b, alpha))
        surface.blit(s, (int(self.x - self.size//2), int(self.y - self.size//2)))
        
        # Glow-Effekt (nur solange es noch relativ hell ist)
        if self.life > self.max_life * 0.35:
            glow_size = int(self.size * 2.8)
            glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int(70 * (self.life / self.max_life))
            pygame.draw.circle(glow, (*self.color, glow_alpha), (glow_size, glow_size), glow_size)
            surface.blit(glow, (int(self.x - glow_size), int(self.y - glow_size)))


class Rocket:
    def __init__(self, x):
        self.x = float(x)
        self.y = float(HEIGHT + 20)
        self.vy = random.uniform(-14.0, -10.0)
        self.color = (255, 240, 120)
        self.trail = []
        self.exploded = False

    def update(self):
        self.vy += 0.14
        self.y += self.vy
        
        # Trail aufbauen
        self.trail.append((self.x, self.y))
        if len(self.trail) > 25:
            self.trail.pop(0)

        # Explosion auslösen
        if self.vy >= -1.0 and not self.exploded:
            create_explosion(self.x, self.y, self.color)
            self.exploded = True

    def draw(self, surface):
        # Rauch- / Feuerschweif
        for i, (tx, ty) in enumerate(self.trail):
            progress = i / len(self.trail)
            alpha = int(180 * progress)
            size = int(3.5 * progress) + 2
            
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((240, 240, 200, alpha))
            surface.blit(s, (int(tx - size//2), int(ty - size//2)))
        
        # Rakete
        pygame.draw.rect(surface, self.color, 
                        (int(self.x - 2.5), int(self.y - 16), 5, 22))
        # Leuchtende Spitze
        pygame.draw.rect(surface, (255, 255, 200), 
                        (int(self.x - 1.5), int(self.y - 19), 3, 7))


class Explosion:
    def __init__(self, x, y, base_color):
        self.particles = []
        self.x = x
        self.y = y
        num_particles = random.randint(70, 120)
        
        for _ in range(num_particles):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(2.2, 7.5)
            size = random.randint(3, 8)
            life = random.randint(50, 90)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.0   # leichter Auftrieb
            
            # Farbvariation
            color = (
                min(255, base_color[0] + random.randint(-50, 50)),
                min(255, base_color[1] + random.randint(-40, 40)),
                min(255, base_color[2] + random.randint(-40, 60))
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


# ====================== GLOBALE LISTEN ======================
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
        
        # Mit Leertaste manuell Rakete starten
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                rockets.append(Rocket(random.randint(120, WIDTH - 120)))
            if event.key == pygame.K_r:      # Reset
                rockets.clear()
                explosions.clear()

    # Automatisches Feuerwerk
    if random.random() < 0.055:
        for _ in range(random.randint(1, 4)):
            rockets.append(Rocket(random.randint(80, WIDTH - 80)))

    # Update
    for rocket in rockets[:]:
        rocket.update()
        if rocket.exploded:
            rockets.remove(rocket)

    for explosion in explosions[:]:
        explosion.update()
        if not explosion.particles:
            explosions.remove(explosion)

    # Zeichnen
    screen.fill((4, 4, 18))        # Tiefer Nachthimmel

    # Raketen zeichnen
    for rocket in rockets:
        rocket.draw(screen)

    # Explosionen zeichnen
    for explosion in explosions:
        explosion.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()