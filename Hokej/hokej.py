import pygame
import math
pygame.init()
window_width = 800
window_height = 1000
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
        def reset(self):
            self.x = 100
            self.y = 200
         


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
        self.default_x = x
        self.default_y = y
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
    def reset(self):
        self.x = 100
        self.y = 200
    def shot_puck(self, keys):
        if keys[pygame.K_e]:
            self.rect = self.image.get_rect(topleft = (100,200))
class Goal(pygame.sprite.Sprite):
    def __init__(self, a = 390, b = 90,):
        super().__init__()
<<<<<<< HEAD
        self.image = pygame.Surface((20,10))
=======
        self.image = pygame.Surface((30,20))
>>>>>>> origin/main
        self.image.fill("Black")
        self.rect =  self.image.get_rect()
        self.rect.topleft = (a, b)
        
def is_collision():
<<<<<<< HEAD
    if puck.sprite.rect.colliderect(goal.sprite.rect):
        if puck.sprite.rect.bottom <= goal.sprite.rect.top:
            print("Dotek shora!")
=======
    return (
    pygame.sprite.spritecollide(puck.sprite, goal, False) or
    pygame.sprite.spritecollide(puck.sprite, goal2, False))
def reset_game():
    player.sprite.rect.x = player.sprite.default_x
    player.sprite.rect.y = player.sprite.default_y
    puck.sprite.rect.x = player.sprite.default_x
    puck.sprite.rect.y = player.sprite.default_y
>>>>>>> origin/main


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
            reset_game()
            player.update(keys)
            player.draw(screen)
        
            


    score_surface = score_font.render(f"Skóre: {score}", True, "Black")
    screen.blit(score_surface, score_rect)
    time_surface = time_font.render(f"čas: {time}", True, "Black")
    screen.blit(time_surface, time_rect)
    pygame.display.update()
    clock.tick(60)