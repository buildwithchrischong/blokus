from js import document
from pyodide.ffi import create_proxy
import math

# ----------------------------
# CANVAS SETUP (must exist in HTML)
# ----------------------------
canvas = document.querySelector("#gameCanvas")

if canvas is None:
    raise Exception("Canvas #gameCanvas not found. Check your index.html")

ctx = canvas.getContext("2d")

# ----------------------------
# GAME CONSTANTS
# ----------------------------
GRID_SIZE = 25
CELL_SIZE = 40

PLAYERS = [
    {"name": "Blue", "color": "#3B82F6"},
    {"name": "Yellow", "color": "#FACC15"},
    {"name": "Red", "color": "#EF4444"},
    {"name": "Green", "color": "#22C55E"},
]

current_player = 0

board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

pieces = {
    "Single": [(0, 0)],
    "Domino": [(0, 0), (1, 0)],
    "L3": [(0, 0), (0, 1), (1, 1)],
    "T4": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "L4": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "Z4": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "Plus": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    "Long5": [(0,0),(1,0),(2,0),(3,0),(4,0)],
}

selected_piece_name = "Single"
selected_piece = pieces[selected_piece_name]
rotation = 0
flipped = False


# ----------------------------
# PIECE TRANSFORMS
# ----------------------------
def rotate_piece(piece):
    return [(-y, x) for x, y in piece]

def flip_piece(piece):
    return [(-x, y) for x, y in piece]

def normalize(piece):
    min_x = min(x for x, y in piece)
    min_y = min(y for x, y in piece)
    return [(x - min_x, y - min_y) for x, y in piece]

def get_transformed_piece():
    p = selected_piece.copy()

    for _ in range(rotation):
        p = rotate_piece(p)

    if flipped:
        p = flip_piece(p)

    return normalize(p)


# ----------------------------
# DRAWING
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
                ctx.fillStyle = PLAYERS[owner]["color"]
                ctx.fillRect(px+2, py+2, CELL_SIZE-4, CELL_SIZE-4)


def redraw(mx=None, my=None):
    draw_board()

    if mx is None:
        return

    piece = get_transformed_piece()

    gx = math.floor(mx / CELL_SIZE)
    gy = math.floor(my / CELL_SIZE)

    color = PLAYERS[current_player]["color"]

    ctx.globalAlpha = 0.5

    for px, py in piece:
        x = (gx + px) * CELL_SIZE
        y = (gy + py) * CELL_SIZE
        ctx.fillStyle = color
        ctx.fillRect(x+2, y+2, CELL_SIZE-4, CELL_SIZE-4)

    ctx.globalAlpha = 1.0


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


def place_piece(piece, gx, gy):
    global current_player

    for px, py in piece:
        board[gy + py][gx + px] = current_player

    current_player = (current_player + 1) % len(PLAYERS)

    update_ui()


# ----------------------------
# HANDLERS (DEFINED FIRST!)
# ----------------------------
def click_handler(event):
    rect = canvas.getBoundingClientRect()

    mx = event.clientX - rect.left
    my = event.clientY - rect.top

    gx = math.floor(mx / CELL_SIZE)
    gy = math.floor(my / CELL_SIZE)

    piece = get_transformed_piece()

    if can_place(piece, gx, gy):
        place_piece(piece, gx, gy)

    redraw(mx, my)


def move_handler(event):
    rect = canvas.getBoundingClientRect()

    mx = event.clientX - rect.left
    my = event.clientY - rect.top

    redraw(mx, my)


def rotate_handler(event):
    global rotation
    rotation = (rotation + 1) % 4
    redraw()


def flip_handler(event):
    global flipped
    flipped = not flipped
    redraw()


# ----------------------------
# UI
# ----------------------------
def update_ui():
    document.getElementById("currentPlayer").innerText = \
        f"Current Player: {PLAYERS[current_player]['name']}"


# ----------------------------
# BIND EVENTS (AFTER FUNCTIONS EXIST)
# ----------------------------
canvas.addEventListener("click", create_proxy(click_handler))
canvas.addEventListener("mousemove", create_proxy(move_handler))

document.getElementById("rotateBtn").addEventListener(
    "click", create_proxy(rotate_handler)
)

document.getElementById("flipBtn").addEventListener(
    "click", create_proxy(flip_handler)
)


# ----------------------------
# START GAME
# ----------------------------
update_ui()
redraw()