from js import document, window
from pyodide.ffi import create_proxy
import math

# ----------------------------
# CANVAS
# ----------------------------

canvas = document.querySelector("#gameCanvas")
ctx = canvas.getContext("2d")

GRID_SIZE = 25
CELL_SIZE = 30

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
    "Single": [(0,0)],
    "Domino": [(0,0),(1,0)],
    "L3": [(0,0),(0,1),(1,1)],
    "T4": [(1,0),(0,1),(1,1),(2,1)],
    "L4": [(0,0),(0,1),(0,2),(1,2)],
    "Z4": [(0,0),(1,0),(1,1),(2,1)],
    "Plus": [(1,0),(0,1),(1,1),(2,1),(1,2)],
    "Long5": [(0,0),(1,0),(2,0),(3,0),(4,0)],
}

selected_piece = None
rotation = 0
flipped = False

mouse_x = 0
mouse_y = 0

# ----------------------------
# RESIZE
# ----------------------------

def resize_canvas():
    dpr = window.devicePixelRatio or 1
    canvas.style.width = "100vw"
    canvas.style.height = "100vw"
    canvas.width = int(canvas.clientWidth * dpr)
    canvas.height = int(canvas.clientHeight * dpr)
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

resize_canvas()

# ----------------------------
# PIECES
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

def draw():
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

    if selected_piece and game_started:
        piece = get_piece()

        gx = math.floor(mouse_x / CELL_SIZE)
        gy = math.floor(mouse_y / CELL_SIZE)

        ctx.globalAlpha = 0.5
        color = players[current_player]["color"]

        for px, py in piece:
            x = (gx + px) * CELL_SIZE
            y = (gy + py) * CELL_SIZE
            ctx.fillStyle = color
            ctx.fillRect(x+2, y+2, CELL_SIZE-4, CELL_SIZE-4)

        ctx.globalAlpha = 1.0

# ----------------------------
# UI
# ----------------------------

def update_ui():
    overlay = document.getElementById("pieceList")
    overlay.innerHTML = ""

    if not game_started:
        title = document.createElement("div")
        title.innerText = "Select Players"
        overlay.appendChild(title)

        def start(n):
            def handler(e):
                global players, game_started
                players = ALL_PLAYERS[:n]
                game_started = True
                update_ui()
            return handler

        for i in range(2, 5):
            btn = document.createElement("button")
            btn.innerText = f"{i} Players"
            btn.addEventListener("click", create_proxy(start(i)))
            overlay.appendChild(btn)

        return

    for name in pieces:
        div = document.createElement("div")
        div.className = "piece-item"
        div.innerText = name

        def make(n):
            def handler(e):
                global selected_piece, rotation, flipped
                selected_piece = pieces[n]
                rotation = 0
                flipped = False
            return handler

        div.addEventListener("click", create_proxy(make(name)))
        overlay.appendChild(div)

# ----------------------------
# INPUT
# ----------------------------

def get_pos(event):
    rect = canvas.getBoundingClientRect()
    t = event.touches[0] if event.touches else event
    return t.clientX - rect.left, t.clientY - rect.top

def pointer_move(e):
    global mouse_x, mouse_y
    mouse_x, mouse_y = get_pos(e)
    draw()

def pointer_down(e):
    if not game_started or not selected_piece:
        return

    x, y = get_pos(e)

    gx = math.floor(x / CELL_SIZE)
    gy = math.floor(y / CELL_SIZE)

    piece = get_piece()

    if can_place(piece, gx, gy):
        place(piece, gx, gy)

    draw()

# ----------------------------
# CONTROLS
# ----------------------------

def rotate_handler(e):
    global rotation
    rotation = (rotation + 1) % 4
    draw()

def flip_handler(e):
    global flipped
    flipped = not flipped
    draw()

# ----------------------------
# BIND EVENTS
# ----------------------------

canvas.addEventListener("mousemove", create_proxy(pointer_move))
canvas.addEventListener("mousedown", create_proxy(pointer_down))
canvas.addEventListener("touchmove", create_proxy(pointer_move))
canvas.addEventListener("touchstart", create_proxy(pointer_down))

document.getElementById("rotateBtn").addEventListener("click", create_proxy(rotate_handler))
document.getElementById("flipBtn").addEventListener("click", create_proxy(flip_handler))

# ----------------------------
# INIT
# ----------------------------

update_ui()
draw()