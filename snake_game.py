import pygame
import random
import sys

# ─────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────
WINDOW_W, WINDOW_H = 800, 600
CELL      = 20          # grid cell size (px)
FPS       = 10          # starting speed

# Colour palette
BG_DARK   = (10,  12,  20)
BG_GRID   = (20,  24,  36)
SNAKE_H   = (80,  220, 120)   # head
SNAKE_B   = (50,  180,  90)   # body
FOOD_CLR  = (255,  70,  70)
TEXT_CLR  = (230, 230, 240)
SCORE_CLR = (100, 210, 255)
BORDER    = (50,   60,  90)
OVERLAY   = (10,  12,  20, 200)

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def draw_rounded_rect(surface, color, rect, radius=6):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def grid_rect(gx, gy):
    """Convert grid coords → pixel Rect (with 2‑px padding)."""
    return pygame.Rect(gx * CELL + 2, gy * CELL + 2, CELL - 4, CELL - 4)

def random_food(snake_body):
    cols = WINDOW_W // CELL
    rows = WINDOW_H // CELL
    while True:
        pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
        if pos not in snake_body:
            return pos

# ─────────────────────────────────────────
#  SCREENS
# ─────────────────────────────────────────
def draw_grid(surface):
    for x in range(0, WINDOW_W, CELL):
        pygame.draw.line(surface, BG_GRID, (x, 0), (x, WINDOW_H))
    for y in range(0, WINDOW_H, CELL):
        pygame.draw.line(surface, BG_GRID, (0, y), (WINDOW_W, y))

def draw_border(surface):
    pygame.draw.rect(surface, BORDER, (0, 0, WINDOW_W, WINDOW_H), 3)

def show_start_screen(surface, font_big, font_med, font_sm):
    surface.fill(BG_DARK)
    draw_grid(surface)

    title = font_big.render("🐍  SNAKE", True, SNAKE_H)
    sub   = font_med.render("Python Edition", True, TEXT_CLR)
    hint  = font_sm.render("Press  SPACE  to start  |  Arrow Keys to move", True, (150, 160, 190))
    ctrl  = font_sm.render("Eat food to grow  ·  Don't hit walls or yourself", True, (120, 130, 160))

    surface.blit(title, title.get_rect(center=(WINDOW_W//2, 200)))
    surface.blit(sub,   sub.get_rect(center=(WINDOW_W//2, 265)))

    pygame.draw.line(surface, BORDER, (200, 300), (600, 300), 1)

    surface.blit(hint, hint.get_rect(center=(WINDOW_W//2, 340)))
    surface.blit(ctrl, ctrl.get_rect(center=(WINDOW_W//2, 375)))

    draw_border(surface)
    pygame.display.flip()

def show_game_over(surface, font_big, font_med, font_sm, score, best):
    # semi‑transparent overlay
    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    surface.blit(overlay, (0, 0))

    go   = font_big.render("GAME OVER", True, FOOD_CLR)
    sc   = font_med.render(f"Score : {score}", True, SCORE_CLR)
    bs   = font_sm.render(f"Best  : {best}", True, TEXT_CLR)
    hint = font_sm.render("SPACE → Restart   |   ESC → Quit", True, (150, 160, 190))

    surface.blit(go,   go.get_rect(center=(WINDOW_W//2, 210)))
    surface.blit(sc,   sc.get_rect(center=(WINDOW_W//2, 290)))
    surface.blit(bs,   bs.get_rect(center=(WINDOW_W//2, 340)))
    surface.blit(hint, hint.get_rect(center=(WINDOW_W//2, 410)))

    draw_border(surface)
    pygame.display.flip()

# ─────────────────────────────────────────
#  MAIN GAME
# ─────────────────────────────────────────
def run_game(surface, clock, font_big, font_med, font_sm):
    cols  = WINDOW_W // CELL
    rows  = WINDOW_H // CELL
    cx, cy = cols // 2, rows // 2

    snake  = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
    direc  = (1, 0)          # moving right
    food   = random_food(snake)
    score  = 0
    speed  = FPS

    grow_next = False

    while True:
        # ── Events ──────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direc != (0,  1): direc = (0, -1)
                if event.key == pygame.K_DOWN  and direc != (0, -1): direc = (0,  1)
                if event.key == pygame.K_LEFT  and direc != (1,  0): direc = (-1, 0)
                if event.key == pygame.K_RIGHT and direc != (-1, 0): direc = (1,  0)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Move ────────────────────────────────
        hx, hy  = snake[0]
        nx, ny  = hx + direc[0], hy + direc[1]
        new_head = (nx, ny)

        # Collision: wall
        if not (0 <= nx < cols and 0 <= ny < rows):
            return score          # game over

        # Collision: self
        if new_head in snake:
            return score

        snake.insert(0, new_head)

        if new_head == food:
            score += 10
            speed  = FPS + score // 50   # gradually speed up
            clock.tick(speed)
            food = random_food(snake)
        else:
            snake.pop()

        # ── Draw ────────────────────────────────
        surface.fill(BG_DARK)
        draw_grid(surface)

        # Food (pulsing circle)
        fx, fy = food
        fc_x   = fx * CELL + CELL // 2
        fc_y   = fy * CELL + CELL // 2
        pulse  = abs((pygame.time.get_ticks() % 800) - 400) / 400  # 0‥1
        radius = int(CELL // 2 - 2 + pulse * 3)
        pygame.draw.circle(surface, FOOD_CLR, (fc_x, fc_y), radius)
        pygame.draw.circle(surface, (255, 140, 140), (fc_x - 3, fc_y - 3), max(2, radius // 3))

        # Snake body
        for i, (bx, by) in enumerate(snake):
            clr = SNAKE_H if i == 0 else SNAKE_B
            draw_rounded_rect(surface, clr, grid_rect(bx, by), radius=5 if i == 0 else 4)

        # HUD
        score_surf = font_med.render(f"Score: {score}", True, SCORE_CLR)
        speed_surf = font_sm.render(f"Speed: {speed}", True, (150, 160, 200))
        surface.blit(score_surf, (12, 8))
        surface.blit(speed_surf, (WINDOW_W - 110, 10))

        draw_border(surface)
        pygame.display.flip()
        clock.tick(speed)

# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────
def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Snake — Python Edition")
    clock = pygame.time.Clock()

    # Fonts (falls back gracefully if system font missing)
    font_big = pygame.font.SysFont("consolas", 72, bold=True)
    font_med = pygame.font.SysFont("consolas", 36)
    font_sm  = pygame.font.SysFont("consolas", 22)

    best_score = 0

    while True:
        # ── Start screen ────────────────────────
        show_start_screen(surface, font_big, font_med, font_sm)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        # ── Play ────────────────────────────────
        score = run_game(surface, clock, font_big, font_med, font_sm)
        best_score = max(best_score, score)

        # ── Game‑over screen ────────────────────
        show_game_over(surface, font_big, font_med, font_sm, score, best_score)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()