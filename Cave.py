import pygame
import random
import sys

# ----------------------------
# Setup
# ----------------------------
pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Cave")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# ----------------------------
# Player
# ----------------------------
player_x = 120
player_y = HEIGHT // 2
player_w = 40
player_h = 30

velocity = 0

# ----------------------------
# Cave
# ----------------------------
gap = 220
cave_center = HEIGHT // 2
scroll_speed = 6
change = random.randint(-3, 3)

segments = []

for x in range(0, WIDTH + 20, 20):
    top = cave_center - gap // 2
    bottom = cave_center + gap // 2
    segments.append([x, top, bottom])

score = 0
game_over = False

# ----------------------------
# Game Loop
# ----------------------------
while True:

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Keys
    keys = pygame.key.get_pressed()

    if not game_over:

        # Hold SPACE to fly
        if keys[pygame.K_SPACE]:
            velocity -= 0.6
        else:
            velocity += 0.4

        velocity *= 0.96
        player_y += velocity

        # Move cave
        for seg in segments:
            seg[0] -= scroll_speed

        if segments[0][0] < -20:

            last = segments[-1]

            cave_center += change

            if random.randint(1, 15) == 1:
                change = random.randint(-4, 4)

            cave_center = max(gap // 2 + 30,
                              min(HEIGHT - gap // 2 - 30,
                                  cave_center))

            top = cave_center - gap // 2
            bottom = cave_center + gap // 2

            segments.pop(0)
            segments.append([last[0] + 20, top, bottom])

            score += 1

        # Collision
        player_rect = pygame.Rect(
            player_x,
            int(player_y),
            player_w,
            player_h
        )

        for seg in segments:
            if seg[0] <= player_x + player_w and seg[0] + 20 >= player_x:

                if player_y < seg[1] or player_y + player_h > seg[2]:
                    game_over = True
                    break

        if player_y < 0 or player_y + player_h > HEIGHT:
            game_over = True

    # ----------------------------
    # Draw
    # ----------------------------
    screen.fill((80, 180, 255))

    # Cave
    for seg in segments:
        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (seg[0], 0, 20, seg[1])
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (seg[0], seg[2], 20, HEIGHT - seg[2])
        )

    # Ship (simple rocket)
    pygame.draw.polygon(
        screen,
        (255, 220, 0),
        [
            (player_x, player_y + player_h // 2),
            (player_x + player_w - 8, player_y),
            (player_x + player_w, player_y + player_h // 2),
            (player_x + player_w - 8, player_y + player_h)
        ]
    )

    pygame.draw.rect(
        screen,
        (200, 50, 50),
        (player_x - 8, player_y + 8, 10, 14)
    )

    if keys[pygame.K_SPACE] and not game_over:
        pygame.draw.polygon(
            screen,
            (255, 120, 0),
            [
                (player_x - 8, player_y + 10),
                (player_x - 22, player_y + 15),
                (player_x - 8, player_y + 20)
            ]
        )

    # Score
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    if game_over:
        over = font.render(
            "GAME OVER - Press ESC to Quit",
            True,
            (255, 60, 60)
        )
        screen.blit(over, (170, 280))

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(60)