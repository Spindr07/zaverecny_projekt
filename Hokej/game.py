import pygame
import sys
pygame.init()
window_width = 800
window_height = 1000
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Hokejové nájezdy")
sky_surface = pygame.Surface((window_width,window_height))
sky_surface.fill("white")
stredovka = pygame.Surface((800,10))
stredovka.fill("red")
puntiky = [(150,170),(650,170)]
postranni_kruhy = [(150,170),(650,170),]
ofsajd_lajna = pygame.Surface((800,10))
ofsajd_lajna.fill("blue")
brankova_lajna = pygame.Surface((800,5))
brankova_lajna.fill("red")
game_active = True
class Player(pygame.sprite.Sprite):
    def __init__(self, x = 100, y = 200):
        super().__init__()
        self.image = pygame.Surface((40,60))
        self.image.fill("Red")
        self.rect = self.image.get_rect(topright = (x,y))
        self.default_x = x
        self.default_y = y
        self.speed = 5
        self.direction = None
        self.position = (x,y)
        self.active = True
    def update(self, keys):
        if not self.active:
            return
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > window_width:
            self.rect.right = window_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > window_height:
            self.rect.bottom = window_height
class Puck(pygame.sprite.Sprite):
    def __init__(self, x = 100, y = 200,):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill("Black")
        self.rect = self.image.get_rect(topleft = (x,y))
        self.default_x = x
        self.default_y = y
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0
        self.stopped = False
        self.caught_by_goalie = False
        self.carried_by = None
        self.owner = None
        self.target_pos = None
        self.speed = 10
    def has_puck(self, player):
        if not self.in_motion and not self.caught_by_goalie:
            offset_x = 30
            offset_y = 10
            if player.direction == "left":
                self.rect.centerx = player.rect.centerx - offset_x
            elif player.direction == "right":
                self.rect.centerx = player.rect.centerx + offset_x
            else:
                self.rect.centerx = player.rect.centerx
            self.rect.centery = player.rect.centery + offset_y

    def update(self):
        if self.carried_by:
            self.rect.centerx = self.carried_by.rect.centerx
            self.rect.centery = self.carried_by.rect.centery + 10
            return
        if self.in_motion:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.speed_x *= 0.98
            self.speed_y *= 0.98
            if self.rect.left <= 0 or self.rect.right >= 800:
                self.speed_x *= -1
            if self.rect.top <= 0 or self.rect.bottom >= 1000:
                self.speed_y *= -1
            if abs(self.speed_x) < 0.1 and abs(self.speed_y) < 0.1:
                self.in_motion = False
                self.speed_x = 0
                self.speed_y = 0
                self.stopped = True
        if self.in_motion and self.target_pos:
        # Aktuální pozice jako float Vector2 (zachová subpixelovou přesnost)
            current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
            target = pygame.math.Vector2(self.target_pos)

            direction = target - current_pos
            distance = direction.length()

            if distance <= self.speed:
                self.rect.center = self.target_pos
                self.in_motion = False
                self.target_pos = None
            else:
                direction = direction.normalize()
                move_vector = direction * self.speed
                new_pos = current_pos + move_vector
                self.rect.center = (round(new_pos.x), round(new_pos.y))

        elif self.carried_by:
            self.rect.center = self.carried_by.rect.center
    def shot_puck(self, player, keys):
        if not self.in_motion:
            self.in_motion = True
            speed = 10
            dx = 0
            dy = 0
            if keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_s]:
                dy += 1
            if keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_d]:
                dx += 1
        # Pokud je alespoň nějaký směr, normalizuj a nastav rychlost
            if dx != 0 or dy != 0:
                length = (dx**2 + dy**2) ** 0.5
                self.speed_x = dx / length * speed
                self.speed_y = dy / length * speed
            else:
            # pokud nešla žádná klávesa, střela ve směru hráče
                if player.direction == "left":
                    self.speed_x = -speed
                    self.speed_y = 0
                elif player.direction == "right":
                    self.speed_x = speed
                    self.speed_y = 0
                else:
                    self.speed_x = 0
                    self.speed_y = -speed
    def reset(self):
        self.rect.topleft = (self.default_x, self.default_y)
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0

 
# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Hodiny
clock = pygame.time.Clock()

# Brankář
goalie_width, goalie_height = 60, 80
goalie_x = window_width // 2 - goalie_width // 2
goalie_y = 50
goalie_speed = 5
goalie_direction = 1  # 1 = doprava, -1 = doleva

# Puk (střela)
puck_radius = 15
puck_x = window_width // 2
puck_y = window_height - 50
puck_speed = 15
shooting = False

# Skóre
score = 0
attempts = 0
font = pygame.font.SysFont(None, 36)

def draw_goal():
    # Nakreslí bránu (jako obdélník nahoře)
    goal_rect = pygame.Rect(window_width//2 - 100, goalie_y - 10, 200, 10)
    pygame.draw.rect(screen, RED, goal_rect)

def reset_puck():
    global puck_x, puck_y, shooting
    puck_x = window_width // 2
    puck_y = window_height - 50
    shooting = False

def display_score():
    score_text = font.render(f"Skóre: {score} / Pokusy: {attempts}", True, BLACK)
    screen.blit(score_text, (10, window_height - 40))

player = pygame.sprite.GroupSingle() 
player.add(Player())
puck = pygame.sprite.GroupSingle()
puck.add(Puck())
while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not shooting:
                shooting = True
    screen.blit(sky_surface,(0,0)) 
    screen.blit(stredovka,(0,850))
    screen.blit(ofsajd_lajna,(0,600))
    screen.blit(brankova_lajna,(0,100))
    pygame.draw.circle(sky_surface, "blue", (400,857.5),50,5 )
    for q in puntiky:
        pygame.draw.circle(sky_surface, "red", q,5,)
    for w in postranni_kruhy:
        pygame.draw.circle(sky_surface, "red",w,50,5 )
    player.update(keys)
    player.draw(screen)
    puck.update()
    puck.draw(screen)
    goalie_x += goalie_speed * goalie_direction
    if goalie_x <= window_width//2 - 100:
        goalie_direction = 1
    elif goalie_x >= window_width//2 + 40:
        goalie_direction = -1
    
    # Nakreslení brankáře
    goalie_rect = pygame.Rect(goalie_x, goalie_y, goalie_width, goalie_height)
    pygame.draw.rect(screen, BLUE, goalie_rect)
    
    # Nakreslení brány
    draw_goal()
    
    # Pohyb puku
    if shooting:
        puck_y -= puck_speed
    
    # Nakreslení puku
    pygame.draw.circle(screen, BLACK, (puck_x, puck_y), puck_radius)
    
    # Kontrola kolize - jestli puk narazil do brankáře
    puck_rect = pygame.Rect(puck_x - puck_radius, puck_y - puck_radius, puck_radius*2, puck_radius*2)
    if puck_rect.colliderect(goalie_rect):
        attempts += 1
        reset_puck()
    
    # Kontrola, jestli puk prošel bránou (tedy pokud je nad brankářem a v bráně)
    if shooting and puck_y < goalie_y:
        attempts += 1
        # Brána je mezi x = WIDTH//2 - 100 a WIDTH//2 + 100
        if window_width//2 - 100 < puck_x < window_width//2 + 100:
            score += 1
        reset_puck()
    
    display_score()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
