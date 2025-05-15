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
    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
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




class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40,60))
        self.image.fill("Blue")
        self.rect = self.image.get_rect(midbottom=(200, 0.635 * window_height))
        self.speed = 5
class Puck(pygame.sprite.Sprite):
    def __init__(self, x = 0, y = 0,):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill("Black")
        self.rect = self.image.get_rect(topleft = (x,y))
    def move(self, keys):
        if keys[pygame.K_e]:
            self.rect.midbottom = (100,100)
class Goal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("branka.png")
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect(midtop = (100,100))
def is_collision():
    return pygame.sprite.spritecollide(player.sprite, goal, False)
def has_puck():
    return pygame.sprite.spritecollide(player.sprite, puck, False)
puck = pygame.sprite.GroupSingle()
puck.add(Puck(100,200))
enemy = pygame.sprite.GroupSingle()
enemy.add(Enemy())
player = pygame.sprite.GroupSingle() 
player.add(Player(100,200)) 
goal = pygame.sprite.GroupSingle()
goal.add(Goal())
screen = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
offset_x = 20
offset_y = 10
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit() 
    if game_active:
        keys = pygame.key.get_pressed()
        screen.blit(sky_surface,(0,0)) 
        player.update(keys)
        player.draw(screen)
        enemy.update()
        enemy.draw(screen)
        puck.update(keys)
        puck.draw(screen)
        goal.update()
        goal.draw(screen)
        if is_collision():
            game_active = False
            print("Gól")
    if has_puck():
        puck.sprite.rect.centerx = player.sprite.rect.centerx + offset_x
        puck.sprite.rect.centery = player.sprite.rect.centery + offset_y



    
    pygame.display.update()
    clock.tick(60) 