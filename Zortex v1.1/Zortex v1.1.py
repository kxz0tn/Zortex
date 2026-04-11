import pygame
import sys
import math
import random
from pygame import gfxdraw

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption("Zortex")

clock = pygame.time.Clock()
FPS = 60

# Colors
DEEP_PURPLE = (12, 6, 35)
NEON_CYAN = (0, 255, 240)
NEON_MAGENTA = (255, 20, 200)
NEON_PURPLE = (180, 0, 255)
NEON_BLUE = (0, 200, 255)
NEON_RED = (255, 60, 80)
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)

# Fonts
title_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.18))
button_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.055))
controls_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.042))
hud_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.045))
warning_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.06))

# ────────────────────────────────────────────────
# Particle System
# ────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 14)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(30, 65)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size < 1: return
        color = (*self.color[:3], alpha)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), size, color)

particles = []

def create_explosion(x, y, color=NEON_CYAN, count=45):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def create_nuke_explosion(x, y):
    create_explosion(x, y, NEON_CYAN, 140)
    create_explosion(x, y, NEON_MAGENTA, 100)

# ────────────────────────────────────────────────
# Nuke Missile
# ────────────────────────────────────────────────
class NukeMissile:
    def __init__(self, sx, sy, tx, ty, target_obj):
        self.x = sx
        self.y = sy
        self.tx = tx
        self.ty = ty
        self.target = target_obj
        dist = math.hypot(tx - sx, ty - sy) or 1
        self.speed = 19
        self.dx = (tx - sx) / dist * self.speed
        self.dy = (ty - sy) / dist * self.speed
        self.life = 130

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        return self.life > 0 and math.hypot(self.tx - self.x, self.ty - self.y) > 20

    def draw(self, surface):
        pygame.draw.line(surface, NEON_CYAN, (self.x - self.dx*4, self.y - self.dy*4), (self.x, self.y), 9)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), 11, NEON_MAGENTA)

# ────────────────────────────────────────────────
# Spaceship - No wrapping
# ────────────────────────────────────────────────
class Spaceship:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.angle = -90
        self.vx = 0
        self.vy = 0
        self.max_speed = 7.5
        self.acceleration = 0.28
        self.rotation_speed = 6.5
        self.shoot_delay = 155
        self.last_shot = 0
        self.lives = 3
        self.nukes = 3
        self.radius = 27

    def update(self):
        keys = pygame.key.get_pressed()
        rad = math.radians(self.angle)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vx += self.acceleration * math.cos(rad)
            self.vy += self.acceleration * math.sin(rad)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.rotation_speed

        self.vx *= 0.982
        self.vy *= 0.982

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = self.vx / speed * self.max_speed
            self.vy = self.vy / speed * self.max_speed

        self.x += self.vx
        self.y += self.vy

        # Clamp - no wrapping
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.x, self.y, self.angle)
        return None

    def draw(self, surface):
        rad = math.radians(self.angle)
        points = [
            (self.x + 35 * math.cos(rad), self.y + 35 * math.sin(rad)),
            (self.x + 24 * math.cos(rad - 2.35), self.y + 24 * math.sin(rad - 2.35)),
            (self.x - 24 * math.cos(rad), self.y - 24 * math.sin(rad)),
            (self.x + 24 * math.cos(rad + 2.35), self.y + 24 * math.sin(rad + 2.35))
        ]
        gfxdraw.filled_polygon(surface, points, NEON_BLUE)
        gfxdraw.aapolygon(surface, points, NEON_CYAN)

        if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
            flame_length = 40 + random.randint(-10, 12)
            fp = [(self.x -16*math.cos(rad), self.y -16*math.sin(rad)),
                  (self.x -flame_length*math.cos(rad-0.7), self.y -flame_length*math.sin(rad-0.7)),
                  (self.x -(flame_length+16)*math.cos(rad), self.y -(flame_length+16)*math.sin(rad)),
                  (self.x -flame_length*math.cos(rad+0.7), self.y -flame_length*math.sin(rad+0.7))]
            gfxdraw.filled_polygon(surface, fp, ORANGE)
            gfxdraw.aapolygon(surface, fp, NEON_CYAN)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 14
        self.life = 70
        rad = math.radians(angle)
        self.dx = self.speed * math.cos(rad)
        self.dy = self.speed * math.sin(rad)
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10: self.trail.pop(0)
        
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

        # IMPORTANT FIX: Bullets disappear when they go off top or bottom
        # Left and right still wrap (as per original game style)
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            return False  # Remove bullet

        self.x = self.x % SCREEN_WIDTH   # Only left/right wrap
        return self.life > 0

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            pygame.draw.circle(surface, (*NEON_CYAN[:3], int(140*(i/len(self.trail)))), (int(tx), int(ty)), 3)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), 6, NEON_MAGENTA)

# Asteroid, Alien, AlienBullet (unchanged)
class Asteroid:
    def __init__(self):
        self.size = random.randint(34, 65)
        self.x = random.choice([random.randint(-110, -40), random.randint(SCREEN_WIDTH + 40, SCREEN_WIDTH + 110)])
        self.y = random.randint(-80, SCREEN_HEIGHT + 80)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(1.1, 2.9)
        self.spin = random.uniform(-3.8, 3.8)
        self.points = [(self.size * random.uniform(0.65, 1.2) * math.cos(math.radians(i*30 + random.randint(-25,25))), 
                        self.size * random.uniform(0.65, 1.2) * math.sin(math.radians(i*30 + random.randint(-25,25)))) for i in range(12)]

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        self.angle += self.spin
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def draw(self, surface):
        translated = [(self.x + px, self.y + py) for px, py in self.points]
        gfxdraw.filled_polygon(surface, translated, (70, 70, 90))
        gfxdraw.aapolygon(surface, translated, NEON_CYAN)

    def collides_with(self, ox, oy, orad):
        return math.hypot(self.x - ox, self.y - oy) < self.size + orad

class Alien:
    def __init__(self):
        self.x = random.choice([0, SCREEN_WIDTH])
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.size = 31
        self.speed = 2.6
        self.shoot_delay = random.randint(1000, 2400)
        self.last_shot = 0

    def update(self, ship):
        dx = ship.x - self.x
        dy = ship.y - self.y
        dist = math.hypot(dx, dy) or 1
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
        if pygame.time.get_ticks() - self.last_shot > self.shoot_delay:
            self.last_shot = pygame.time.get_ticks()
            return AlienBullet(self.x, self.y, ship.x, ship.y)
        return None

    def draw(self, surface):
        points = [(self.x, self.y - self.size*1.25), (self.x - self.size*0.98, self.y + self.size*0.7),
                  (self.x - self.size*0.48, self.y + self.size*1.1), (self.x + self.size*0.48, self.y + self.size*1.1),
                  (self.x + self.size*0.98, self.y + self.size*0.7)]
        gfxdraw.filled_polygon(surface, points, NEON_RED)
        gfxdraw.aapolygon(surface, points, NEON_MAGENTA)
        gfxdraw.filled_circle(surface, int(self.x-11), int(self.y-6), 8, NEON_CYAN)
        gfxdraw.filled_circle(surface, int(self.x+11), int(self.y-6), 8, NEON_CYAN)

class AlienBullet:
    def __init__(self, x, y, tx, ty):
        self.x = x
        self.y = y
        dist = math.hypot(tx - x, ty - y) or 1
        self.dx = (tx - x) / dist * 9
        self.dy = (ty - y) / dist * 9
        self.life = 90

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT
        return self.life > 0

    def draw(self, surface):
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), 7, NEON_RED)

# Starfield
stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.25, 1.6)) for _ in range(280)]

def draw_stars(offset_x=0, offset_y=0):
    for x, y, spd in stars:
        px = (x + offset_x * spd) % SCREEN_WIDTH
        py = (y + offset_y * spd) % SCREEN_HEIGHT
        size = 2 if spd > 0.9 else 1
        pygame.draw.circle(screen, WHITE, (int(px), int(py)), size)

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
    nuke_missiles = []
    score = 0
    asteroid_timer = 0
    alien_timer = 0
    bg_offset_x = bg_offset_y = 0
    nuke_mode = False
    targeted = None
    show_out_of_nukes = 0

    # Buttons
    btn_w = int(SCREEN_WIDTH * 0.42)
    btn_h = int(SCREEN_HEIGHT * 0.09)
    start_y = int(SCREEN_HEIGHT * 0.48)

    buckle_rect   = pygame.Rect((SCREEN_WIDTH - btn_w)//2, start_y, btn_w, btn_h)
    controls_rect = pygame.Rect((SCREEN_WIDTH - btn_w)//2, start_y + int(btn_h*1.4), btn_w, btn_h)
    quit_rect     = pygame.Rect((SCREEN_WIDTH - btn_w)//2, start_y + int(btn_h*2.8), btn_w, btn_h)
    back_rect     = pygame.Rect((SCREEN_WIDTH - btn_w)//2, SCREEN_HEIGHT - int(SCREEN_HEIGHT*0.12), btn_w, int(btn_h*0.85))

    running = True
    pygame.mouse.set_visible(True)

    while running:
        dt = clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "playing":
                    if event.key == pygame.K_SPACE:
                        b = ship.shoot() if ship else None
                        if b: bullets.append(b)

                    if event.key == pygame.K_n:
                        if ship.nukes > 0:
                            nuke_mode = not nuke_mode
                            pygame.mouse.set_visible(not nuke_mode)
                            if not nuke_mode:
                                targeted = None
                        else:
                            show_out_of_nukes = 90

                    if event.key == pygame.K_l and nuke_mode and targeted and ship.nukes > 0:
                        nuke_missiles.append(NukeMissile(ship.x, ship.y, targeted.x, targeted.y, targeted))
                        ship.nukes -= 1
                        nuke_mode = False
                        pygame.mouse.set_visible(True)
                        targeted = None

                    if event.key == pygame.K_ESCAPE:
                        state = "menu"

                elif state == "game_over":
                    if event.key == pygame.K_r:
                        ship = Spaceship()
                        bullets.clear()
                        asteroids = [Asteroid() for _ in range(5)]
                        aliens.clear()
                        alien_bullets.clear()
                        nuke_missiles.clear()
                        score = 0
                        asteroid_timer = alien_timer = 0
                        state = "playing"
                    if event.key == pygame.K_q:
                        running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if buckle_rect.collidepoint(event.pos):
                        state = "playing"
                        ship = Spaceship()
                        bullets.clear()
                        asteroids = [Asteroid() for _ in range(5)]
                        aliens.clear()
                        alien_bullets.clear()
                        nuke_missiles.clear()
                        score = 0
                        asteroid_timer = alien_timer = 0
                        bg_offset_x = bg_offset_y = 0
                        nuke_mode = False
                        show_out_of_nukes = 0
                    elif controls_rect.collidepoint(event.pos):
                        state = "controls"
                    elif quit_rect.collidepoint(event.pos):
                        running = False
                elif state == "controls":
                    if back_rect.collidepoint(event.pos):
                        state = "menu"

        # Update
        particles = [p for p in particles if p.update()]

        for m in nuke_missiles[:]:
            if not m.update():
                create_nuke_explosion(m.x, m.y)
                if m.target:
                    if isinstance(m.target, Asteroid) and m.target in asteroids:
                        asteroids.remove(m.target)
                        score += 40
                    elif isinstance(m.target, Alien) and m.target in aliens:
                        aliens.remove(m.target)
                        score += 160
                nuke_missiles.remove(m)

        screen.fill(DEEP_PURPLE)
        draw_stars(bg_offset_x if state == "playing" else 0, bg_offset_y if state == "playing" else 0)

        if state == "menu":
            title = title_font.render("ZORTEX", True, NEON_CYAN)
            t_rect = title.get_rect(center=(SCREEN_WIDTH//2, int(SCREEN_HEIGHT*0.28)))
            screen.blit(title, t_rect)
            glow = title_font.render("ZORTEX", True, NEON_MAGENTA)
            glow.set_alpha(80)
            screen.blit(glow, glow.get_rect(center=t_rect.center))

            for rect, text, color in [
                (buckle_rect, "BUCKLE UP", NEON_CYAN),
                (controls_rect, "CONTROLS", NEON_PURPLE),
                (quit_rect, "QUIT", NEON_RED)
            ]:
                pygame.draw.rect(screen, (20, 10, 50), rect, border_radius=30)
                pygame.draw.rect(screen, color, rect, 8, border_radius=30)
                txt = button_font.render(text, True, WHITE)
                screen.blit(txt, txt.get_rect(center=rect.center))

        elif state == "controls":
            title = title_font.render("ZORTEX", True, NEON_CYAN)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, int(SCREEN_HEIGHT*0.12))))

            controls_list = [
                ("Rotate Ship", "A / D   or   Left arrow / Right arrow"),
                ("Thrust Forward", "W / Up arrow"),
                ("Fire Laser", "SPACE"),
                ("Activate Nuke Mode", "N   (3 nukes per game)"),
                ("Target & Launch Nuke", "Hover your mouse over the enemy and press L to launch"),
                ("Cancel Nuke Mode", "Press N again"),
                ("Return to Menu", "ESC")
            ]

            y = int(SCREEN_HEIGHT * 0.32)
            spacing = int(SCREEN_HEIGHT * 0.068)
            for label, key in controls_list:
                lbl = controls_font.render(label + ":", True, NEON_CYAN)
                ky = controls_font.render(key, True, WHITE)
                screen.blit(lbl, (SCREEN_WIDTH//2 - 420, y))
                screen.blit(ky, (SCREEN_WIDTH//2 + 80, y))
                y += spacing

            pygame.draw.rect(screen, (20, 10, 50), back_rect, border_radius=30)
            pygame.draw.rect(screen, NEON_CYAN, back_rect, 8, border_radius=30)
            back_txt = button_font.render("BACK TO MENU", True, WHITE)
            screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        elif state == "playing":
            if not ship: ship = Spaceship()
            ship.update()
            bg_offset_x += ship.vx * 0.5
            bg_offset_y += ship.vy * 0.5

            asteroid_timer += dt
            if asteroid_timer > max(1100 - score//100, 450):
                asteroids.append(Asteroid())
                asteroid_timer = 0
            alien_timer += dt
            if alien_timer > max(9800 - score//60, 3800):
                aliens.append(Alien())
                alien_timer = 0

            for b in bullets[:]:
                if not b.update(): bullets.remove(b)
            for a in asteroids[:]: a.update()
            for al in aliens[:]:
                ab = al.update(ship)
                if ab: alien_bullets.append(ab)
            for ab in alien_bullets[:]:
                if not ab.update(): alien_bullets.remove(ab)

            # Collisions
            for a in asteroids[:]:
                if a.collides_with(ship.x, ship.y, ship.radius):
                    ship.lives -= 1
                    asteroids.remove(a)
                    create_explosion(a.x, a.y, NEON_RED, 40)

            for b in bullets[:]:
                hit = False
                for a in asteroids[:]:
                    if a.collides_with(b.x, b.y, 7):
                        asteroids.remove(a)
                        bullets.remove(b)
                        score += 15
                        create_explosion(a.x, a.y, ORANGE, 42)
                        hit = True
                        break
                if not hit:
                    for al in aliens[:]:
                        if math.hypot(al.x - b.x, al.y - b.y) < al.size + 9:
                            aliens.remove(al)
                            bullets.remove(b)
                            score += 90
                            create_explosion(al.x, al.y, NEON_RED, 55)
                            break

            for ab in alien_bullets[:]:
                if math.hypot(ab.x - ship.x, ab.y - ship.y) < 26:
                    ship.lives -= 1
                    alien_bullets.remove(ab)
                    create_explosion(ship.x, ship.y, NEON_CYAN, 30)

            for al in aliens[:]:
                if math.hypot(al.x - ship.x, al.y - ship.y) < al.size + ship.radius:
                    ship.lives -= 1
                    aliens.remove(al)
                    create_explosion(al.x, al.y, NEON_RED, 50)

            if ship.lives <= 0:
                state = "game_over"

            # Nuke Targeting
            targeted = None
            if nuke_mode:
                mx, my = mouse_pos
                for obj in asteroids + aliens:
                    dist = math.hypot(obj.x - mx, obj.y - my)
                    if dist < getattr(obj, 'size', 40) + 70:
                        targeted = obj
                        break

            ship.draw(screen)
            for p in particles: p.draw(screen)
            for b in bullets: b.draw(screen)
            for a in asteroids: a.draw(screen)
            for al in aliens: al.draw(screen)
            for ab in alien_bullets: ab.draw(screen)
            for m in nuke_missiles: m.draw(screen)

            if nuke_mode:
                mx, my = mouse_pos
                col = NEON_RED if targeted else NEON_CYAN
                pygame.draw.circle(screen, col, (mx, my), 36, 5)
                pygame.draw.line(screen, col, (mx-45, my), (mx+45, my), 4)
                pygame.draw.line(screen, col, (mx, my-45), (mx, my+45), 4)

            # HUD
            score_text = hud_font.render(f"SCORE {score:06d}", True, NEON_CYAN)
            lives_text = hud_font.render(f"LIVES {ship.lives}", True, NEON_RED)
            nukes_text = hud_font.render(f"NUKES {ship.nukes}", True, NEON_PURPLE)
            screen.blit(score_text, (50, 40))
            screen.blit(lives_text, (50, 100))
            screen.blit(nukes_text, (50, 160))

            if show_out_of_nukes > 0:
                warning = warning_font.render("OUT OF NUKES!", True, NEON_RED)
                screen.blit(warning, warning.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)))
                show_out_of_nukes -= 1

        elif state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            screen.blit(overlay, (0, 0))

            go = title_font.render("GAME OVER", True, NEON_RED)
            screen.blit(go, go.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140)))

            fs = hud_font.render(f"FINAL SCORE: {score:06d}", True, WHITE)
            screen.blit(fs, fs.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))

            restart = controls_font.render("Press R to Restart", True, NEON_CYAN)
            quit_text = controls_font.render("Press Q to Quit", True, NEON_RED)
            screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80)))
            screen.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
