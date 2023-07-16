import pygame
import random
import math

# Fensterabmessungen
WIDTH = 800
HEIGHT = 600

# Farben
BLACK = (0, 0, 0)

# Initialisierung von Pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Fireworks")

clock = pygame.time.Clock()

class Pixel(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, size, color):
        super().__init__()
        self.image = pygame.Surface((size, size))  # Größe des Pixels anpassen
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.gravity = random.uniform(0.1, 0.3)  # Gravitation zwischen 0.1 und 0.3

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.speed_y += self.gravity

        if self.rect.y > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pixels = pygame.sprite.Group()
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        num_pixels = random.randint(40, 90)  # Anzahl der Pixel pro Explosion zwischen 40 und 90
        for _ in range(num_pixels):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 5)
            size = random.randint(2, 7)
            speed_x = math.sin(angle) * speed
            speed_y = math.cos(angle) * -speed
            pixel = Pixel(x, y, speed_x, speed_y, size, self.color)
            self.pixels.add(pixel)

    def update(self):
        self.pixels.update()
        if len(self.pixels) == 0:
            self.kill()

    def draw(self, surface):
        self.pixels.draw(surface)

explosions = pygame.sprite.Group()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if random.random() < 0.05:  # Wahrscheinlichkeit für den Start einer Explosion
        start_x = random.randint(0, WIDTH)
        start_y = random.randint(0, HEIGHT)
        explosion = Explosion(start_x, start_y)
        explosions.add(explosion)

    explosions.update()

    window.fill(BLACK)
    for explosion in explosions:
        explosion.draw(window)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
