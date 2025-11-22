import tkinter as tk
from tkinter import simpledialog
import turtle
import math

# ------------------- Main Window -------------------
root = tk.Tk()
root.title("Turtle Drawing Game")
root.geometry("1000x700")
root.configure(bg="#111133")

# Globals
turtle_screen = None
t = None
turtle_canvas = None

_anim_after_id = None
_commands = []
_cmd_index = 0

# base delay = 60 ms (Option A)
_delay_ms = 60
_step_scale = 1

_runtime_marks = {}    # stores A, B, C etc.


# ------------------- UI: Start Screen -------------------
def show_start_screen():
    global turtle_screen, t, _anim_after_id, _runtime_marks
    if _anim_after_id is not None:
        try:
            root.after_cancel(_anim_after_id)
        except:
            pass
        _anim_after_id = None

    if turtle_screen is not None:
        try:
            turtle_screen.clear()
        except:
            pass
        turtle_screen = None

    t = None
    _runtime_marks = {}

    for w in root.winfo_children():
        w.destroy()

    frame = tk.Frame(root, bg="#111133")
    frame.pack(expand=True, fill="both")

    title = tk.Label(frame, text="TURTLE\nDRAWING GAME", font=("Arial", 46, "bold"),
                     fg="#00ffff", bg="#111133")
    title.pack(pady=60)

    btn = tk.Button(frame, text="START GAME", font=("Arial", 28, "bold"),
                    bg="#00aaff", fg="white",
                    width=18, height=2,
                    command=show_game_screen)
    btn.pack(pady=20)


# ------------------- UI: Game Screen -------------------
def show_game_screen():
    for w in root.winfo_children():
        w.destroy()

    # Top bar
    top = tk.Frame(root, bg="#222255")
    top.pack(fill="x")

    tk.Label(top, text="Your Awesome Turtle Drawing",
             font=("Arial", 20), fg="#00ffff", bg="#222255").pack(side="left", padx=12, pady=8)

    tk.Button(top, text="BACK", font=("Arial", 12), bg="#ff5555", fg="white",
              command=show_start_screen).pack(side="right", padx=8, pady=8)

    tk.Button(top, text="CLEAR", font=("Arial", 12), bg="#ffaa00", fg="white",
              command=clear_drawing).pack(side="right", padx=8, pady=8)

    # Canvas
    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True, padx=12, pady=12)

    global turtle_canvas
    turtle_canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
    turtle_canvas.pack(fill="both", expand=True)

    root.update_idletasks()
    turtle_canvas.update()

    setup_turtle()

    # ------------------- USER INPUTS -------------------
    length = simpledialog.askfloat(
        "Length",
        "Enter length (Recommended 100):",
        initialvalue=100.0,
        minvalue=1.0,
        parent=root
    )
    if length is None:
        show_start_screen()
        return

    n = simpledialog.askinteger(
        "Polygon Sides",
        "Enter number of sides:",
        initialvalue=4,
        minvalue=3,
        parent=root
    )
    if n is None:
        show_start_screen()
        return

    # NEW: turtle speed box
    speed = simpledialog.askinteger(
        "Turtle Speed",
        "Enter speed (1 slow → 10 fast):",
        initialvalue=5,
        minvalue=1,
        maxvalue=10,
        parent=root
    )
    if speed is None:
        speed = 5

    set_speed(speed)

    # World = pixel mapping
    try:
        cw = turtle_canvas.winfo_width()
        ch = turtle_canvas.winfo_height()
        turtle_screen.setworldcoordinates(-cw/2, -ch/2, cw/2, ch/2)
        turtle_screen.update()
    except:
        pass

    prepare_commands(length, n)
    start_animation()


# ------------------- Apply Speed -------------------
def set_speed(speed):
    global _delay_ms, _step_scale
    _delay_ms = int(60 / speed)
    _step_scale = speed


# ------------------- Turtle Setup -------------------
def setup_turtle():
    global turtle_screen, t
    if turtle_screen is None:
        turtle_screen = turtle.TurtleScreen(turtle_canvas)
        turtle_screen.bgcolor("white")
        turtle_screen.tracer(0)

    if t is None:
        t = turtle.RawTurtle(turtle_screen)
        t.speed(0)
        t.width(2)
        t.showturtle()
        t.penup()
        t.home()
        t.pendown()


# --------------- Micro-step helpers -----------------
def micro_forward_steps(dist):
    global _step_scale
    step = 4 * _step_scale
    steps = int(abs(dist) / step)
    if steps < 1:
        return [("forward", dist)]
    real_step = dist / steps
    return [("forward", real_step)] * steps


def micro_line_to(target):
    return [("goto", target)]


# ------------------- Build Commands -------------------
def prepare_commands(length, n):
    global _commands, _cmd_index, _runtime_marks
    _commands = []
    _cmd_index = 0
    _runtime_marks = {}

    # A
    _commands += [
        ("penup", None),
        ("goto", (-200, 0)),
        ("mark", "A"),
        ("pendown", None)
    ]

    # AB blue
    _commands.append(("color", "blue"))
    _commands += micro_forward_steps(length)
    _commands.append(("mark", "B"))

    # BC
    _commands.append(("left", 90))
    _commands += micro_forward_steps(length)
    _commands.append(("mark", "C"))

    # go to A
    _commands += [("penup", None), ("goto_mark", "A"), ("pendown", None)]

    # go to B
    _commands += [("penup", None), ("goto_mark", "B"), ("setheading", 0)]
    _commands.append(("color", "white"))
    _commands += micro_forward_steps(length)
    _commands.append(("left", 90))
    _commands.append(("color", "black"))
    _commands.append(("pendown", None))
    _commands.append(("mark", "D"))

    # ------------------- RED CIRCLE (smooth + 3× faster) -------------------
    _commands.append(("color", "red"))
    cw = turtle_canvas.winfo_width()
    ch = turtle_canvas.winfo_height()

    seg = max(120, int(min(cw, ch) * 0.9 // 3))
    circumference = 2 * math.pi * length
    step_f = circumference / seg
    step_t = 360 / seg

    for _ in range(seg):
        _commands.append(("forward", step_f))
        _commands.append(("left", step_t))

    # E point
    _commands += [
        ("penup", None), ("goto_mark", "A"), ("setheading", 0),
        ("pendown", None)
    ]
    _commands += micro_forward_steps(length / 2)
    _commands.append(("mark", "E"))

    # F
    _commands.append(("left", 90))
    _commands.append(("mark", "F"))
    _commands += micro_forward_steps(2 * length)
    _commands += micro_forward_steps(length)

    # SMALL LABELS (10px)
    _commands.append(("write_label_at_mark", ("A", -10, -30, 10)))
    _commands.append(("write_label_at_mark", ("B", 0, -30, 10)))
    _commands.append(("write_label_at_mark", ("C", -10, 10, 10)))
    _commands.append(("write_label_at_mark", ("D", 5, -30, 10)))
    _commands.append(("write_label_at_mark", ("E", -10, -30, 10)))

    # Vertical points
    A = (-200, 0)
    Ax, Ay = A

    xv = Ax + length / 2
    p4 = (xv, length * 0.5)
    p6 = (xv, length * math.sqrt(3) / 2)
    p5 = (xv, (p4[1] + p6[1]) / 2)
    d = p5[1] - p4[1]
    p3 = (xv, p4[1] - d)

    points = {3: p3, 4: p4, 5: p5, 6: p6}

    y = p6[1]
    label = 7
    for _ in range(n + 2):
        y += d
        points[label] = (xv, y)
        label += 1

    colors = ["blue","orange","green","purple","magenta","cyan","yellow",
              "pink","brown","gray","olive","teal","navy","maroon"]

    # draw points (10 px labels)
    for lbl in sorted(points.keys()):
        px, py = points[lbl]
        _commands += [
            ("penup", None),
            ("goto", (px, py)),
            ("pendown", None),
            ("dot", (6, colors[(lbl - 3) % len(colors)])),
            ("penup", None),
            ("goto", (px, py - 30)),
            ("write_text", (str(lbl), 10))
        ]

    # connect them
    sorted_pts = [p for _, p in sorted(points.items(), key=lambda x: x[1][1])]

    _commands.append(("penup", None))
    _commands.append(("goto", sorted_pts[0]))
    _commands.append(("pendown", None))
    _commands.append(("color", "gray"))

    for pt in sorted_pts[1:]:
        _commands.append(("goto", pt))

    _commands.append(("penup", None))
    _commands.append(("color", "black"))

    # store
    for lbl, pt in points.items():
        _commands.append(("set_runtime_mark", (str(lbl), pt)))

    # center
    center = points[n]
    radius = math.hypot(center[0] - Ax, center[1] - Ay)

    cx, cy = center

    # ------------------- MAGENTA CIRCLE (smooth + 3× faster) -------------------
    seg2 = max(120, int(min(cw, ch) * 0.9 // 3))
    circ2 = 2 * math.pi * radius
    step_f2 = circ2 / seg2
    step_t2 = 360 / seg2

    _commands += [
        ("penup", None), ("goto", (cx, cy - radius)), ("setheading", 0),
        ("pendown", None), ("color", "magenta")
    ]

    for _ in range(seg2):
        _commands.append(("forward", step_f2))
        _commands.append(("left", step_t2))

    _commands.append(("penup", None))
    _commands.append(("goto", (cx - 25, cy + radius + 10)))
    _commands.append(("write_text", (f"{n}-sided polygon", 10)))

    # polygon points
    dx = Ax - cx
    dy = Ay - cy
    start_angle = math.degrees(math.atan2(dy, dx))
    if start_angle < 0:
        start_angle += 360

    step_ang = 360 / n
    poly = []

    for i in range(n):
        ang = start_angle + i * step_ang
        rad = math.radians(ang)
        px = cx + radius * math.cos(rad)
        py = cy + radius * math.sin(rad)
        poly.append((px, py))

        lbl = "A" if i == 0 else f"P{i}"

        _commands += [
            ("penup", None),
            ("goto", (px, py)),
            ("pendown", None),
            ("dot", (8, "red")),
            ("penup", None),
            ("goto", (px, py - 30)),
            ("write_text", (lbl, 9))  # polygon labels 9px
        ]

    # polygon outline
    _commands.append(("penup", None))
    _commands.append(("goto", poly[0]))
    _commands.append(("pendown", None))
    _commands.append(("color", "purple"))
    _commands.append(("pensize", 3))

    for pt in poly[1:]:
        _commands.append(("goto", pt))

    _commands.append(("goto", poly[0]))
    _commands.append(("penup", None))
    _commands.append(("pensize", 4))


# ------------------- Animation Engine -------------------
def start_animation():
    global _anim_after_id
    if _anim_after_id:
        try:
            root.after_cancel(_anim_after_id)
        except:
            pass
    run_next_command()


def run_next_command():
    global _cmd_index, _commands, _anim_after_id, _runtime_marks

    if _cmd_index >= len(_commands):
        _anim_after_id = None
        turtle_screen.update()
        return

    cmd, val = _commands[_cmd_index]
    _cmd_index += 1

    try:
        if cmd == "penup":
            t.penup()
        elif cmd == "pendown":
            t.pendown()
        elif cmd == "goto":
            t.goto(val)
        elif cmd == "goto_mark" and val in _runtime_marks:
            t.goto(_runtime_marks[val])
        elif cmd == "forward":
            t.forward(val)
        elif cmd == "left":
            t.left(val)
        elif cmd == "setheading":
            t.setheading(val)
        elif cmd == "color":
            t.color(val)
        elif cmd == "pensize":
            t.pensize(val)
        elif cmd == "mark":
            _runtime_marks[val] = t.position()
        elif cmd == "set_runtime_mark":
            name, pt = val
            _runtime_marks[name] = pt
        elif cmd == "dot":
            size, color = val
            t.dot(size, color)
        elif cmd == "write_label_at_mark":
            name, ox, oy, fs = val
            if name in _runtime_marks:
                px, py = _runtime_marks[name]
                t.penup()
                t.goto(px + ox, py + oy)
                t.write(name, font=("Arial", fs, "bold"))
                t.penup()
        elif cmd == "write_text":
            text, fs = val
            t.write(text, font=("Arial", fs, "bold"), align="center")
            t.penup()

    except:
        pass

    turtle_screen.update()
    _anim_after_id = root.after(_delay_ms, run_next_command)


# ------------------- Clear -------------------
def clear_drawing():
    global _anim_after_id, _cmd_index, _commands, _runtime_marks
    if _anim_after_id:
        try:
            root.after_cancel(_anim_after_id)
        except:
            pass
    _anim_after_id = None
    if t:
        t.clear()
        t.penup()
        t.home()
        t.pendown()

    _commands = []
    _cmd_index = 0
    _runtime_marks = {}


# ------------------- Start App -------------------
show_start_screen()
root.mainloop()
