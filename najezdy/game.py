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
clock = pygame.time.Clock()
game_started = False
can_pickup = False
pickup_delay = 2000  
start_time = pygame.time.get_ticks()
paused = False
goalie_caught_time = 0
pause_duration = 2000
class Player(pygame.sprite.Sprite):
    def __init__(self, x = 400, y = 925):
        super().__init__()
        self.image = pygame.Surface((40,60))
        self.image.fill("Red")
        self.rect = self.image.get_rect(midbottom = (x,y))
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
    def reset_position(self):
        self.rect.midbottom = (self.default_x, self.default_y)
class Puck(pygame.sprite.Sprite):
    def __init__(self, x = 400, y = 857.5,):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill("Black")
        self.rect = self.image.get_rect(midbottom = (x,y))
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
            if dx != 0 or dy != 0:
                length = (dx**2 + dy**2) ** 0.5
                self.speed_x = dx / length * speed
                self.speed_y = dy / length * speed
            else:
                if player.direction == "left":
                    self.speed_x = -speed
                    self.speed_y = 0
                elif player.direction == "right":
                    self.speed_x = speed
                    self.speed_y = 0
                else:
                    self.speed_x = 0
                    self.speed_y = -speed
    def reset_position(self):
        self.rect.midbottom = (self.default_x, self.default_y)
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0
        self.caught_by_goalie = False
        self.carried_by = None
class Goal(pygame.sprite.Sprite):
    def __init__(self, a = 390, b = 90,):
        super().__init__()
        self.image = pygame.Surface((50,20))
        self.image.fill("Black")
        self.rect =  self.image.get_rect()
        self.rect.topleft = (a, b)
class Goalkeeper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Blue_keeper.png")
        self.image = pygame.transform.scale(self.image, (50,50))
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

    def catch_puck(self):
        self.has_puck = True
        puck.sprite.in_motion = False
        puck.sprite.caught_by_goalie = True
        self.hold_timer = 0
        puck.sprite.speed_x = 0
        puck.sprite.speed_y = 0
def check_goal_collision():
    if puck.sprite.rect.colliderect(goal.sprite.rect):
        if puck.sprite.speed_y < 0 and puck.sprite.rect.bottom <= goal.sprite.rect.bottom + 5:
            print("GÓL DO HORNÍ BRANKY!")
            puck.sprite.reset()
            return 'away'
    return None
player = pygame.sprite.GroupSingle() 
player.add(Player())
puck = pygame.sprite.GroupSingle()
puck.add(Puck())
goal = pygame.sprite.GroupSingle()
goal.add(Goal())
goalie = pygame.sprite.GroupSingle()
goalie.add(Goalkeeper())
while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit()
    current_time = pygame.time.get_ticks()
    if paused:
        if paused and current_time - goalie_caught_time >= pause_duration:
            paused = False
            puck.sprite.reset_position()
            player.sprite.reset_position()
            can_pickup = False
            start_time = current_time
        else:
            screen.blit(sky_surface,(0,0)) 
            screen.blit(stredovka,(0,850))
            screen.blit(ofsajd_lajna,(0,600))
            screen.blit(brankova_lajna,(0,100))
            pygame.draw.circle(sky_surface, "blue", (400,857.5),50,5 )
            for q in puntiky:
                pygame.draw.circle(sky_surface, "red", q,5,)
            for w in postranni_kruhy:
                pygame.draw.circle(sky_surface, "red",w,50,5 )
            player.draw(screen)
            puck.draw(screen)
            goal.draw(screen)
            goalie.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue
    if not paused:
        if not can_pickup and pygame.time.get_ticks() - start_time > pickup_delay:
            can_pickup = True
        if not paused and puck.sprite.caught_by_goalie:
            paused = True
            goalie_caught_time = pygame.time.get_ticks()
        if puck.sprite.rect.colliderect(goalie.sprite.rect):
            puck.sprite.caught_by_goalie = True
            puck.sprite.in_motion = False
            puck.sprite.speed_x = 0
            puck.sprite.speed_y = 0
            paused = True
            goalie_caught_time = current_time
            goalie.sprite.has_puck = True
        if puck.sprite.in_motion and player.sprite.rect.colliderect(puck.sprite.rect):
            puck.sprite.in_motion = False
            puck.sprite.speed_x = 0
            puck.sprite.speed_y = 0
            puck.sprite.has_puck(player.sprite)
        if can_pickup and not puck.sprite.in_motion and not puck.sprite.caught_by_goalie:
            if player.sprite.rect.colliderect(puck.sprite.rect):
                puck.sprite.has_puck(player.sprite)
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
        goal.update()
        goal.draw(screen)
        goalie.update()
        goalie.draw(screen)
        if puck.sprite.rect.colliderect(goalie.sprite.rect):
            puck.sprite.caught_by_goalie = True
            puck.sprite.in_motion = False
            puck.sprite.speed_x = 0
            puck.sprite.speed_y = 0
            paused = True
            goalie_caught_time = current_time
        if not can_pickup and pygame.time.get_ticks() - start_time > pickup_delay:
            can_pickup = True
        if puck.sprite.in_motion and player.sprite.rect.colliderect(puck.sprite.rect):
            puck.sprite.in_motion = False
            puck.sprite.speed_x = 0
            puck.sprite.speed_y = 0
            puck.sprite.has_puck(player.sprite)
        if can_pickup and not puck.sprite.in_motion and not puck.sprite.caught_by_goalie:
           puck.sprite.has_puck(player.sprite)
        if keys[pygame.K_SPACE]:
            puck.sprite.shot_puck(player.sprite, keys)
        if check_goal_collision():
            goal_result = check_goal_collision()    
        pygame.display.flip()
        clock.tick(60)
