import pygame
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
    def shot_puck(self, player, keys):
        if not self.in_motion:
            self.in_motion = True
            speed = 10
            self.speed_x = 0
            self.speed_y = 0
            if keys[pygame.K_w]:
                self.speed_y = -speed
            if keys[pygame.K_s]:
                self.speed_y = speed
            if keys[pygame.K_a]:
                self.speed_x = -speed
            if keys[pygame.K_d]:
                self.speed_x = speed
            if self.speed_x != 0 and self.speed_y != 0:
                self.speed_x *= 0.7071  
                self.speed_y *= 0.7071
            if self.speed_x == 0 and self.speed_y == 0:
                if player.direction == "left":
                    self.speed_x = -speed
                elif player.direction == "right":
                    self.speed_x = speed
                else:
                    self.speed_y = -speed

    def reset(self):
        self.rect.topleft = (self.default_x, self.default_y)
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0
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
            puck.sprite.update()
            puck.draw(screen)
            goal_result = check_goal_collision()
            if goal_result == 'home':
                home_score += 1
            elif goal_result == 'away':
                away_score += 1
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
        else:
            screen.blit(end_surface,(0,0))
            screen.blit(pohar,(200,200))
        

    pygame.display.update()
    clock.tick(60)