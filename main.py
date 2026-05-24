from js import document
from pyodide.ffi import create_proxy
import math

# ----------------------------
# CANVAS
# ----------------------------

canvas = document.querySelector("#gameCanvas")
if canvas is None:
    raise Exception("Canvas #gameCanvas not found")

ctx = canvas.getContext("2d")

# ----------------------------
# GAME STATE
# ----------------------------

GRID_SIZE = 25
CELL_SIZE = 40

ALL_PLAYERS = [
    {"name": "Blue", "color": "#3B82F6"},
    {"name": "Yellow", "color": "#FACC15"},
    {"name": "Red", "color": "#EF4444"},
    {"name": "Green", "color": "#22C55E"},
]

players = []
current_player = 0
game_started = False

board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

pieces = {
    "Single": [(0, 0)],
    "Domino": [(0, 0), (1, 0)],
    "L3": [(0, 0), (0, 1), (1, 1)],
    "T4": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "L4": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "Z4": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "Plus": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    "Long5": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
}

selected_piece = None
rotation = 0
flipped = False

mouse_x = 0
mouse_y = 0

# ----------------------------
# START SCREEN
# ----------------------------

def show_start_screen():
    overlay = document.getElementById("pieceList")
    overlay.innerHTML = ""

    title = document.createElement("div")
    title.innerText = "Select Players (2–4)"
    title.style.fontSize = "20px"
    title.style.marginBottom = "10px"
    overlay.appendChild(title)

    def start_game(n):
        def handler(e):
            global players, game_started
            players = ALL_PLAYERS[:n]
            game_started = True
            update_ui()
        return handler

    for i in range(2, 5):
        btn = document.createElement("button")
        btn.innerText = f"Start {i} Players"
        btn.addEventListener("click", create_proxy(start_game(i)))
        overlay.appendChild(btn)

# ----------------------------
# PIECES TRANSFORMS
# ----------------------------

def rotate(piece):
    return [(-y, x) for x, y in piece]

def flip(piece):
    return [(-x, y) for x, y in piece]

def normalize(piece):
    min_x = min(x for x, y in piece)
    min_y = min(y for x, y in piece)
    return [(x - min_x, y - min_y) for x, y in piece]

def get_piece():
    if not selected_piece:
        return []

    p = selected_piece.copy()

    for _ in range(rotation):
        p = rotate(p)

    if flipped:
        p = flip(p)

    return normalize(p)

# ----------------------------
# GAME LOGIC
# ----------------------------

def can_place(piece, gx, gy):
    for px, py in piece:
        x = gx + px
        y = gy + py

        if x < 0 or y < 0 or x >= GRID_SIZE or y >= GRID_SIZE:
            return False

        if board[y][x] is not None:
            return False

    return True

def place(piece, gx, gy):
    global current_player

    for px, py in piece:
        board[gy + py][gx + px] = current_player

    current_player = (current_player + 1) % len(players)
    update_ui()

# ----------------------------
# DRAW
# ----------------------------

def draw_board():
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            px = x * CELL_SIZE
            py = y * CELL_SIZE

            ctx.strokeStyle = "#333"
            ctx.strokeRect(px, py, CELL_SIZE, CELL_SIZE)

            owner = board[y][x]
            if owner is not None:
                ctx.fillStyle = players[owner]["color"]
                ctx.fillRect(px+2, py+2, CELL_SIZE-4, CELL_SIZE-4)

def draw_piece(piece, gx, gy, color, alpha=0.5):
    ctx.globalAlpha = alpha

    for px, py in piece:
        x = (gx + px) * CELL_SIZE
        y = (gy + py) * CELL_SIZE
        ctx.fillStyle = color
        ctx.fillRect(x+2, y+2, CELL_SIZE-4, CELL_SIZE-4)

    ctx.globalAlpha = 1.0

def redraw():
    draw_board()

    if selected_piece and game_started:
        piece = get_piece()

        gx = math.floor(mouse_x / CELL_SIZE)
        gy = math.floor(mouse_y / CELL_SIZE)

        color = players[current_player]["color"]
        draw_piece(piece, gx, gy, color, 0.5)

# ----------------------------
# INPUT
# ----------------------------

def mouse_move(event):
    global mouse_x, mouse_y

    rect = canvas.getBoundingClientRect()
    mouse_x = event.clientX - rect.left
    mouse_y = event.clientY - rect.top

    redraw()

def click(event):
    global selected_piece

    if not game_started:
        return

    if not selected_piece:
        return

    rect = canvas.getBoundingClientRect()

    gx = math.floor((event.clientX - rect.left) / CELL_SIZE)
    gy = math.floor((event.clientY - rect.top) / CELL_SIZE)

    piece = get_piece()

    if can_place(piece, gx, gy):
        place(piece, gx, gy)

    redraw()

# ----------------------------
# UI
# ----------------------------

def select_piece(name):
    global selected_piece, rotation, flipped

    selected_piece = pieces[name]
    rotation = 0
    flipped = False

def update_ui():
    piece_list = document.getElementById("pieceList")
    piece_list.innerHTML = ""

    if not game_started:
        show_start_screen()
        return

    for name in pieces:
        div = document.createElement("div")
        div.className = "piece-item"
        div.innerText = name

        def make_handler(n):
            def handler(e):
                select_piece(n)
            return handler

        div.addEventListener("click", create_proxy(make_handler(name)))
        piece_list.appendChild(div)

# ----------------------------
# CONTROLS
# ----------------------------

def rotate_handler(event):
    global rotation
    rotation = (rotation + 1) % 4
    redraw()

def flip_handler(event):
    global flipped
    flipped = not flipped
    redraw()

# ----------------------------
# BIND
# ----------------------------

canvas.addEventListener("mousemove", create_proxy(mouse_move))
canvas.addEventListener("click", create_proxy(click))

document.getElementById("rotateBtn").addEventListener("click", create_proxy(rotate_handler))
document.getElementById("flipBtn").addEventListener("click", create_proxy(flip_handler))

# ----------------------------
# INIT
# ----------------------------

update_ui()
redraw()