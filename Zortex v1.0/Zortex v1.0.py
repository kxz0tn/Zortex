import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption("Zortex")

clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 20)
ORANGE = (255, 140, 0)
YELLOW = (255, 220, 0)
BLUE = (60, 140, 255)
GRAY = (90, 90, 110)
DARK_GRAY = (40, 40, 50)
GREEN = (100, 255, 100)
CYAN = (100, 200, 255)
PURPLE = (180, 100, 255)
DARK_RED = (180, 40, 40)

# Fonts
title_font = pygame.font.Font(None, 180)
button_font = pygame.font.Font(None, 70)
small_font = pygame.font.Font(None, 36)
font = pygame.font.Font(None, 48)
big_font = pygame.font.Font(None, 100)
controls_font = pygame.font.Font(None, 44)

# ────────────────────────────────────────────────
# Particle for explosion
# ────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 12)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 45)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.97
        self.vy *= 0.97
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color[:3], alpha) if len(self.color) == 3 else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size * (self.life / self.max_life)))

particles = []

def create_explosion(x, y, color=YELLOW, count=30):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# ────────────────────────────────────────────────
# SPACESHIP
# ────────────────────────────────────────────────
class Spaceship:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.angle = -90
        self.speed = 0
        self.max_speed = 5.8
        self.acceleration = 0.20
        self.deceleration = 0.10
        self.rotation_speed = 6.0
        self.shoot_delay = 170
        self.last_shot = 0
        self.lives = 3
        self.radius = 24

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)

        if self.speed > 0:
            self.speed = max(self.speed - self.deceleration, 0)

        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

        self.x = self.x % SCREEN_WIDTH
        self.y = self.y % SCREEN_HEIGHT

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            rad = math.radians(self.angle)
            return Bullet(self.x, self.y, self.angle)
        return None

    def draw(self, surface):
        rad = math.radians(self.angle)
        points = [
            (self.x + 30 * math.cos(rad), self.y + 30 * math.sin(rad)),
            (self.x + 20 * math.cos(rad - 130), self.y + 20 * math.sin(rad - 130)),
            (self.x - 20 * math.cos(rad), self.y - 20 * math.sin(rad)),
            (self.x + 20 * math.cos(rad + 130), self.y + 20 * math.sin(rad + 130)),
        ]
        pygame.draw.polygon(surface, BLUE, points)
        pygame.draw.polygon(surface, CYAN, points, 3)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            flame_length = 30 + random.randint(-6, 8)
            flame_points = [
                (self.x - 12 * math.cos(rad), self.y - 12 * math.sin(rad)),
                (self.x - flame_length * math.cos(rad - 0.6), self.y - flame_length * math.sin(rad - 0.6)),
                (self.x - (flame_length + 8) * math.cos(rad), self.y - (flame_length + 8) * math.sin(rad)),
                (self.x - flame_length * math.cos(rad + 0.6), self.y - flame_length * math.sin(rad + 0.6)),
            ]
            pygame.draw.polygon(surface, ORANGE, flame_points)
            pygame.draw.polygon(surface, YELLOW, flame_points, 2)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 12
        self.life = 70
        rad = math.radians(angle)
        self.dx = self.speed * math.cos(rad)
        self.dy = self.speed * math.sin(rad)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
        return self.life > 0

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 5, 1)

class Asteroid:
    def __init__(self):
        self.size = random.randint(30, 58)
        self.x = random.choice([random.randint(-80, -20), random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 80)])
        self.y = random.randint(-50, SCREEN_HEIGHT + 50)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(0.8, 2.5)
        self.spin = random.uniform(-2.8, 2.8)
        self.points = self.generate_shape()

    def generate_shape(self):
        pts = []
        for i in range(10):
            ang = i * 36 + random.randint(-18, 18)
            r = self.size * random.uniform(0.68, 1.12)
            pts.append((r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))))
        return pts

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        self.angle += self.spin
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def draw(self, surface):
        translated = [(self.x + px, self.y + py) for px, py in self.points]
        pygame.draw.polygon(surface, GRAY, translated)
        pygame.draw.polygon(surface, DARK_GRAY, translated, 4)

    def collides_with(self, ox, oy, orad):
        return math.hypot(self.x - ox, self.y - oy) < self.size + orad

class Alien:
    def __init__(self):
        self.x = random.choice([0, SCREEN_WIDTH])
        self.y = random.randint(30, SCREEN_HEIGHT - 30)
        self.size = 28
        self.speed = 2.4
        self.shoot_delay = random.randint(1000, 2500)
        self.last_shot = 0

    def update(self, ship):
        dx = ship.x - self.x
        dy = ship.y - self.y
        dist = math.hypot(dx, dy) or 1
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return AlienBullet(self.x, self.y, ship.x, ship.y)
        return None

    def draw(self, surface):
        points = [
            (self.x, self.y - self.size * 1.15),
            (self.x - self.size * 0.9, self.y + self.size * 0.7),
            (self.x - self.size * 0.4, self.y + self.size * 1.0),
            (self.x + self.size * 0.4, self.y + self.size * 1.0),
            (self.x + self.size * 0.9, self.y + self.size * 0.7),
        ]
        pygame.draw.polygon(surface, RED, points)
        pygame.draw.polygon(surface, (180, 0, 0), points, 3)
        pygame.draw.circle(surface, YELLOW, (int(self.x - 9), int(self.y - 3)), 6)
        pygame.draw.circle(surface, YELLOW, (int(self.x + 9), int(self.y - 3)), 6)

class AlienBullet:
    def __init__(self, x, y, tx, ty):
        self.x = x
        self.y = y
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy) or 1
        self.dx = (dx / dist) * 8
        self.dy = (dy / dist) * 8
        self.life = 90

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
        return self.life > 0

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 90, 80), (int(self.x), int(self.y)), 6)

# Starfield
stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.3, 1.3))
         for _ in range(200)]

def draw_stars(offset_x, offset_y):
    for x, y, spd in stars:
        px = (x + offset_x * spd) % SCREEN_WIDTH
        py = (y + offset_y * spd) % SCREEN_HEIGHT
        pygame.draw.circle(screen, WHITE, (int(px), int(py)), 1 + int(spd * 1.2))

# ────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────
def main():
    global particles
    particles = []

    state = "menu"
    ship = None
    bullets = []
    asteroids = []
    aliens = []
    alien_bullets = []
    score = 0
    asteroid_timer = 0
    alien_timer = 0
    bg_offset_x = 0
    bg_offset_y = 0

    buckle_rect   = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 20,  400, 100)
    controls_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150, 400, 100)
    close_rect    = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 280, 400, 100)

    go_home_rect  = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 160, 400, 100)

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "playing":
                    if event.key == pygame.K_SPACE:
                        b = ship.shoot()
                        if b:
                            bullets.append(b)
                    if event.key == pygame.K_ESCAPE:
                        running = False

                elif state == "game_over":
                    if event.key == pygame.K_r:
                        ship = Spaceship()
                        bullets = []
                        asteroids = [Asteroid() for _ in range(5)]
                        aliens = []
                        alien_bullets = []
                        score = 0
                        asteroid_timer = 0
                        alien_timer = 0
                        bg_offset_x = 0
                        bg_offset_y = 0
                        state = "playing"
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if buckle_rect.collidepoint(event.pos):
                        state = "playing"
                        ship = Spaceship()
                        bullets = []
                        asteroids = [Asteroid() for _ in range(5)]
                        aliens = []
                        alien_bullets = []
                        score = 0
                        asteroid_timer = 0
                        alien_timer = 0
                        bg_offset_x = 0
                        bg_offset_y = 0
                    elif controls_rect.collidepoint(event.pos):
                        state = "controls"
                    elif close_rect.collidepoint(event.pos):
                        running = False

                elif state == "controls":
                    if go_home_rect.collidepoint(event.pos):
                        state = "menu"

        # Update particles
        particles = [p for p in particles if p.update()]

        screen.fill(BLACK)

        if state == "menu":
            title = title_font.render("Zortex", True, CYAN)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180)))

            buckle_text = button_font.render("Buckle up", True, WHITE)
            buckle_surf = pygame.Surface((buckle_rect.width, buckle_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(buckle_surf, (40, 100, 180, 220), buckle_surf.get_rect(), border_radius=15)
            pygame.draw.rect(buckle_surf, CYAN, buckle_surf.get_rect(), 5, border_radius=15)
            buckle_surf.blit(buckle_text, buckle_text.get_rect(center=buckle_surf.get_rect().center))
            screen.blit(buckle_surf, buckle_rect)

            controls_text = button_font.render("Controls", True, WHITE)
            controls_surf = pygame.Surface((controls_rect.width, controls_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(controls_surf, (120, 60, 180, 220), controls_surf.get_rect(), border_radius=15)
            pygame.draw.rect(controls_surf, PURPLE, controls_surf.get_rect(), 5, border_radius=15)
            controls_surf.blit(controls_text, controls_text.get_rect(center=controls_surf.get_rect().center))
            screen.blit(controls_surf, controls_rect)

            close_text = button_font.render("Close", True, WHITE)
            close_surf = pygame.Surface((close_rect.width, close_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(close_surf, (180, 40, 40, 220), close_surf.get_rect(), border_radius=15)
            pygame.draw.rect(close_surf, DARK_RED, close_surf.get_rect(), 5, border_radius=15)
            close_surf.blit(close_text, close_text.get_rect(center=close_surf.get_rect().center))
            screen.blit(close_surf, close_rect)

        elif state == "controls":
            title = title_font.render("Controls", True, PURPLE)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 140)))

            controls_list = [
                "Move / Rotate:          W / A / D   or   Left / Right Arrow",
                "Thrust forward:         W / Up Arrow",
                "Shoot:                  SPACE",
                "Quit game:              ESC (anytime during play)",
            ]

            y_pos = 300
            for line in controls_list:
                text = controls_font.render(line, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 80

            home_text = button_font.render("Go to Home", True, WHITE)
            home_surf = pygame.Surface((go_home_rect.width, go_home_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(home_surf, (40, 180, 80, 220), home_surf.get_rect(), border_radius=15)
            pygame.draw.rect(home_surf, GREEN, home_surf.get_rect(), 5, border_radius=15)
            home_surf.blit(home_text, home_text.get_rect(center=home_surf.get_rect().center))
            screen.blit(home_surf, go_home_rect)

        elif state == "playing":
            ship.update()

            bg_offset_x += ship.speed * math.cos(math.radians(ship.angle)) * 0.35
            bg_offset_y += ship.speed * math.sin(math.radians(ship.angle)) * 0.35

            asteroid_timer += dt
            if asteroid_timer > max(1300 - score//90, 550):
                asteroids.append(Asteroid())
                asteroid_timer = 0

            alien_timer += dt
            if alien_timer > max(11000 - score//60, 4500):
                aliens.append(Alien())
                alien_timer = 0

            for b in bullets[:]:
                if not b.update():
                    bullets.remove(b)

            for a in asteroids[:]:
                a.update()

            for al in aliens[:]:
                ab = al.update(ship)
                if ab:
                    alien_bullets.append(ab)

            for ab in alien_bullets[:]:
                if not ab.update():
                    alien_bullets.remove(ab)

            # Collisions - ship vs asteroid
            for a in asteroids[:]:
                if a.collides_with(ship.x, ship.y, ship.radius):
                    ship.lives -= 1
                    asteroids.remove(a)
                    create_explosion(a.x, a.y, ORANGE, 25)

            # Bullet vs asteroid / alien
            for b in bullets[:]:
                hit = False
                for a in asteroids[:]:
                    if a.collides_with(b.x, b.y, 4):
                        asteroids.remove(a)
                        bullets.remove(b)
                        score += 15
                        create_explosion(a.x, a.y, ORANGE, 35)
                        hit = True
                        break
                if not hit:
                    for al in aliens[:]:
                        if math.hypot(al.x - b.x, al.y - b.y) < al.size + 6:
                            aliens.remove(al)
                            bullets.remove(b)
                            score += 90
                            create_explosion(al.x, al.y, RED, 45)
                            break

            # Alien bullet / ram vs ship
            for ab in alien_bullets[:]:
                if math.hypot(ab.x - ship.x, ab.y - ship.y) < 22:
                    ship.lives -= 1
                    alien_bullets.remove(ab)
                    create_explosion(ship.x, ship.y, YELLOW, 20)

            for al in aliens[:]:
                if math.hypot(al.x - ship.x, al.y - ship.y) < al.size + ship.radius:
                    ship.lives -= 1
                    aliens.remove(al)
                    create_explosion(al.x, al.y, RED, 40)

            if ship.lives <= 0:
                state = "game_over"

            draw_stars(bg_offset_x, bg_offset_y)

            # Draw all objects
            ship.draw(screen)
            for p in particles:
                p.draw(screen)
            for b in bullets:
                b.draw(screen)
            for a in asteroids:
                a.draw(screen)
            for al in aliens:
                al.draw(screen)
            for ab in alien_bullets:
                ab.draw(screen)

            screen.blit(font.render(f"SCORE: {score}", True, WHITE), (30, 30))
            screen.blit(font.render(f"LIVES: {ship.lives}", True, GREEN), (30, 90))
            screen.blit(small_font.render("ESC to quit", True, (180, 180, 255)), (30, SCREEN_HEIGHT - 60))

        elif state == "game_over":
            draw_stars(bg_offset_x, bg_offset_y)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            go = big_font.render("GAME OVER", True, RED)
            screen.blit(go, go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100)))

            fs = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(fs, fs.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10)))

            restart_text = small_font.render("Press R to Restart   ESC to Quit", True, CYAN)
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Game crashed:", e)
        pygame.quit()
        sys.exit(1)