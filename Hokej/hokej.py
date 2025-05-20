import pygame
pygame.init()
window_width = 500
window_height = 800
sky_surface = pygame.Surface((window_width,window_height))
sky_surface.fill("white")
pygame.display.set_caption("Hokejový zápas") 
game_active = True
has_puck = True
class Player(pygame.sprite.Sprite):
    def __init__(self, x = 0, y = 0):
        super().__init__()
        self.image = pygame.Surface((40,60))
        self.image.fill("Red")
        self.rect = self.image.get_rect(topright = (x,y))
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
        self.rect.topright = self.position

class Goalkeeper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("keeper.png")
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect(midbottom = (300, 200) )



class Enemy(pygame.sprite.Sprite):
    def __init__(self, c = 200, d = 200):
        super().__init__()
        self.image = pygame.Surface((40,60))
        self.image.fill("Blue")
        self.rect = self.image.get_rect(midbottom=(c, d))
        self.speed = 5
class Puck(pygame.sprite.Sprite):
    def __init__(self, x = 100, y = 200,):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill("Black")
        self.rect = self.image.get_rect(topleft = (x,y))
    def has_puck(self,player):
        offset_x = 30
        offset_y = 10
        if player.direction == "left":
            self.rect.centerx = player.rect.centerx - offset_x
        elif player.direction == "right":
            self.rect.centerx = player.rect.centerx + offset_x
        else:
            self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery + offset_y
    def shot_puck(self, keys):
        if keys[pygame.K_e]:
            self.rect = self.image.get_rect(topleft = (100,200))
class Goal(pygame.sprite.Sprite):
    def __init__(self, a = 100, b = 100):
        super().__init__()
        self.image = pygame.image.load("branka.png")
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect =  self.image.get_rect()
        self.rect.topleft = (a, b)
def is_collision():
    return (
    pygame.sprite.spritecollide(puck.sprite, goal, False) or
    pygame.sprite.spritecollide(puck.sprite, goal2, False))


goalkeeper = pygame.sprite.GroupSingle()
goalkeeper.add(Goalkeeper())
puck = pygame.sprite.GroupSingle()
puck.add(Puck())
enemy = pygame.sprite.GroupSingle()
enemy.add(Enemy())
enemy1 = pygame.sprite.GroupSingle()
enemy1.add(Enemy(300,300))
enemy2 = pygame.sprite.GroupSingle()
enemy2.add(Enemy(400,400))
enemy3 = pygame.sprite.GroupSingle()
enemy3.add(Enemy(450,450))
enemy4 = pygame.sprite.GroupSingle()
enemy4.add(Enemy(500,500))
player = pygame.sprite.GroupSingle() 
player.add(Player(100,200)) 
goal = pygame.sprite.GroupSingle()
goal.add(Goal())
goal2 = pygame.sprite.GroupSingle()
goal2.add(Goal(300,400))
screen = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
offset_x = 20
offset_y = 10
score = 0
frame = 0
score_font = pygame.font.SysFont("arial", 40)
score_text = score_font.render("score", True, (0, 0, 0))
score_rect = score_text.get_rect(topleft=(20, 20))
time_font = pygame.font.SysFont("arial", 40)
time_text = time_font.render("score", True, (0, 0, 0))
time_rect = time_text.get_rect(topright=(200,200))
while True:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            player.sprite.active = True
            pygame.time.set_timer(pygame.USEREVENT, 0)
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit() 
    if game_active:
        keys = pygame.key.get_pressed()
        screen.blit(sky_surface,(0,0)) 
        player.update(keys)
        player.draw(screen)
        frame += 1
        time = frame // 60
        enemy.update()
        enemy.draw(screen)
        enemy1.update()
        enemy1.draw(screen)
        enemy2.update()
        enemy2.draw(screen)
        enemy3.update()
        enemy3.draw(screen)
        enemy4.update()
        enemy4.draw(screen)
        puck.update()
        puck.draw(screen)
        puck.sprite.has_puck(player.sprite)
        puck.sprite.shot_puck(keys)
        goal.update()
        goal.draw(screen)
        goal2.update()
        goal2.draw(screen)
        goalkeeper.update()
        goalkeeper.draw(screen)
        if time == 20:
            print("Konec")
            game_active = False
        if is_collision():
            game_active = False
            score += 1
            #if keys[pygame.K_r]:
               # player.sprite.reset_position()
                #player.sprite.active = False
                #pygame.time.set_timer(pygame.USEREVENT, 1000)


    score_surface = score_font.render(f"Skóre: {score}", True, "Black")
    screen.blit(score_surface, score_rect)
    time_surface = time_font.render(f"čas: {time}", True, "Black")
    screen.blit(time_surface, time_rect)
    pygame.display.update()
    clock.tick(60) 