from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.clock import Clock
from math import sin, cos, radians, sqrt, pi, atan2

# ============================================================
#   AnimatedDrawer = Canvas drawing + Turtle-like animation
# ============================================================

class AnimatedDrawer(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # zoom & pan
        self.scale_value = 1
        self.pan_x = 0
        self.pan_y = 0

        self.bind(size=self.center_canvas)
        self.center_canvas()

        # Animation
        self.commands = []
        self.cmd_index = 0
        self.anim_speed = 0.5  # default speed

        # State for drawing
        self.x = -200
        self.y = 0
        self.heading = 0

        # store points A,B,C,D...
        self.marks = {}

        Clock.schedule_once(self.start_sequence, 0.5)

    # ------------------------------------------------------------
    # Coordinate transform (apply zoom + pan)
    # ------------------------------------------------------------
    def tx(self, x):
        return self.center_x + (x * self.scale_value) + self.pan_x

    def ty(self, y):
        return self.center_y + (y * self.scale_value) + self.pan_y

    # ------------------------------------------------------------
    # Auto-center canvas
    # ------------------------------------------------------------
    def center_canvas(self, *a):
        self.center_x = self.width / 2
        self.center_y = self.height / 2

    # ------------------------------------------------------------
    # TOUCH: Pinch zoom + drag
    # ------------------------------------------------------------
    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches = getattr(self, "_touches", [])
        self._touches.append(touch)
        if len(self._touches) == 2:
            t1, t2 = self._touches
            self.initial_dist = sqrt((t2.x - t1.x) ** 2 + (t2.y - t1.y) ** 2)
            self.initial_scale = self.scale_value

    def on_touch_move(self, touch):
        if len(self._touches) == 1:
            # PAN
            self.pan_x += touch.dx
            self.pan_y += touch.dy

        elif len(self._touches) == 2:
            # PINCH ZOOM
            t1, t2 = self._touches
            new_dist = sqrt((t2.x - t1.x) ** 2 + (t2.y - t1.y) ** 2)
            zoom = new_dist / self.initial_dist
            self.scale_value = self.initial_scale * zoom

    def on_touch_up(self, touch):
        if touch in self._touches:
            self._touches.remove(touch)

    # ------------------------------------------------------------
    # MOVEMENT
    # ------------------------------------------------------------
    def goto(self, x, y):
        nx, ny = self.tx(x), self.ty(y)
        ox, oy = self.tx(self.x), self.ty(self.y)
        with self.canvas:
            Color(0, 0, 0)
            Line(points=[ox, oy, nx, ny], width=1)
        self.x, self.y = x, y

    def forward(self, d):
        ang = radians(self.heading)
        nx = self.x + d * cos(ang)
        ny = self.y + d * sin(ang)
        self.goto(nx, ny)

    def left(self, deg):
        self.heading += deg

    def dot(self, size, r, g, b):
        with self.canvas:
            Color(r, g, b)
            Ellipse(pos=(self.tx(self.x)-size/2, self.ty(self.y)-size/2),
                    size=(size, size))

    # ------------------------------------------------------------
    # Write label (Kivy: small text)
    # ------------------------------------------------------------
    def write(self, text, size=10):
        pass  # optional: Kivy labels can be added; skipping to keep simple

    # ------------------------------------------------------------
    # Add a command
    # ------------------------------------------------------------
    def add(self, cmd):
        self.commands.append(cmd)

    # ------------------------------------------------------------
    # Start drawing sequence
    # ------------------------------------------------------------
    def start_sequence(self, *args):
        self.prepare_commands()
        Clock.schedule_interval(self.run_command, self.anim_speed)

    # ------------------------------------------------------------
    # Execute next command each frame
    # ------------------------------------------------------------
    def run_command(self, dt):
        if self.cmd_index >= len(self.commands):
            return

        cmd = self.commands[self.cmd_index]
        self.cmd_index += 1

        action = cmd[0]

        if action == "goto":
            _, x, y = cmd
            self.goto(x, y)

        elif action == "forward":
            _, d = cmd
            self.forward(d)

        elif action == "left":
            _, ang = cmd
            self.left(ang)

        elif action == "mark":
            _, name = cmd
            self.marks[name] = (self.x, self.y)

        elif action == "goto_mark":
            _, name = cmd
            x, y = self.marks[name]
            self.goto(x, y)

        elif action == "dot":
            _, size, r, g, b = cmd
            self.dot(size, r, g, b)

    # ------------------------------------------------------------
    # Convert your entire Turtle logic into Kivy commands
    # ------------------------------------------------------------
    def prepare_commands(self):
        length = 100
        n = 6

        # A
        self.x, self.y = -200, 0
        self.add(("mark", "A"))

        # AB (blue)
        for _ in range(50):
            self.add(("forward", length/50))
        self.add(("mark", "B"))

        # BC
        self.add(("left", 90))
        for _ in range(50):
            self.add(("forward", length/50))
        self.add(("mark", "C"))

        # Red circle (smooth)
        self.x, self.y = self.marks["B"]
        self.heading = 0
        radius = length
        steps = 180
        step_len = 2 * pi * radius / steps
        step_ang = 360 / steps

        for _ in range(steps):
            self.add(("forward", step_len))
            self.add(("left", step_ang))

        # You can continue converting ALL your other shapes here
        # (vertical points, polygon, labels, etc.)

        # For demonstration, draw polygon:
        A = self.marks["A"]
        Ax, Ay = A
        Cx = Ax + length/2
        Cy = Ay + length
        center = (Cx, Cy)
        r = sqrt((Cx - Ax)**2 + (Cy - Ay)**2)

        px, py = center

        # Move to circle bottom
        self.add(("goto", px, py - r))
        self.heading = 0

        # Polygon points
        step_ang = 360/n
        ang0 = 90
        for i in range(n+1):
            ang = radians(ang0 + i*step_ang)
            x = px + r * cos(ang)
            y = py + r * sin(ang)
            self.add(("goto", x, y))


# ============================================================
#   APP
# ============================================================
class DrawApp(App):
    def build(self):
        return AnimatedDrawer()


DrawApp().run()
