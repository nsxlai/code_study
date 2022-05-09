"""
source: https://www.youtube.com/watch?v=RRYgc4YIhEs&t=380s
Tech with Tim Youtube channel
"""
import pygame
import random
from queue import Queue
import time

pygame.init()


WIDTH, HEIGHT = 700, 800

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

BG_COLOR = 'white'
ROWS, COLS = 10, 10
BOMBS = 15

SIZE = WIDTH / ROWS

NUM_FONT = pygame.font.SysFont('comicsans', 20)
LOST_FONT = pygame.font.SysFont('comicssans', 100)
TIME_FONT = pygame.font.SysFont('comicssans', 50)

NUM_COLORS = {1: 'black', 2: 'green', 3: 'red', 4: 'orange', 5: 'yellow', 6: 'purple', 7: 'blue', 8: 'pink'}

RECT_COLOR = (200, 200, 200)
CLICKED_RECT_COLOR = (140, 140, 140)
FLAG_RECT_COLOR = 'green'
BOMB_COLOR = 'red'


def get_neighbors(row, col, rows, cols):
    neighbors = []

    if row > 0:  # UP
        neighbors.append((row -1, col))
    if row < rows - 1:  # DOWN
        neighbors.append((row + 1, col))
    if col > 0:  # LEFT
        neighbors.append((row, col -1))
    if col < cols - 1:  # RIGHT
        neighbors.append((row, col + 1))

    if row > 0 and col > 0:  # TOP LEFT
        neighbors.append((row - 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))

    return neighbors


def create_mind_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    while len(mine_positions) < mines:
        row = random.randrange(0, rows - 1)
        col = random.randrange(0, cols - 1)
        pos = row, col

        if pos in mine_positions:
            continue

        mine_positions.add(pos)
        field[row][col] = -1

    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != 1:
                field[r][c] += 1

    return field


def draw(win, field, cover_field, current_time):
    win.fill(BG_COLOR)

    time_text = TIME_FONT.render(f'Time Elapsed: {round(current_time)}', 1, 'black')
    win.blit(time_text, (10, HEIGHT - time_text.get_height()))

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = cover_field[i][j] == 0
            is_flag = cover_field[i][j] == -2
            is_bomb = value == -1

            if is_flag :
                pygame.draw.rect(win, FLAG_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, 'black', (x, y, SIZE, SIZE), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, 'black', (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, 'black', (x, y, SIZE, SIZE), 2)
                if is_bomb:
                    pygame.draw.circle(
                        win, BOMB_COLOR, (x + SIZE//2, y + SIZE//2), SIZE//2 - 4)

            if value > 0:
                text = NUM_FONT.render(str(value), 1, NUM_COLORS[value])
                win.blit(text, (x + (SIZE/2 - text.get_width()/2),
                                y + (SIZE/2 - text.get_height()/2)))

    pygame.display.update()


def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)

    return row, col


def uncover_from_pos(row, col, cover_field, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r, c in neighbors:
            if (r, c) in visited:
                continue

            value = field[r][c]
            if value == 0 and cover_field[r][c] != -2:
                q.put((r, c))

            if cover_field[r][c] != -2:
                cover_field[r][c] = 1
            visited.add((r, c))


def draw_lost(win, text):
    text = LOST_FONT.render(text, 1, 'black')
    win.blit(text, (WIDTH/2 - text.get_width()/2,
                    HEIGHT/2 - text.get_width()/2))
    pygame.display.update()


def main():
    run = True
    field = create_mind_field(ROWS, COLS, BOMBS)
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flags = BOMBS
    clicks = 0
    lost = False

    start_time = 0

    while run:
        if start_time > 0:
            current_time = time.time() - start_time
        else:
            current_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue

                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and cover_field[row][col] != -2:
                    cover_field[row][col] = 1

                    if field[row][col] == -1:  # Bomb clicked!
                        lost = True

                    if clicks == 0 or field[row][col] == 0:
                        uncover_from_pos(row, col, cover_field, field)
                    if clicks == 0:
                        start_time = time.time()
                    clicks += 1
                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                        flags += 1
                    else:
                        flags -= 1
                        cover_field[row][col] = -2

        if lost:
            draw(win, field, cover_field)
            draw_lost(win, "You lost! Try again...")
            pygame.time.delay(5000)

            field = create_mind_field(ROWS, COLS, BOMBS)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = BOMBS
            clicks = 0
            lost = False

        draw(win, field, cover_field, current_time)

    pygame.quit()


if __name__ == '__main__':
    main()
