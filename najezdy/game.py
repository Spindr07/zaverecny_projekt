import pygame
pygame.init()
pygame.mixer.init()
window_width = 800
window_height = 1000
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Hokejové nájezdy")
end_surface = pygame.Surface((window_width,window_height))
end_surface.fill("black")
sky_surface = pygame.Surface((window_width,window_height))
sky_surface.fill("white")
stredovka = pygame.Surface((800,10))
stredovka.fill("dark red")
puntiky = [(150,270),(650,270)]
postranni_kruhy = [(150,270),(650,270),]
ofsajd_lajna = pygame.Surface((800,10))
ofsajd_lajna.fill("blue")
brankova_lajna = pygame.Surface((800,5))
brankova_lajna.fill("dark red")
game_active = True
clock = pygame.time.Clock()
game_started = False
can_pickup = False
pickup_delay = 500  
start_time = pygame.time.get_ticks()
paused = False
goalie_caught_time = 0
pause_duration = 1000
score = 0
attempts = 0
puck_stop_time = 0
waiting_after_stop = False
class Player(pygame.sprite.Sprite):
    def __init__(self, x = 400, y = 970):
        super().__init__()
        player_1 = pygame.image.load('Standing.png')
        player_2 = pygame.image.load('Moving1.png')
        player_3 = pygame.image.load('Moving2.png')
        player_1 = pygame.transform.scale(pygame.image.load('Standing.png'), (40, 70))
        player_2 = pygame.transform.scale(pygame.image.load('Moving1.png'), (40, 60))
        player_3 = pygame.transform.scale(pygame.image.load('Moving2.png'), (40, 60))
        self.player_images = [player_2, player_3]
        self.player_index = 0
        self.standing_image = player_1
        self.image = self.player_images[self.player_index]
        self.rect = self.image.get_rect(midbottom = (x,y))
        self.default_x = x
        self.default_y = y
        self.speed = 5
        self.direction = None
        self.position = (x,y)
        self.active = True
        self.animation_counter = 0
        self.animation_speed= 0.05
        self.index = 0
    def update(self, keys):
        moving = False
        if not self.active:
            return
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            moving = True
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            moving = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            moving = True
        if moving:
            self.animate()
      
        else:
            self.player_index = 0
            self.image = self.player_images[self.player_index]
            self.image = self.standing_image
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > window_width:
            self.rect.right = window_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > window_height:
            self.rect.bottom = window_height
    def animate(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.index = (self.index + 1) % len(self.player_images)
            self.image = self.player_images[self.index]
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
        self.was_shot = False
    def has_puck(self, player):
        if not self.in_motion and not self.caught_by_goalie:
            self.carried_by = player
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
            self.was_shot = False
            self.carried_by = None
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
                self.was_shot = True
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
        self.stopped = False
        self.just_reset = True
        self.was_shot = False
class Goal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("branka.png")
        self.image = pygame.transform.scale(self.image,(150,110))
        self.rect =  self.image.get_rect(center = (400,50))
       
class Goalkeeper(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        man_1 = pygame.image.load('Red_keeper.png')
        man_2 = pygame.image.load('left.png.png')
        man_3 = pygame.image.load('right (1).png')
        man_1 = pygame.transform.scale(pygame.image.load('Red_keeper.png'), (40, 70))
        man_2 = pygame.transform.scale(pygame.image.load('left.png.png'), (40, 60))
        man_3 = pygame.transform.scale(pygame.image.load('right (1).png'), (40, 60))
        self.keeping_images = [man_1, man_2, man_3]
        self.keeping_index = 0
        self.image = self.keeping_images[self.keeping_index]
        self.rect = self.image.get_rect(center=(400, 120))
        self.move_speed = 2
        self.direction = 1
        self.has_puck = False
        self.hold_timer = 0
    def update(self):
        puck_x = puck.sprite.rect.centerx  
        if puck_x > self.rect.centerx:
            self.rect.x += self.move_speed
            self.keeping_index = 2 
        elif puck_x < self.rect.centerx:
            self.rect.x -= self.move_speed
            self.keeping_index = 1 
        else:
            self.keeping_index = 0
        self.image = self.keeping_images[self.keeping_index]
        if self.rect.left < 350:
            self.rect.left = 350
        if self.rect.right > 450:
            self.rect.right = 450
        if self.rect.colliderect(puck.sprite.rect) and puck.sprite.in_motion and not self.has_puck:
            self.catch_puck()
        if self.has_puck:
            self.hold_timer += 1
            puck.sprite.rect.center = (self.rect.centerx, self.rect.bottom + 5)


    def catch_puck(self):
        self.has_puck = True
        puck.sprite.in_motion = False
        puck.sprite.caught_by_goalie = True
        self.hold_timer = 0
        puck.sprite.speed_x = 0
        puck.sprite.speed_y = 0
        global attempts
        attempts += 1
    def reset_position(self):
        self.rect.center = (400, 120)
        self.has_puck = False
        self.hold_timer = 0

def check_goal_collision():
    puck_rect = puck.sprite.rect
    goal_rect = goal.sprite.rect

    if (
        puck.sprite.speed_y < 0 and
        puck_rect.left >= goal_rect.left and
        puck_rect.right <= goal_rect.right and
        puck_rect.top <= goal_rect.bottom - 5):
        puck.sprite.reset_position()
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
title_font = pygame.font.SysFont("arial", 40)
prompt_font = pygame.font.SysFont("arial", 40)
score_font = pygame.font.SysFont("calligrapher", 30)
game_state = "menu"
zvuk = pygame.mixer.Sound("menu_sound.mp3")
zvuk.set_volume(0.3)
goal_horn = pygame.mixer.Sound("goal.mp3")
goal_horn.set_volume(0.3)
win_horn = pygame.mixer.Sound("win.mp3")
win_horn.set_volume(0.3)
fail_horn = pygame.mixer.Sound("fail.mp3")
fail_horn.set_volume(0.3)
menu_background = pygame.image.load("menu.png")
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            exit()
    if game_state == "menu":
        screen.blit(menu_background, (-240,100))
        zvuk.play()
        title_surface = title_font.render(f"Hokejová hra: Nájezdy", True, "White")
        ovladani_surface = title_font.render(f"WSAD, SPACE, 5/10 for win", True, "White")
        screen.blit(title_surface,(100,50))
        screen.blit(ovladani_surface,(100,850))
    if game_state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "hra"
                frame = 0
                time = 0
                game_active = True
                zvuk.stop()
    elif game_state == "hra":
        if not game_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                frame = 0
                time = 0
                game_active = True
                print("Restart")
    current_time = pygame.time.get_ticks()
    pygame.display.flip()
    if game_state == "hra":
        if game_active:
            keys = pygame.key.get_pressed()
            if paused:
                if paused and current_time - goalie_caught_time >= pause_duration:
                    paused = False
                    puck.sprite.reset_position()
                    player.sprite.reset_position()
                    goalie.sprite.has_puck = False
                    goalie.sprite.reset_position()
                    can_pickup = False
                    start_time = current_time
                else:
                    screen.blit(sky_surface,(0,0)) 
                    screen.blit(stredovka,(0,850))
                    screen.blit(ofsajd_lajna,(0,600))
                    screen.blit(brankova_lajna,(0,100))
                    pygame.draw.circle(sky_surface, "blue", (400,857.5),100,5 )
                    for q in puntiky:
                        pygame.draw.circle(sky_surface, "dark red", q,5,)
                    for w in postranni_kruhy:
                        pygame.draw.circle(sky_surface, "dark red",w,100,5 )
                    player.draw(screen)
                    puck.draw(screen)
                    goal.draw(screen)
                    goalie.draw(screen)
                    pygame.display.flip()
                    clock.tick(60)
                    continue
            if not paused:
                if not paused and puck.sprite.caught_by_goalie:
                    paused = True
                    goalie_caught_time = pygame.time.get_ticks()
                if can_pickup and not puck.sprite.in_motion and not puck.sprite.caught_by_goalie and not puck.sprite.was_shot:
                    if player.sprite.rect.colliderect(puck.sprite.rect):
                        puck.sprite.has_puck(player.sprite)
                score_surface = score_font.render(f"skóre: {score}", True, "Black")
                attempts_surface = score_font.render(f"pokusy: {attempts}", True, "Black")
                screen.blit(sky_surface,(0,0)) 
                screen.blit(stredovka,(0,850))
                screen.blit(ofsajd_lajna,(0,600))
                screen.blit(brankova_lajna,(0,100))
                screen.blit(score_surface,(50,900))
                screen.blit(attempts_surface,(50,950))
                pygame.draw.circle(sky_surface, "blue", (400,857.5),100,5 )
                for q in puntiky:
                    pygame.draw.circle(sky_surface, "dark red", q,5,)
                for w in postranni_kruhy:
                    pygame.draw.circle(sky_surface, "dark red",w,100,5 )
                player.update(keys)
                player.draw(screen)
                puck.update()
                puck.draw(screen)
                goal.update()
                goal.draw(screen)
                goalie.update()
                goalie.draw(screen)
                goal_rect = goal.sprite.rect
                left_post = pygame.Rect(goal_rect.left, goal_rect.top, 5, goal_rect.height)
                right_post = pygame.Rect(goal_rect.right - 5, goal_rect.top, 5, goal_rect.height)
                top_bar = pygame.Rect(goal_rect.left, goal_rect.top, goal_rect.width, 5)
                if puck.sprite.rect.colliderect(left_post) and puck.sprite.speed_x > 0:
                    puck.sprite.speed_x *= -1
                if puck.sprite.rect.colliderect(right_post) and puck.sprite.speed_x < 0:
                    puck.sprite.speed_x *= -1
                if puck.sprite.rect.colliderect(top_bar) and puck.sprite.speed_y < 0:
                    puck.sprite.speed_y *= -1
                if puck.sprite.rect.colliderect(goalie.sprite.rect):
                    puck.sprite.caught_by_goalie = True
                    attempts += 1
                    puck.sprite.in_motion = False
                    puck.sprite.speed_x = 0
                    puck.sprite.speed_y = 0
                    paused = True
                    goalie_caught_time = current_time
                if not can_pickup and pygame.time.get_ticks() - start_time > pickup_delay:
                    can_pickup = True
                if puck.sprite.in_motion and player.sprite.rect.colliderect(puck.sprite.rect) and not puck.sprite.was_shot:
                    puck.sprite.in_motion = False
                    puck.sprite.speed_x = 0
                    puck.sprite.speed_y = 0
                    puck.sprite.has_puck(player.sprite)
                if keys[pygame.K_SPACE]:
                    puck.sprite.shot_puck(player.sprite, keys)
                    puck.sprite.was_shot = True
                if check_goal_collision():
                    goal_horn.play()
                    goal_result = check_goal_collision() 
                    score += 1  
                    attempts += 1
                    paused = True
                    goalie_caught_time = current_time 
                if puck.sprite.stopped and not waiting_after_stop:
                    waiting_after_stop = True
                    puck_stop_time = pygame.time.get_ticks()
                    puck.sprite.stopped = False  # Aby se to spustilo jen jednou
                if waiting_after_stop:
                    if current_time - puck_stop_time >= 1000:  # Po 1 vteřině
                        player.sprite.reset_position()
                        puck.sprite.reset_position()
                        goalie.sprite.has_puck = False
                        can_pickup = False
                        start_time = current_time
                        waiting_after_stop = False
                        attempts += 1
                    else:
                        screen.blit(sky_surface,(0,0)) 
                        screen.blit(stredovka,(0,850))
                        screen.blit(ofsajd_lajna,(0,600))
                        screen.blit(brankova_lajna,(0,100))
                        score_surface = score_font.render(f"skóre: {score}", True, "Black")
                        screen.blit(score_surface,(0,100))
                        attempts_surface = score_font.render(f"skóre: {attempts}", True, "Black")
                        screen.blit(attempts_surface,(0,100))
                        pygame.draw.circle(sky_surface, "blue", (400,857.5),100,5 )
                        for q in puntiky:
                            pygame.draw.circle(sky_surface, "dark red", q,5,)
                        for w in postranni_kruhy:
                            pygame.draw.circle(sky_surface, "dark red",w,100,5 )
                        player.draw(screen)
                        puck.draw(screen)
                        goal.draw(screen)
                        goalie.draw(screen)
                        pygame.display.flip()
                        clock.tick(60)
                        continue
                if attempts == 10:
                    screen.blit(end_surface,(0,0))
                    if score >= 5:
                        win_surface = pygame.image.load("win.png")
                        win_surface = pygame.transform.scale(pygame.image.load("win.png"), (window_width, window_height))
                        score_surface = score_font.render(f"skóre: {score}", True, "Black")
                        win_horn.play()
                        screen.blit(win_surface,(0,0))
                        screen.blit(score_surface,(350,900))
                    else:
                        lose_surface = pygame.image.load("lose.png")
                        lose_surface = pygame.transform.scale(pygame.image.load("lose.png"), (window_width, window_height))
                        screen.blit(lose_surface,(0,0))
                        fail_horn.play()
                    game_active = False
                clock.tick(60)
                pygame.display.flip()