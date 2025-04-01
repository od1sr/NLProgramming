import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_snake(snake_body):
    for segment in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, BLACK, pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_food(food_pos):
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, BLACK, pygame.Rect(food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def show_score(score):
    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (5, 5))

def game_over_screen(score):
    screen.fill(BLACK)
    game_over_font = pygame.font.SysFont(None, 75)
    score_font = pygame.font.SysFont(None, 50)

    game_over_text = game_over_font.render("Игра окончена!", True, RED)
    score_text = score_font.render(f"Ваш счет: {score}", True, WHITE)

    game_over_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def main():
    snake_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    snake_body = [[snake_pos[0], snake_pos[1]],
                  [snake_pos[0] - 1, snake_pos[1]],
                  [snake_pos[0] - 2, snake_pos[1]]]
    direction = RIGHT
    change_to = direction

    food_pos = [random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT)]
    while food_pos in snake_body:
         food_pos = [random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT)]

    score = 0
    game_speed = 10
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if direction != DOWN:
                        change_to = UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if direction != UP:
                        change_to = DOWN
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if direction != RIGHT:
                        change_to = LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if direction != LEFT:
                        change_to = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        direction = change_to

        snake_pos[0] += direction[0]
        snake_pos[1] += direction[1]

        if snake_pos[0] < 0 or snake_pos[0] >= GRID_WIDTH or snake_pos[1] < 0 or snake_pos[1] >= GRID_HEIGHT:
            game_over = True

        snake_body.insert(0, list(snake_pos))

        if snake_pos == food_pos:
            score += 1
            game_speed = min(30, 10 + score // 2) # Increase speed slightly
            food_pos = [random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT)]
            while food_pos in snake_body:
                food_pos = [random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT)]
        else:
            snake_body.pop()

        if snake_pos in snake_body[1:]:
            game_over = True

        screen.fill(BLACK)
        # draw_grid() # Optional: uncomment to show grid
        draw_snake(snake_body)
        draw_food(food_pos)
        show_score(score)

        pygame.display.flip()
        clock.tick(game_speed)

    game_over_screen(score)

if __name__ == '__main__':
    main()