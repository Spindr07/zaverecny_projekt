import pygame
import math
pygame.init()
window_width = 800
window_height = 1000
end_surface = pygame.Surface((window_width,window_height))
end_surface.fill("white")
sky_surface = pygame.Surface((window_width,window_height))
sky_surface.fill("white")
stredovka = pygame.Surface((800,10))
stredovka.fill("red")
puntiky = [(150,366),(150,633),(650,366),(650,633),(150,170),(150,830),(650,170),(650,830)]
postranni_kruhy = [(150,170),(150,830),(650,170),(650,830)]
ofsajd_lajna = pygame.Surface((800,10))
ofsajd_lajna.fill("blue")
brankova_lajna = pygame.Surface((800,5))
brankova_lajna.fill("red")
pygame.display.set_caption("Hokejový zápas") 
game_active = True
has_puck = True
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

class Goalkeeper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill("Gray")
        self.rect = self.image.get_rect(center=(400, 120))
        self.speed = 2
        self.direction = 1
        self.has_puck = False
        self.hold_timer = 0
    def update(self):
        self.rect.x += self.speed * self.direction
        puck_x = puck.sprite.rect.centerx
        if abs(puck_x - self.rect.centerx) > 5:  
            if puck_x > self.rect.centerx:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
        if self.rect.left < 300:
            self.rect.left = 300
        if self.rect.right > 500:
            self.rect.right = 500
        if self.rect.left <= 300 or self.rect.right >= 500:
            self.direction *= -1
        if self.rect.colliderect(puck.sprite.rect) and puck.sprite.in_motion:
            self.catch_puck()
        if not self.has_puck:
            if self.rect.colliderect(puck.sprite.rect) and puck.sprite.in_motion and not puck.sprite.caught_by_goalie:
                self.catch_puck()
        else:
            self.hold_timer += 1
            puck.sprite.rect.center = (self.rect.centerx, self.rect.bottom + 5)
            if self.hold_timer >= 60:
                self.release_puck()
    def catch_puck(self):
        self.has_puck = True
        puck.sprite.in_motion = False
        puck.sprite.caught_by_goalie = True
        self.hold_timer = 0
        puck.sprite.speed_x = 0
        puck.sprite.speed_y = 0
    def release_puck(self):
        self.has_puck = False
        puck.sprite.caught_by_goalie = False
        puck.sprite.in_motion = True
        puck.sprite.speed_x = 0
        puck.sprite.speed_y = 8  
        self.hold_timer = 0
class Teammate(pygame.sprite.Sprite):
    def __init__(self, x, y, role="attacker"):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill("Green")
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.role = role 
        self.direction = 1
        self.has_puck = False
        self.pass_cooldown = 0
    def update(self, puck_rect, teammates_group, puck_obj):
        if self.rect.colliderect(puck_rect.inflate(20, 20)):
            self.has_puck = True
            puck.carried_by = self
        else:
            if puck_obj.carried_by == self:
                puck.carried_by = None
            self.has_puck = False
        if self.role == "attacker":
            if puck_rect.centery < self.rect.centery:
                self.rect.y -= self.speed
            elif puck_rect.centery > self.rect.centery:
                self.rect.y += self.speed
            self.rect.x += self.direction * self.speed
            if self.rect.left <= 100 or self.rect.right >= 700:
                self.direction *= -1
        elif self.role == "defender":
            if puck_rect.centery < 500:
                if self.rect.centery > 600:
                    self.rect.y -= self.speed
            else:
                if self.rect.centery < 800:
                    self.rect.y += self.speed
        if self.has_puck:
            if self.pass_cooldown <= 0:
                self.pass_puck(teammates_group, puck)
                self.pass_cooldown = 120
            else:
                self.pass_cooldown -= 1
        if self.rect.colliderect(puck_rect) and puck.in_motion:
            puck.sprite.carried_by = self
            puck.sprite.in_motion = False
            
    def pass_puck(self, teammates_group, puck):
        closest_teammate = None
        min_distance = float('inf')
        for mate in teammates_group:
            if mate == self:
                continue
            dist = ((mate.rect.centerx - self.rect.centerx) ** 2 + (mate.rect.centery - self.rect.centery) ** 2) ** 0.5
            if dist < min_distance:
                min_distance = dist
                closest_teammate = mate
        if closest_teammate:
            dx = closest_teammate.rect.centerx - self.rect.centerx
            dy = closest_teammate.rect.centery - self.rect.centery
            length = (dx**2 + dy**2) ** 0.5
            speed = 10
            puck.in_motion = True
            puck.speed_x = dx / length * speed
            puck.speed_y = dy / length * speed
            puck.carried_by = None
            self.has_puck = False
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, role="forward"):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill("Blue")
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 3
        self.role = role
        self.start_x = x
        self.start_y = y

    def update(self, puck):
        if self.role == "forward":
            if puck.rect.x > 400:
                self.move_towards(puck.rect.x, puck.rect.y)
            else:
                self.move_towards(self.start_x, self.start_y)

        elif self.role == "defense":
            if puck.rect.x < 400:
                self.move_towards(puck.rect.x, puck.rect.y)
            else:
                self.move_towards(self.start_x, self.start_y)
        
    def move_towards(self, target_x, target_y):
        if abs(self.rect.x - target_x) > 5:
            self.rect.x += self.speed if self.rect.x < target_x else -self.speed
        if abs(self.rect.y - target_y) > 5:
            self.rect.y += self.speed if self.rect.y < target_y else -self.speed
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
    def pass_puck_to(self, target_pos):
        self.target_pos = target_pos
        self.in_motion = True
        self.carried_by = None
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
    def pick_up(self, player):
        if not self.in_motion and not self.caught_by_goalie:
            self.carried_by = player
    def attach_to(self, player):
        self.in_motion = False
        self.owner = player
        offset_x = 30
        offset_y = 10
        if hasattr(player, 'direction'):
            if player.direction == "left":
                self.rect.centerx = player.rect.centerx - offset_x
            elif player.direction == "right":
                self.rect.centerx = player.rect.centerx + offset_x
            else:
                self.rect.centerx = player.rect.centerx
        else:
            self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery + offset_y
    def pass_to_teammate(self, player, teammates):
        if self.in_motion or self.caught_by_goalie:
            return
        closest = None
        min_dist = float('inf')
        for mate in teammates:
            dist = ((mate.rect.centerx - player.rect.centerx) ** 2 + (mate.rect.centery - player.rect.centery) ** 2) ** 0.5
            if dist < min_dist:
                closest = mate
                min_dist = dist
        if closest:
            self.in_motion = True
            dx = closest.rect.centerx - player.rect.centerx
            dy = closest.rect.centery - player.rect.centery
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                return
            speed = 8
            self.speed_x = speed * dx / length
            self.speed_y = speed * dy / length
class Goal(pygame.sprite.Sprite):
    def __init__(self, a = 390, b = 90,):
        super().__init__()
        self.image = pygame.Surface((20,10))
        self.image.fill("Black")
        self.rect =  self.image.get_rect()
        self.rect.topleft = (a, b)
        

def check_goal_collision():
    if puck.sprite.rect.colliderect(goal.sprite.rect):
        if puck.sprite.speed_y < 0 and puck.sprite.rect.bottom <= goal.sprite.rect.bottom + 5:
            print("GÓL DO HORNÍ BRANKY!")
            puck.sprite.reset()
            return 'away'
    if puck.sprite.rect.colliderect(goal2.sprite.rect):
        if puck.sprite.speed_y > 0 and puck.sprite.rect.top >= goal2.sprite.rect.top - 5:
            print("GÓL DO DOLNÍ BRANKY!")
            puck.sprite.reset()
            return 'home'
    return None


goalkeeper = pygame.sprite.GroupSingle()
goalkeeper.add(Goalkeeper())
puck = pygame.sprite.GroupSingle()
puck.add(Puck())
enemies = pygame.sprite.Group()
enemies.add(Enemy(300, 300, "forward"))
enemies.add(Enemy(400, 400, "forward"))
enemies.add(Enemy(500, 500, "forward"))
enemies.add(Enemy(250, 250, "defense"))
enemies.add(Enemy(550, 250, "defense"))
teammates = pygame.sprite.Group()
teammates.add(Teammate(200, 800, role="attacker"))
teammates.add(Teammate(600, 800, role="attacker"))
teammates.add(Teammate(250, 900, role="defender"))
teammates.add(Teammate(550, 900, role="defender"))
player = pygame.sprite.GroupSingle() 
player.add(Player()) 
goal = pygame.sprite.GroupSingle()
goal.add(Goal())
goal2 = pygame.sprite.GroupSingle()
goal2.add(Goal(390,905))
screen = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
offset_x = 20
offset_y = 10
score = 0
home_score = 0
away_score = 0
frame = 0
time = 0
score_font = pygame.font.SysFont("arial", 40)
time_font = pygame.font.SysFont("arial", 40)
title_font = pygame.font.SysFont("arial", 40)
prompt_font = pygame.font.SysFont("arial", 40)
game_state = "menu"
pohar = pygame.image.load("pohar.png")
pohar= pygame.transform.scale(pohar, (100,100))
game_state = "menu"
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit() 
        if not game_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                time = 0
                frame = 0
                game_state = "menu"
                game_active = True
        if game_state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "hra"
                frame = 0
                time = 0
                game_active = True
        elif game_state == "hra":
            if not game_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    frame = 0
                    time = 0
                    game_active = True
                    print("Restart")
    if game_state == "menu":
        screen.fill("white")
        title_surface = title_font.render(f"Hokejový zápas", True, "Black")
        prompt_surface = prompt_font.render(f"Stiskněte enter", True, "Black")
        WSAD_surface = prompt_font.render(f"WSAD = ovládání", True, "Black")
        SPACE_surface = prompt_font.render(f"SPACE = střela", True, "Black")
        screen.blit(title_surface, (window_width//2 - title_surface.get_width()//2, 200))
        screen.blit(prompt_surface, (window_width//2 - prompt_surface.get_width()//2, 300))
        screen.blit(WSAD_surface, (window_width//2 - prompt_surface.get_width()//2, 400))
        screen.blit(SPACE_surface, (window_width//2 - prompt_surface.get_width()//2, 500))
    if game_state == "hra":
        if game_active:
            keys = pygame.key.get_pressed()
            screen.blit(sky_surface,(0,0)) 
            screen.blit(stredovka,(0,495))
            screen.blit(ofsajd_lajna,(0,666))
            screen.blit(ofsajd_lajna,(0,333))
            screen.blit(brankova_lajna,(0,100))
            screen.blit(brankova_lajna,(0,900))
            pygame.draw.circle(sky_surface, "blue", (400, 500), 50, 5)
            pygame.draw.circle(sky_surface, "blue", (400,500),5 )
            for q in puntiky:
                pygame.draw.circle(sky_surface, "red", q,5,)
            for w in postranni_kruhy:
                pygame.draw.circle(sky_surface, "red",w,50,5 )
            player.update(keys)
            player.draw(screen)
            frame += 1
            time = frame // 60
            enemies.update(puck.sprite)
            enemies.draw(screen)
            teammates.update(puck.sprite.rect, teammates, puck.sprite)
            teammates.draw(screen)
            puck.sprite.update()
            puck.draw(screen)
            if check_goal_collision():
                goal_result = check_goal_collision()
                if goal_result == 'home':
                    home_score += 1
                elif goal_result == 'away':
                    away_score += 1
            if player.sprite.rect.colliderect(puck.sprite.rect):
                puck.sprite.in_motion = False
                puck.sprite.speed_x = 0
                puck.sprite.speed_y = 0
                puck.sprite.has_puck(player.sprite)
            if not puck.sprite.in_motion and not puck.sprite.caught_by_goalie:
                puck.sprite.has_puck(player.sprite)
            goal.update()
            goal.draw(screen)
            goal2.update()
            goal2.draw(screen)
            goalkeeper.update()
            goalkeeper.draw(screen)
            if time == 1000:
                print("Konec")
                game_active = False
            score_surface = score_font.render(f"Skóre: {score}", True, "Black")
            home_surface = score_font.render(f"Domácí: {home_score}", True, "Black")
            away_surface = score_font.render(f"{away_score} :Hosté", True, "Black")
            screen.blit(home_surface, (250, 20))
            screen.blit(away_surface, (410, 20))
            time_surface = time_font.render(f"čas: {time}", True, "Black")
            time_rect = time_surface.get_rect(topright=(200,200))
            screen.blit(time_surface, time_rect)
            if keys[pygame.K_e]:
                puck.sprite.shot_puck(player.sprite, keys)
            if keys[pygame.K_q] and not puck.sprite.in_motion:
                nearest_teammate = min(teammates, key=lambda t: ((player.sprite.rect.centerx - t.rect.centerx) ** 2 + (player.sprite.rect.centery - t.rect.centery) ** 2))
                target_pos = (nearest_teammate.rect.centerx, nearest_teammate.rect.centery)
                puck.sprite.pass_puck_to(target_pos)
        else:
            screen.blit(end_surface,(0,0))
            screen.blit(pohar,(200,200))
        

    pygame.display.update()
    clock.tick(60)