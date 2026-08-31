import pygame
import random
import sys

pygame.init()

# Screen
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Cave")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Colors
SKY = (135, 206, 235)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
YELLOW = (255, 220, 0)

# Ship
ship_x = 120
ship_y = HEIGHT // 2
ship_w = 40
ship_h = 25
velocity = 0
gravity = 0.5
jump = -8

# Cave
wall_width = 10
gap_height = 180
gap_y = HEIGHT // 2 - gap_height // 2
gap_speed = 2
scroll_speed = 5

walls = []

for x in range(0, WIDTH + wall_width, wall_width):
    walls.append([x, gap_y])

score = 0
game_over = False

while True:

    # ---------------- Events ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                velocity = jump

            if event.key == pygame.K_r and game_over:
                # Restart
                ship_y = HEIGHT // 2
                velocity = 0
                gap_y = HEIGHT // 2 - gap_height // 2
                score = 0
                game_over = False
                walls = []
                for x in range(0, WIDTH + wall_width, wall_width):
                    walls.append([x, gap_y])

    # ---------------- Game ----------------
    if not game_over:

        velocity += gravity
        ship_y += velocity

        # Move cave
        for wall in walls:
            wall[0] -= scroll_speed

        # Add new cave section
        if walls[0][0] < -wall_width:
            walls.pop(0)

            gap_y += random.randint(-20, 20)
            gap_y = max(60, min(HEIGHT - gap_height - 60, gap_y))

            walls.append([walls[-1][0] + wall_width, gap_y])

            score += 1

        # Collision
        ship_rect = pygame.Rect(ship_x, ship_y, ship_w, ship_h)

        if ship_y < 0 or ship_y + ship_h > HEIGHT:
            game_over = True

        for x, gap in walls:
            top = pygame.Rect(x, 0, wall_width, gap)
            bottom = pygame.Rect(
                x,
                gap + gap_height,
                wall_width,
                HEIGHT - (gap + gap_height)
            )

            if ship_rect.colliderect(top) or ship_rect.colliderect(bottom):
                game_over = True

    # ---------------- Draw ----------------
    screen.fill(SKY)

    # Cave
    for x, gap in walls:
        pygame.draw.rect(screen, BLACK, (x, 0, wall_width, gap))
        pygame.draw.rect(
            screen,
            BLACK,
            (x, gap + gap_height, wall_width, HEIGHT)
        )

    # Ship (rocket)
    pygame.draw.rect(screen, RED, (ship_x, ship_y, ship_w, ship_h))
    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (ship_x + ship_w, ship_y + ship_h // 2),
            (ship_x + ship_w + 15, ship_y + 5),
            (ship_x + ship_w + 15, ship_y + ship_h - 5),
        ],
    )

    # Flame
    if not game_over:
        pygame.draw.polygon(
            screen,
            (255, 120, 0),
            [
                (ship_x, ship_y + ship_h // 2),
                (ship_x - 12, ship_y + 6),
                (ship_x - 12, ship_y + ship_h - 6),
            ],
        )

    # Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    if game_over:
        pygame.draw.circle(
            screen,
            (255, 200, 0),
            (ship_x + 20, int(ship_y + 12)),
            35,
        )
        pygame.draw.circle(
            screen,
            (255, 80, 0),
            (ship_x + 20, int(ship_y + 12)),
            20,
        )

        text = font.render("GAME OVER! Press R", True, WHITE)
        screen.blit(text, (220, 280))

    pygame.display.flip()
    clock.tick(60)