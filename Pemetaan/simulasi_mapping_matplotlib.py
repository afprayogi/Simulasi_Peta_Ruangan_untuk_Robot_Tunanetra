import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from matplotlib.lines import Line2D

CELL_SIZE = 20  # Grid lebih besar

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

def generate_connected_rooms(
    room_count=5,
    min_size=6,
    max_size=12,
    obstacle_prob=0.2,
    min_wall_count=2,
    max_wall_count=5,
):
    fig, ax = plt.subplots(figsize=(14, 12))
    placed_rooms = []
    room_grid_map = {}
    directions = ['right', 'left', 'top', 'bottom']
    blocked_cells = set()
    robot_start = None
    exit_door_placed = False
    esp_points = []

    start_x, start_y = 50, 50
    w = random.randint(min_size, max_size)
    h = random.randint(min_size, max_size)
    placed_rooms.append((start_x, start_y, w, h))
    room_grid_map[(start_x, start_y)] = (w, h)

    for _ in range(room_count - 1):
        for _ in range(100):
            base_x, base_y, base_w, base_h = random.choice(placed_rooms)
            dir = random.choice(directions)
            new_w = random.randint(min_size, max_size)
            new_h = random.randint(min_size, max_size)

            if dir == 'right':
                new_x = base_x + base_w
                new_y = base_y
            elif dir == 'left':
                new_x = base_x - new_w
                new_y = base_y
            elif dir == 'top':
                new_x = base_x
                new_y = base_y + base_h
            else:
                new_x = base_x
                new_y = base_y - new_h

            occupied = False
            for ox, oy in room_grid_map.keys():
                ow, oh = room_grid_map[(ox, oy)]
                if not (new_x + new_w <= ox or ox + ow <= new_x or
                        new_y + new_h <= oy or oy + oh <= new_y):
                    occupied = True
                    break
            if not occupied:
                placed_rooms.append((new_x, new_y, new_w, new_h))
                room_grid_map[(new_x, new_y)] = (new_w, new_h)
                break

    exit_room_index = random.randint(0, len(placed_rooms) - 1)

    for idx, (x, y, w, h) in enumerate(placed_rooms):
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        room_w = w * CELL_SIZE
        room_h = h * CELL_SIZE

        ax.plot([px, px + room_w], [py, py], 'k')
        ax.plot([px, px + room_w], [py + room_h, py + room_h], 'k')
        ax.plot([px, px], [py, py + room_h], 'k')
        ax.plot([px + room_w, px + room_w], [py, py + room_h], 'k')

        for i in range(w + 1):
            ax.plot([px + i * CELL_SIZE] * 2, [py, py + room_h], color='lightgray', linewidth=0.5)
        for j in range(h + 1):
            ax.plot([px, px + room_w], [py + j * CELL_SIZE] * 2, color='lightgray', linewidth=0.5)

        for gx in range(w):
            for gy in range(h):
                if random.random() < obstacle_prob:
                    ox = px + gx * CELL_SIZE
                    oy = py + gy * CELL_SIZE
                    rect = patches.Rectangle((ox, oy), CELL_SIZE, CELL_SIZE, color='gray')
                    ax.add_patch(rect)
                    blocked_cells.add((ox, oy))

        wall_count = random.randint(min_wall_count, max_wall_count)
        for _ in range(wall_count):
            gx = random.randint(0, w - 3)
            gy = random.randint(0, h - 3)
            orientation = random.choice(['h', 'v'])
            wall_w = random.randint(2, 4) if orientation == 'h' else 1
            wall_h = 1 if orientation == 'h' else random.randint(2, 4)

            for dx in range(wall_w):
                for dy in range(wall_h):
                    wx = px + (gx + dx) * CELL_SIZE
                    wy = py + (gy + dy) * CELL_SIZE
                    rect = patches.Rectangle((wx, wy), CELL_SIZE, CELL_SIZE, color='black')
                    ax.add_patch(rect)
                    blocked_cells.add((wx, wy))

        # Titik ESP ditempatkan dekat pintu jika tersedia nanti
        esp_points.append((px, py, w, h))

        if robot_start is None:
            attempts = 0
            while True:
                sx = random.randint(0, w - 1)
                sy = random.randint(0, h - 1)
                sx_px = px + sx * CELL_SIZE
                sy_py = py + sy * CELL_SIZE
                if (sx_px, sy_py) not in blocked_cells:
                    robot_start = (sx_px + CELL_SIZE / 2, sy_py + CELL_SIZE / 2)
                    ax.plot(*robot_start, 'ro')
                    break
                attempts += 1
                if attempts > 1000:
                    print("Gagal mencari titik aman.")
                    break

        if idx == exit_room_index:
            ax.text(px + room_w / 2, py + room_h + 10, "\U0001F3C1 Exit", ha='center', color='red')
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
                    door_x = px - CELL_SIZE / 2
                    door_y = py + random.randint(1, h - 2) * CELL_SIZE
                elif side == 'right':
                    door_x = px + room_w
                    door_y = py + random.randint(1, h - 2) * CELL_SIZE
                elif side == 'top':
                    door_x = px + random.randint(1, w - 2) * CELL_SIZE
                    door_y = py + room_h
                elif side == 'bottom':
                    door_x = px + random.randint(1, w - 2) * CELL_SIZE
                    door_y = py - CELL_SIZE / 2

                rect = patches.Rectangle((door_x, door_y), CELL_SIZE / 2 if side in ['left', 'right'] else CELL_SIZE,
                                         CELL_SIZE if side in ['left', 'right'] else CELL_SIZE / 2, color='red')
                ax.add_patch(rect)
                ax.plot(door_x + CELL_SIZE / 4, door_y + CELL_SIZE / 4, 'bo')  # Titik ESP dekat pintu keluar

    for (x1, y1), (w1, h1) in room_grid_map.items():
        for (x2, y2), (w2, h2) in room_grid_map.items():
            if (x1, y1) == (x2, y2):
                continue
            if y1 == y2 and abs(x1 + w1 - x2) == 0:
                py = y1 * CELL_SIZE + random.randint(1, h1 - 2) * CELL_SIZE
                px = (x1 + w1) * CELL_SIZE
                rect = patches.Rectangle((px, py), CELL_SIZE / 2, CELL_SIZE, color='green')
                ax.add_patch(rect)
                ax.plot(px + CELL_SIZE / 4, py + CELL_SIZE / 2, 'bo')  # ESP dekat pintu antar ruangan
            elif x1 == x2 and abs(y1 + h1 - y2) == 0:
                px = x1 * CELL_SIZE + random.randint(1, w1 - 2) * CELL_SIZE
                py = (y1 + h1) * CELL_SIZE
                rect = patches.Rectangle((px, py), CELL_SIZE, CELL_SIZE / 2, color='green')
                ax.add_patch(rect)
                ax.plot(px + CELL_SIZE / 2, py + CELL_SIZE / 4, 'bo')  # ESP dekat pintu antar ruangan

    all_x = [x for x, y, w, h in placed_rooms] + [x + w for x, y, w, h in placed_rooms]
    all_y = [y for x, y, w, h in placed_rooms] + [y + h for x, y, w, h in placed_rooms]
    min_x = min(all_x) * CELL_SIZE
    max_x = max(all_x) * CELL_SIZE
    min_y = min(all_y) * CELL_SIZE
    max_y = max(all_y) * CELL_SIZE
    padding = CELL_SIZE * 5
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)
    ax.set_aspect('equal')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='ESP Point', markerfacecolor='blue', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Start Robot', markerfacecolor='red', markersize=10),
        Line2D([0], [0], color='green', lw=6, label='Pintu'),
        Line2D([0], [0], color='red', lw=6, label='Pintu Exit'),
        Line2D([0], [0], color='gray', lw=10, label='Halangan'),
        Line2D([0], [0], color='black', lw=10, label='Dinding Kuat'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    ax.set_title("Peta Simulasi Adaptif Robot Tunanetra")
    plt.show()

generate_connected_rooms(room_count=5)
