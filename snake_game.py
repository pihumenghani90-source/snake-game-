# snake-game-
import pygame, sys, random
from pygame.math import Vector2

# ── colours ──────────────────────────────────────────────
BG_COLOR     = (0,   200, 210)   # cyan background
SNAKE_COLOR  = (34,  180,  60)   # green snake
FRUIT_COLOR  = (255,  80, 160)   # pink fruit
GRID_COLOR   = (0,   180, 190)   # subtle grid lines
TEXT_COLOR   = (255, 255, 255)   # white text
SCORE_BG     = (0,   160, 170)

# ── constants ────────────────────────────────────────────
CELL_SIZE   = 30
CELL_NUMBER = 20
SCREEN_SIZE = CELL_SIZE * CELL_NUMBER   # 600 x 600
FPS         = 10                        # snake speed (frames per second)

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 60))
pygame.display.set_caption("🐍  Snake Game")
clock  = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


# ── FRUIT class ──────────────────────────────────────────
class Fruit:
    def __init__(self):
        self.randomize()

    def randomize(self):
        self.pos = Vector2(random.randint(0, CELL_NUMBER - 1),
                           random.randint(0, CELL_NUMBER - 1))

    def draw(self):
        rect = pygame.Rect(int(self.pos.x * CELL_SIZE),
                           int(self.pos.y * CELL_SIZE),
                           CELL_SIZE, CELL_SIZE)
        pygame.draw.ellipse(screen, FRUIT_COLOR, rect.inflate(-4, -4))
        # shine dot
        pygame.draw.circle(screen, (255, 180, 210),
                           (rect.centerx - 4, rect.centery - 4), 4)


# ── SNAKE class ──────────────────────────────────────────
class Snake:
    def __init__(self):
        self.body      = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)   # moving right
        self.grow      = False

    def draw(self):
        for i, block in enumerate(self.body):
            rect = pygame.Rect(int(block.x * CELL_SIZE),
                               int(block.y * CELL_SIZE),
                               CELL_SIZE, CELL_SIZE)
            color = (20, 150, 40) if i == 0 else SNAKE_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=8)
            # inner highlight
            inner = rect.inflate(-8, -8)
            pygame.draw.rect(screen, (60, 210, 80) if i == 0 else (60, 200, 80),
                             inner, border_radius=4)

    def move(self):
        if self.grow:
            self.body.insert(0, self.body[0] + self.direction)
            self.grow = False
        else:
            new_head = self.body[0] + self.direction
            self.body = [new_head] + self.body[:-1]

    def set_direction(self, new_dir):
        # prevent reversing into itself
        if new_dir != -self.direction:
            self.direction = new_dir

    def head(self):
        return self.body[0]

    def check_self_collision(self):
        return self.head() in self.body[1:]

    def check_wall_collision(self):
        h = self.head()
        return not (0 <= h.x < CELL_NUMBER and 0 <= h.y < CELL_NUMBER)


# ── GAME class ───────────────────────────────────────────
class Game:
    def __init__(self):
        self.snake   = Snake()
        self.fruit   = Fruit()
        self.score   = 0
        self.running = True
        self.paused  = False

    def reset(self):
        self.snake   = Snake()
        self.fruit   = Fruit()
        self.score   = 0
        self.running = True
        self.paused  = False

    def update(self):
        if not self.running or self.paused:
            return
        self.snake.move()
        self.check_eat()
        if self.snake.check_self_collision() or self.snake.check_wall_collision():
            self.running = False

    def check_eat(self):
        if self.snake.head() == self.fruit.pos:
            self.snake.grow = True
            self.score += 1
            # make sure fruit doesn't spawn on snake
            while True:
                self.fruit.randomize()
                if self.fruit.pos not in self.snake.body:
                    break

    def draw_grid(self):
        for x in range(CELL_NUMBER):
            pygame.draw.line(screen, GRID_COLOR,
                             (x * CELL_SIZE, 0),
                             (x * CELL_SIZE, SCREEN_SIZE))
        for y in range(CELL_NUMBER):
            pygame.draw.line(screen, GRID_COLOR,
                             (0, y * CELL_SIZE),
                             (SCREEN_SIZE, y * CELL_SIZE))

    def draw_score_bar(self):
        bar_rect = pygame.Rect(0, SCREEN_SIZE, SCREEN_SIZE, 60)
        pygame.draw.rect(screen, SCORE_BG, bar_rect)
        score_surf = font_small.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_surf, (16, SCREEN_SIZE + 18))
        tip = font_small.render("P = Pause   R = Restart", True, (200, 240, 240))
        screen.blit(tip, (SCREEN_SIZE - tip.get_width() - 16, SCREEN_SIZE + 18))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        go   = font_big.render("GAME OVER", True, (255, 80, 160))
        sc   = font_small.render(f"Score: {self.score}", True, TEXT_COLOR)
        rst  = font_small.render("Press R to restart", True, (200, 255, 200))
        screen.blit(go,  go.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2 - 40)))
        screen.blit(sc,  sc.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2 + 10)))
        screen.blit(rst, rst.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2 + 50)))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        p = font_big.render("PAUSED", True, TEXT_COLOR)
        screen.blit(p, p.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2)))


# ── MAIN LOOP ─────────────────────────────────────────────
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP    or event.key == pygame.K_w:
                game.snake.set_direction(Vector2(0, -1))
            if event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                game.snake.set_direction(Vector2(0,  1))
            if event.key == pygame.K_LEFT  or event.key == pygame.K_a:
                game.snake.set_direction(Vector2(-1, 0))
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                game.snake.set_direction(Vector2(1,  0))
            if event.key == pygame.K_r:
                game.reset()
            if event.key == pygame.K_p:
                game.paused = not game.paused

    game.update()

    # ── draw ──────────────────────────────────────────────
    screen.fill(BG_COLOR)
    game.draw_grid()
    game.fruit.draw()
    game.snake.draw()
    game.draw_score_bar()

    if not game.running:
        game.draw_game_over()
    elif game.paused:
        game.draw_pause()

    pygame.display.update()
    clock.tick(FPS)