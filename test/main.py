import pygame
import random
import sys
import time

pygame.init()

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
dark_red = (139, 0, 0)
orange = (255, 165, 0)
green = (0, 255, 0)
blue = (50, 153, 213)

dis_width = 800
dis_height = 600

dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Змейка с бомбами')

clock = pygame.time.Clock()

snake_block = 20
initial_snake_speed = 10

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def draw_score(score):
    value = score_font.render("Очки: " + str(score), True, yellow)
    dis.blit(value, [10, 10])

def draw_snake(snake_block, snake_list):
    for i, x in enumerate(snake_list):
        if i == 0: # Head
             pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])
             pygame.draw.rect(dis, black, [x[0]+4, x[1]+4, snake_block-8, snake_block-8]) # Simple eyes
        else: # Body
            outer_color = (0, 200 - i*2 if 200 - i*2 > 0 else 0, 0)
            inner_color = (0, 255 - i*2 if 255 - i*2 > 0 else 0, 0)
            pygame.draw.rect(dis, outer_color, [x[0], x[1], snake_block, snake_block])
            pygame.draw.rect(dis, inner_color, [x[0]+2, x[1]+2, snake_block-4, snake_block-4])


def draw_bomb(bomb_x, bomb_y):
     pygame.draw.rect(dis, dark_red, [bomb_x, bomb_y, snake_block, snake_block])
     pygame.draw.circle(dis, black, (bomb_x + snake_block // 2, bomb_y + snake_block // 2), snake_block // 3)
     pygame.draw.line(dis, black, (bomb_x + snake_block // 2, bomb_y), (bomb_x + snake_block // 2 + 3, bomb_y - 5) , 2) # Fuse


def draw_explosion(center_x, center_y, radius):
    steps = 8
    max_radius = int(radius)
    for i in range(steps):
        r = max_radius * (steps - i) // steps
        if r <= 0: continue
        alpha = 255 * (steps - i) // steps
        color = random.choice([red, orange, yellow])

        temp_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*color, alpha), (r, r), r)
        dis.blit(temp_surf, (center_x - r, center_y - r))


def message(msg, color, y_displace=0, font_size=50):
    mesg_font = pygame.font.SysFont("arial", font_size)
    mesg = mesg_font.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(dis_width / 2, dis_height / 2 + y_displace))
    dis.blit(mesg, mesg_rect)


def gameLoop():
    game_over = False
    game_close = False
    exploding = False
    explosion_details = None # (x, y, start_time)

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    snake_speed = initial_snake_speed

    foodx = round(random.randrange(0, dis_width - snake_block) / snake_block) * snake_block
    foody = round(random.randrange(0, dis_height - snake_block) / snake_block) * snake_block

    bombs = []
    bomb_spawn_timer = 0
    bomb_spawn_interval = 150 # ticks

    while not game_over:

        while game_close:
            dis.fill(blue)
            message("Вы проиграли!", red, -50, 50)
            message("Нажмите C чтобы играть снова или Q для выхода", black, 50, 30)
            draw_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        while exploding:
            dis.fill(black)
            draw_snake(snake_block, snake_List)
            pygame.draw.rect(dis, blue, [foodx, foody, snake_block, snake_block])
            for bomb in bombs:
                draw_bomb(bomb[0], bomb[1])
            draw_score(Length_of_snake - 1)

            center_x = explosion_details[0] + snake_block // 2
            center_y = explosion_details[1] + snake_block // 2
            elapsed_time = time.time() - explosion_details[2]
            max_explosion_radius = 100
            explosion_duration = 0.6 # seconds

            if elapsed_time < explosion_duration:
                current_radius = max_explosion_radius * (elapsed_time / explosion_duration)
                draw_explosion(center_x, center_y, current_radius)
            else:
                exploding = False
                game_close = True

            pygame.display.update()
            clock.tick(30) # Explosion animation FPS

            for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                    exploding = False
                    game_over = True
                    game_close = False # Ensure we exit cleanly


        # --- Main Game Logic ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change

        dis.fill(black)
        pygame.draw.rect(dis, blue, [foodx, foody, snake_block, snake_block])

        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.insert(0, snake_Head) # Insert head at the beginning

        if len(snake_List) > Length_of_snake:
            del snake_List[-1]

        for x in snake_List[1:]:
            if x == snake_Head:
                game_close = True

        # Bomb spawning
        bomb_spawn_timer += 1
        if bomb_spawn_timer >= bomb_spawn_interval:
             bomb_spawn_timer = 0
             valid_pos = False
             while not valid_pos:
                 bx = round(random.randrange(0, dis_width - snake_block) / snake_block) * snake_block
                 by = round(random.randrange(0, dis_height - snake_block) / snake_block) * snake_block
                 # Check collision with snake, food, and other bombs
                 pos_ok = True
                 if bx == foodx and by == foody:
                     pos_ok = False
                 if pos_ok:
                     for seg in snake_List:
                         if bx == seg[0] and by == seg[1]:
                             pos_ok = False
                             break
                 if pos_ok:
                     for bomb in bombs:
                          if bx == bomb[0] and by == bomb[1]:
                              pos_ok = False
                              break
                 if pos_ok:
                     valid_pos = True

             bombs.append([bx, by])
             if len(bombs) > 10: # Limit max bombs
                 bombs.pop(0)

        # Draw bombs
        for bomb in bombs:
             draw_bomb(bomb[0], bomb[1])

        draw_snake(snake_block, snake_List)
        draw_score(Length_of_snake - 1)

        pygame.display.update()

        # Check collision with food
        if x1 == foodx and y1 == foody:
            valid_food_pos = False
            while not valid_food_pos:
                 foodx = round(random.randrange(0, dis_width - snake_block) / snake_block) * snake_block
                 foody = round(random.randrange(0, dis_height - snake_block) / snake_block) * snake_block
                 # Ensure food doesn't spawn on snake or bombs
                 pos_ok = True
                 for seg in snake_List:
                     if foodx == seg[0] and foody == seg[1]:
                         pos_ok = False
                         break
                 if pos_ok:
                      for bomb in bombs:
                          if foodx == bomb[0] and foody == bomb[1]:
                              pos_ok = False
                              break
                 if pos_ok:
                     valid_food_pos = True

            Length_of_snake += 1
            # snake_speed += 0.5 # Optional: Increase speed

        # Check collision with bombs
        for bomb in bombs:
             if x1 == bomb[0] and y1 == bomb[1]:
                 exploding = True
                 explosion_details = (x1, y1, time.time())
                 # Don't set game_close = True yet, wait for animation
                 break # Only explode on one bomb

        clock.tick(snake_speed)

    pygame.quit()
    sys.exit()

gameLoop()