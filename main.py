from js import document


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


def next_piece_handler(event):
    global selected_piece_name
    global selected_piece

    player_name = PLAYERS[current_player]["name"]
    available = remaining_pieces[player_name]

    if not available:
        return

    current_index = available.index(selected_piece_name) if selected_piece_name in available else -1

    next_index = (current_index + 1) % len(available)

    selected_piece_name = available[next_index]
    selected_piece = pieces[selected_piece_name]

    update_ui()
    redraw()


def update_ui():
    document.getElementById(
        "currentPlayer"
    ).innerText = f"Current Player: {PLAYERS[current_player]['name']}"

    piece_list = document.getElementById("pieceList")
    piece_list.innerHTML = ""

    player_name = PLAYERS[current_player]["name"]

    for name in remaining_pieces[player_name]:
        div = document.createElement("div")
        div.className = "piece-item"
        div.innerText = name

        def make_handler(piece_name):
            def handler(event):
                global selected_piece_name
                global selected_piece

                selected_piece_name = piece_name
                selected_piece = pieces[piece_name]
                redraw()

            return handler

        div.addEventListener("click", create_proxy(make_handler(name)))

        piece_list.appendChild(div)


canvas.addEventListener("click", create_proxy(click_handler))
canvas.addEventListener("mousemove", create_proxy(move_handler))

document.getElementById("rotateBtn").addEventListener(
    "click",
    create_proxy(rotate_handler)
)

document.getElementById("flipBtn").addEventListener(
    "click",
    create_proxy(flip_handler)
)


document.getElementById("nextBtn").addEventListener(
    "click",
    create_proxy(next_piece_handler)
)

update_ui()
redraw()