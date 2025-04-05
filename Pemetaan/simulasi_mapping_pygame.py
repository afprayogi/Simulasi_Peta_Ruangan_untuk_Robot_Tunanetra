import pygame
import random
import sys

CELL_SIZE = 20
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Peta Simulasi Adaptif Robot Tunanetra")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
big_font = pygame.font.SysFont(None, 30)

def draw_grid(room_rect, color=(200, 200, 200)):
    x, y, w, h = room_rect
    for i in range(w + 1):
        pygame.draw.line(screen, color, (x + i * CELL_SIZE, y), (x + i * CELL_SIZE, y + h * CELL_SIZE), 1)
    for j in range(h + 1):
        pygame.draw.line(screen, color, (x, y + j * CELL_SIZE), (x + w * CELL_SIZE, y + j * CELL_SIZE), 1)

def is_outer_wall(x, y, w, h, all_rooms, direction):
    for rx, ry, rw, rh in all_rooms:
        if (rx, ry, rw, rh) == (x, y, w, h):
            continue
        if direction == 'left' and rx + rw == x and not (ry + rh <= y or y + h <= ry):
            return False
        if direction == 'right' and x + w == rx and not (ry + rh <= y or y + h <= ry):
            return False
        if direction == 'top' and y + h == ry and not (rx + rw <= x or x + w <= rx):
            return False
        if direction == 'bottom' and ry + rh == y and not (rx + rw <= x or x + w <= rx):
            return False
    return True

def draw_legend():
    items = [
        ("ESP Point", (0, 0, 255)),
        ("Start Robot", (255, 0, 0)),
        ("Pintu", (0, 200, 0)),
        ("Pintu Exit", (200, 0, 0)),
        ("Halangan", (120, 120, 120)),
        ("Dinding Kuat", (0, 0, 0)),
    ]
    y = 20
    for label, color in items:
        pygame.draw.rect(screen, color, (20, y, 20, 20))
        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (50, y))
        y += 30

def generate_rooms(room_count=5, min_size=6, max_size=12, obstacle_prob=0.2):
    placed_rooms = []
    room_map = {}
    directions = ['right', 'left', 'top', 'bottom']
    blocked_cells = set()
    robot_start = None
    esp_points = []

    start_x, start_y = 30, 30
    w = random.randint(min_size, max_size)
    h = random.randint(min_size, max_size)
    placed_rooms.append((start_x, start_y, w, h))
    room_map[(start_x, start_y)] = (w, h)

    for _ in range(room_count - 1):
        for _ in range(100):
            bx, by, bw, bh = random.choice(placed_rooms)
            dir = random.choice(directions)
            nw = random.randint(min_size, max_size)
            nh = random.randint(min_size, max_size)

            if dir == 'right':
                nx = bx + bw
                ny = by
            elif dir == 'left':
                nx = bx - nw
                ny = by
            elif dir == 'top':
                nx = bx
                ny = by + bh
            else:
                nx = bx
                ny = by - nh

            conflict = False
            for ox, oy in room_map:
                ow, oh = room_map[(ox, oy)]
                if not (nx + nw <= ox or ox + ow <= nx or ny + nh <= oy or oy + oh <= ny):
                    conflict = True
                    break
            if not conflict:
                placed_rooms.append((nx, ny, nw, nh))
                room_map[(nx, ny)] = (nw, nh)
                break

    screen.fill((255, 255, 255))
    exit_room_index = random.randint(0, len(placed_rooms) - 1)

    for idx, (x, y, w, h) in enumerate(placed_rooms):
        px = x * CELL_SIZE
        py = y * CELL_SIZE

        pygame.draw.rect(screen, (0, 0, 0), (px, py, w * CELL_SIZE, h * CELL_SIZE), 2)
        draw_grid((px, py, w, h))

        # Obstacles
        for gx in range(w):
            for gy in range(h):
                if random.random() < obstacle_prob:
                    ox = px + gx * CELL_SIZE
                    oy = py + gy * CELL_SIZE
                    pygame.draw.rect(screen, (120, 120, 120), (ox, oy, CELL_SIZE, CELL_SIZE))
                    blocked_cells.add((ox, oy))

        # Dinding kuat (dalam ruangan)
        for _ in range(random.randint(2, 5)):
            gx = random.randint(0, w - 3)
            gy = random.randint(0, h - 3)
            orientation = random.choice(['h', 'v'])
            wall_w = random.randint(2, 4) if orientation == 'h' else 1
            wall_h = 1 if orientation == 'h' else random.randint(2, 4)

            for dx in range(wall_w):
                for dy in range(wall_h):
                    wx = px + (gx + dx) * CELL_SIZE
                    wy = py + (gy + dy) * CELL_SIZE
                    pygame.draw.rect(screen, (0, 0, 0), (wx, wy, CELL_SIZE, CELL_SIZE))
                    blocked_cells.add((wx, wy))

        # Titik awal robot
        if robot_start is None:
            for _ in range(1000):
                sx = random.randint(0, w - 1)
                sy = random.randint(0, h - 1)
                sx_px = px + sx * CELL_SIZE
                sy_py = py + sy * CELL_SIZE
                if (sx_px, sy_py) not in blocked_cells:
                    robot_start = (sx_px + CELL_SIZE // 2, sy_py + CELL_SIZE // 2)
                    pygame.draw.circle(screen, (255, 0, 0), robot_start, CELL_SIZE // 3)
                    break

        # Titik ESP
        esp_points.append((px + CELL_SIZE // 2, py + CELL_SIZE // 2))
        pygame.draw.circle(screen, (0, 0, 255), esp_points[-1], CELL_SIZE // 4)

        # Exit room
        if idx == exit_room_index:
            pygame.draw.rect(screen, (255, 255, 255), (px, py - 25, w * CELL_SIZE, 30))
            text = big_font.render("🏁 EXIT", True, (200, 0, 0))
            screen.blit(text, (px + (w * CELL_SIZE) // 2 - 20, py - 20))

            possible_sides = []
            if is_outer_wall(x, y, w, h, placed_rooms, 'left'):
                possible_sides.append('left')
            if is_outer_wall(x, y, w, h, placed_rooms, 'right'):
                possible_sides.append('right')
            if is_outer_wall(x, y, w, h, placed_rooms, 'top'):
                possible_sides.append('top')
            if is_outer_wall(x, y, w, h, placed_rooms, 'bottom'):
                possible_sides.append('bottom')

            if possible_sides:
                side = random.choice(possible_sides)
                if side == 'left':
                    door_x = px - CELL_SIZE // 2
                    door_y = py + random.randint(1, h - 2) * CELL_SIZE
                    pygame.draw.rect(screen, (200, 0, 0), (door_x, door_y, CELL_SIZE // 2, CELL_SIZE))
                    pygame.draw.circle(screen, (0, 0, 255), (door_x + CELL_SIZE // 4, door_y + CELL_SIZE // 2), 4)
                elif side == 'right':
                    door_x = px + w * CELL_SIZE
                    door_y = py + random.randint(1, h - 2) * CELL_SIZE
                    pygame.draw.rect(screen, (200, 0, 0), (door_x, door_y, CELL_SIZE // 2, CELL_SIZE))
                    pygame.draw.circle(screen, (0, 0, 255), (door_x + CELL_SIZE // 4, door_y + CELL_SIZE // 2), 4)
                elif side == 'top':
                    door_x = px + random.randint(1, w - 2) * CELL_SIZE
                    door_y = py + h * CELL_SIZE
                    pygame.draw.rect(screen, (200, 0, 0), (door_x, door_y, CELL_SIZE, CELL_SIZE // 2))
                    pygame.draw.circle(screen, (0, 0, 255), (door_x + CELL_SIZE // 2, door_y + CELL_SIZE // 4), 4)
                elif side == 'bottom':
                    door_x = px + random.randint(1, w - 2) * CELL_SIZE
                    door_y = py - CELL_SIZE // 2
                    pygame.draw.rect(screen, (200, 0, 0), (door_x, door_y, CELL_SIZE, CELL_SIZE // 2))
                    pygame.draw.circle(screen, (0, 0, 255), (door_x + CELL_SIZE // 2, door_y + CELL_SIZE // 4), 4)

    # Pintu antar ruangan
    for (x1, y1), (w1, h1) in room_map.items():
        for (x2, y2), (w2, h2) in room_map.items():
            if (x1, y1) == (x2, y2):
                continue
            if y1 == y2 and abs(x1 + w1 - x2) == 0:
                py = y1 * CELL_SIZE + random.randint(1, h1 - 2) * CELL_SIZE
                px = (x1 + w1) * CELL_SIZE
                pygame.draw.rect(screen, (0, 200, 0), (px, py, CELL_SIZE // 2, CELL_SIZE))
                pygame.draw.circle(screen, (0, 0, 255), (px + CELL_SIZE // 4, py + CELL_SIZE // 2), 4)
            elif x1 == x2 and abs(y1 + h1 - y2) == 0:
                px = x1 * CELL_SIZE + random.randint(1, w1 - 2) * CELL_SIZE
                py = (y1 + h1) * CELL_SIZE
                pygame.draw.rect(screen, (0, 200, 0), (px, py, CELL_SIZE, CELL_SIZE // 2))
                pygame.draw.circle(screen, (0, 0, 255), (px + CELL_SIZE // 2, py + CELL_SIZE // 4), 4)

    draw_legend()
    pygame.display.flip()

def main():
    generate_rooms(room_count=5)
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
