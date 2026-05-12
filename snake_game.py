import pygame
import random
import sys
import math

WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
BASE_FPS = 10

BG = (12, 12, 20)
GRID_DOT = (30, 30, 50)
BORDER = (50, 55, 75)
SNAKE_HEAD = (50, 225, 80)
SNAKE_BODY = (25, 165, 55)
FOOD = (235, 55, 55)
FOOD_GLOW = (255, 110, 80)
WHITE = (235, 235, 235)
GRAY = (130, 130, 155)
GOLD = (255, 215, 0)

HIGHSCORE_FILE = "highscore.txt"

screen = None
clock = None
font_big = None
font_mid = None
font_sml = None


def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except OSError:
        pass


class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.segments = [(cx, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.grow_pending = 0

    @property
    def head(self):
        return self.segments[0]

    def set_direction(self, d):
        if (d[0] * -1, d[1] * -1) != self.next_dir:
            self.next_dir = d

    def move(self):
        self.direction = self.next_dir
        nx = self.head[0] + self.direction[0]
        ny = self.head[1] + self.direction[1]
        self.segments.insert(0, (nx, ny))
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.segments.pop()
        return (nx, ny)

    def grow(self):
        self.grow_pending += 1

    def collides_self(self, pos):
        return pos in self.segments[1:]

    def collides_wall(self, pos):
        return not (0 <= pos[0] < COLS and 0 <= pos[1] < ROWS)

    def occupies(self):
        return set(self.segments)


class Food:
    def __init__(self, occupied):
        self.pos = self._randomize(occupied)

    def _randomize(self, occupied):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]
        return random.choice(free) if free else (0, 0)


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.circle(screen, GRID_DOT, (x, y), 1)


def draw_snake(snake):
    segs = snake.segments
    for i, (gx, gy) in enumerate(segs):
        cx = gx * CELL_SIZE + CELL_SIZE // 2
        cy = gy * CELL_SIZE + CELL_SIZE // 2
        if i == 0:
            pygame.draw.circle(screen, SNAKE_HEAD, (cx, cy), CELL_SIZE // 2 + 1)
            dx, dy = snake.direction
            if dx == 1:
                eyes = [(4, -4), (4, 4)]
            elif dx == -1:
                eyes = [(-4, -4), (-4, 4)]
            elif dy == -1:
                eyes = [(-4, -4), (4, -4)]
            else:
                eyes = [(-4, 4), (4, 4)]
            for ex, ey in eyes:
                pygame.draw.circle(screen, WHITE, (cx + ex, cy + ey), 3)
                pygame.draw.circle(screen, BG, (cx + ex + dx, cy + ey + dy), 1.5)
        else:
            t = i / len(segs)
            r = int(SNAKE_HEAD[0] * (1 - t) + SNAKE_BODY[0] * t)
            g = int(SNAKE_HEAD[1] * (1 - t) + SNAKE_BODY[1] * t)
            b = int(SNAKE_HEAD[2] * (1 - t) + SNAKE_BODY[2] * t)
            pygame.draw.circle(screen, (r, g, b), (cx, cy), CELL_SIZE // 2 - 2)


def draw_food(food):
    gx, gy = food.pos
    cx = gx * CELL_SIZE + CELL_SIZE // 2
    cy = gy * CELL_SIZE + CELL_SIZE // 2
    pulse = 1 + 0.08 * math.sin(pygame.time.get_ticks() * 0.005)
    r = int((CELL_SIZE // 2 - 2) * pulse)
    pygame.draw.circle(screen, FOOD_GLOW, (cx, cy), r + 4)
    pygame.draw.circle(screen, FOOD, (cx, cy), r)
    pygame.draw.circle(screen, (255, 200, 200), (cx - 3, cy - 3), 3)


def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


class Game:
    PLAYING = 0
    PAUSED = 1
    GAMEOVER = 2

    def __init__(self):
        self.highscore = load_highscore()
        self.snake = Snake()
        self.food = Food(self.snake.occupies())
        self.score = 0
        self.fps = BASE_FPS
        self.state = self.PLAYING

    def start_game(self):
        self.snake = Snake()
        self.food = Food(self.snake.occupies())
        self.score = 0
        self.fps = BASE_FPS
        self.state = self.PLAYING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()

                elif event.key == pygame.K_p and self.state != self.GAMEOVER:
                    self.state = self.PAUSED if self.state == self.PLAYING else self.PLAYING

                elif self.state == self.PLAYING:
                    if event.key == pygame.K_UP:
                        self.snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction((1, 0))

        return True

    def update(self):
        if self.state != self.PLAYING:
            return

        new_head = self.snake.move()

        if self.snake.collides_wall(new_head) or self.snake.collides_self(new_head):
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)
            self.state = self.GAMEOVER
            return

        if new_head == self.food.pos:
            self.snake.grow()
            self.score += 1
            self.fps = min(20, BASE_FPS + self.score // 5)
            self.food = Food(self.snake.occupies())

    def draw(self):
        screen.fill(BG)

        if self.state in (self.PLAYING, self.PAUSED):
            self._draw_game()
            if self.state == self.PAUSED:
                self._draw_pause()
        elif self.state == self.GAMEOVER:
            self._draw_game()
            self._draw_gameover()

        pygame.display.flip()

    def _draw_game(self):
        draw_grid()
        draw_food(self.food)
        draw_snake(self.snake)
        pygame.draw.rect(screen, BORDER, (0, 0, WIDTH, HEIGHT), 2)
        draw_text(f"Score: {self.score}", font_sml, WHITE, 10, 10)
        draw_text(f"Best: {self.highscore}", font_sml, GRAY, WIDTH - 10, 10)

    def _draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", font_big, WHITE, WIDTH // 2, HEIGHT // 2, center=True)
        draw_text("Press P to resume", font_sml, GRAY,
                  WIDTH // 2, HEIGHT // 2 + 45, center=True)

    def _draw_gameover(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        draw_text("GAME OVER", font_big, FOOD, WIDTH // 2, HEIGHT // 3,
                  center=True)
        draw_text(f"Score: {self.score}", font_mid, WHITE,
                  WIDTH // 2, HEIGHT // 2, center=True)
        if self.score >= self.highscore and self.score > 0:
            draw_text("NEW HIGH SCORE!", font_sml, GOLD,
                      WIDTH // 2, HEIGHT // 2 + 38, center=True)
        draw_text("Press SPACE to play again", font_sml, GRAY,
                  WIDTH // 2, HEIGHT // 2 + 75, center=True)
        draw_text("P to pause", font_sml, GRAY,
                  WIDTH // 2, HEIGHT // 2 + 105, center=True)

    def run(self):
        pygame.event.clear()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(self.fps if self.state == self.PLAYING else BASE_FPS)
        pygame.quit()
        sys.exit()


def main():
    global screen, clock, font_big, font_mid, font_sml
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font_big = pygame.font.Font(None, 72)
    font_mid = pygame.font.Font(None, 36)
    font_sml = pygame.font.Font(None, 24)
    Game().run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input(f"\nError: {e}\nPress Enter to exit...")
