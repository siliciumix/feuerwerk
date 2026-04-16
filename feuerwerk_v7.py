import tkinter as tk
import math
import random

# ══════════════════════════════════════════════════════════
#  KONFIGURATION
# ══════════════════════════════════════════════════════════
WIDTH, HEIGHT = 960, 660
BG            = "#04040f"

ROCKET_COLORS = ["#ff6644","#ffaa22","#44aaff","#ff44ff","#44ffaa","#ffffff"]
BURST_PALETTE = [
    ["#ff0000","#ff6600","#ffcc00","#ffffff"],
    ["#0055ff","#44aaff","#aaddff","#ffffff"],
    ["#ff00ff","#aa00ff","#ff88ff","#ffffff"],
    ["#00ff88","#00ffcc","#aaffdd","#ffffff"],
    ["#ffff00","#ffcc00","#ff8800","#ffffff"],
    ["#ff2255","#ff6688","#ffaabb","#ffffff"],
]

# ── Pixel-Definitionen für jeden Buchstaben (7×5 Raster) ──
LETTERS = {
    'P': [
        "XXXX.",
        "X...X",
        "XXXX.",
        "X....",
        "X....",
        "X....",
        "X....",
    ],
    'Y': [
        "X...X",
        "X...X",
        ".X.X.",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
    ],
    'T': [
        "XXXXX",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
    ],
    'H': [
        "X...X",
        "X...X",
        "X...X",
        "XXXXX",
        "X...X",
        "X...X",
        "X...X",
    ],
    'O': [
        ".XXX.",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        ".XXX.",
    ],
    'N': [
        "X...X",
        "XX..X",
        "X.X.X",
        "X..XX",
        "X...X",
        "X...X",
        "X...X",
    ],
}

def letter_points(ch, cx, cy, scale=5.0):
    grid = LETTERS.get(ch, [])
    rows = len(grid)
    cols = max(len(r) for r in grid) if grid else 5
    pts  = []
    for row_i, row in enumerate(grid):
        for col_i, cell in enumerate(row):
            if cell == 'X':
                x = cx + (col_i - cols / 2 + 0.5) * scale
                y = cy + (row_i - rows / 2 + 0.5) * scale
                pts.append((x, y))
    return pts

# ══════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════
def dim(color, f):
    f = max(0.0, min(1.0, f))
    r = int(int(color[1:3], 16) * f)
    g = int(int(color[3:5], 16) * f)
    b = int(int(color[5:7], 16) * f)
    return f"#{r:02x}{g:02x}{b:02x}"

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    r = int(int(c1[1:3],16)*(1-t) + int(c2[1:3],16)*t)
    g = int(int(c1[3:5],16)*(1-t) + int(c2[3:5],16)*t)
    b = int(int(c1[5:7],16)*(1-t) + int(c2[5:7],16)*t)
    return f"#{r:02x}{g:02x}{b:02x}"

# ══════════════════════════════════════════════════════════
#  PARTIKEL
# ══════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, vx, vy, color, size=3, life=1.0, grav=0.07):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.size  = size
        self.life  = life
        self.max_life = life
        self.grav  = grav
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.vx *= 0.97
        self.vy  = self.vy * 0.97 + self.grav
        self.x  += self.vx
        self.y  += self.vy
        self.life -= 0.018
        return self.life > 0

    @property
    def alpha(self):
        return max(0.0, self.life / self.max_life)


class LetterParticle:
    def __init__(self, x, y, tx, ty, color):
        self.x, self.y   = float(x), float(y)
        self.tx, self.ty = float(tx), float(ty)
        self.color = color
        angle = math.atan2(ty - y, tx - x) + random.uniform(-0.6, 0.6)
        burst = random.uniform(4, 11)
        self.vx = math.cos(angle) * burst
        self.vy = math.sin(angle) * burst
        self.phase = 0
        self.timer = 0
        self.life  = 1.0
        self.size  = random.uniform(2.5, 4.2)

    def update(self):
        self.timer += 1

        if self.phase == 0:
            dx = self.tx - self.x
            dy = self.ty - self.y
            self.vx += dx * 0.07
            self.vy += dy * 0.07
            self.vx *= 0.78
            self.vy *= 0.78
            self.x  += self.vx
            self.y  += self.vy
            if math.hypot(dx, dy) < 2.5 and math.hypot(self.vx, self.vy) < 0.6:
                self.phase = 1
                self.timer = 0

        elif self.phase == 1:
            self.x = self.tx + random.uniform(-0.5, 0.5)
            self.y = self.ty + random.uniform(-0.5, 0.5)
            if self.timer > 140:
                self.phase = 2

        elif self.phase == 2:
            self.life -= 0.010
            return self.life > 0

        return True

    @property
    def alpha(self):
        if self.phase < 2:
            return 1.0
        return max(0.0, self.life)

# ══════════════════════════════════════════════════════════
#  RAKETE
# ══════════════════════════════════════════════════════════
class Rocket:
    def __init__(self, canvas, start_x, target_x, target_y,
                 letter=None, letter_color=None):
        self.canvas   = canvas
        self.x        = float(start_x)
        self.y        = float(HEIGHT + 10)
        self.tx       = float(target_x)
        self.ty       = float(target_y)
        self.letter   = letter
        self.l_color  = letter_color or "#ffffff"
        self.vx       = (target_x - start_x) / 30.0
        self.vy       = -random.uniform(13, 17)
        self.color    = random.choice(ROCKET_COLORS)
        self.trail    = []
        self.exploded = False

    def update(self, free_parts, letter_parts):
        if self.exploded:
            return False

        self.trail.append((self.x, self.y))
        if len(self.trail) > 16:
            self.trail.pop(0)

        self.vy += 0.22
        self.x  += self.vx
        self.y  += self.vy

        if random.random() < 0.65:
            ang = math.atan2(-self.vy, -self.vx) + random.uniform(-0.35, 0.35)
            spd = random.uniform(0.5, 2.0)
            free_parts.append(Particle(
                self.x, self.y,
                math.cos(ang)*spd, math.sin(ang)*spd,
                random.choice(["#ffcc44","#ff8822","#ffffaa"]),
                size=2, life=0.45, grav=0.03
            ))

        if self.vy >= -0.8 or self.y <= self.ty:
            self.explode(free_parts, letter_parts)
            return False
        return True

    def explode(self, free_parts, letter_parts):
        self.exploded = True

        if self.letter:
            pts = letter_points(self.letter, self.x, self.y, scale=5)
            palette = random.choice(BURST_PALETTE)
            for (tx, ty) in pts:
                col = random.choice(palette)
                letter_parts.append(LetterParticle(self.x, self.y, tx, ty, col))
                if random.random() < 0.5:
                    letter_parts.append(LetterParticle(
                        self.x + random.uniform(-3,3),
                        self.y + random.uniform(-3,3),
                        tx, ty,
                        lerp_color(col, "#ffffff", 0.4)
                    ))
            # Kern-Burst
            for i in range(40):
                ang = 2*math.pi*i/40 + random.uniform(-0.1,0.1)
                spd = random.uniform(1.5, 5)
                free_parts.append(Particle(
                    self.x, self.y,
                    math.cos(ang)*spd, math.sin(ang)*spd,
                    "#ffffff", size=2,
                    life=random.uniform(0.3, 0.6), grav=0.05
                ))
        else:
            pal = random.choice(BURST_PALETTE)
            for i in range(110):
                ang = 2*math.pi*i/110 + random.uniform(-0.1,0.1)
                spd = random.uniform(2, 8)
                free_parts.append(Particle(
                    self.x, self.y,
                    math.cos(ang)*spd, math.sin(ang)*spd,
                    random.choice(pal),
                    size=random.randint(2,4),
                    life=random.uniform(0.7,1.2),
                    grav=random.uniform(0.04,0.09)
                ))
            for i in range(25):
                ang = 2*math.pi*i/25
                spd = random.uniform(1, 3)
                free_parts.append(Particle(
                    self.x, self.y,
                    math.cos(ang)*spd, math.sin(ang)*spd,
                    "#ffffff", size=2,
                    life=random.uniform(0.2,0.5), grav=0.03
                ))

# ══════════════════════════════════════════════════════════
#  HAUPT-APP
# ══════════════════════════════════════════════════════════
class App:
    TEXT    = "PYTHON"
    N_LETT  = len(TEXT)
    LETTER_Y = HEIGHT // 2 - 20
    LETTER_COLORS = [
        "#ff4444", "#ff9900", "#ffee00",
        "#44ff88", "#44aaff", "#dd44ff",
    ]

    def __init__(self, root):
        self.root = root
        root.title("🎆  P Y T H O N  🎆")
        root.resizable(False, False)

        self.cv = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                            bg=BG, highlightthickness=0)
        self.cv.pack()

        self._draw_stars()

        self.fade = self.cv.create_rectangle(
            0, 0, WIDTH, HEIGHT,
            fill=BG, stipple="gray25", outline=""
        )

        self.free_parts   = []
        self.letter_parts = []
        self.rockets      = []

        self.frame        = 0
        self.next_letter  = 0
        self.letter_interval = 55
        self.deco_phase   = True
        self.deco_end     = 90

        spacing = 115
        start_x = WIDTH//2 - (self.N_LETT-1)*spacing//2
        self.letter_xs = [start_x + i*spacing for i in range(self.N_LETT)]

        self._animate()

    def _draw_stars(self):
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            r = random.choice([0.5, 1, 1, 1.5])
            c = random.choice(["#ffffff","#aaaaff","#ffeecc","#cceeff"])
            self.cv.create_oval(x-r, y-r, x+r, y+r, fill=c, outline="")

    def _launch_deco(self):
        cx = WIDTH//2
        tx = cx + random.uniform(-300, 300)
        ty = random.uniform(HEIGHT*0.15, HEIGHT*0.45)
        sx = random.uniform(100, WIDTH-100)
        self.rockets.append(Rocket(self.cv, sx, tx, ty))

    def _launch_letter(self, idx):
        tx  = self.letter_xs[idx]
        ty  = self.LETTER_Y
        sx  = tx + random.uniform(-80, 80)
        ch  = self.TEXT[idx]
        col = self.LETTER_COLORS[idx]
        self.rockets.append(Rocket(self.cv, sx, tx, ty,
                                   letter=ch, letter_color=col))

    def _animate(self):
        self.frame += 1
        f = self.frame

        if self.deco_phase:
            if f % 30 == 0:
                self._launch_deco()
            if f >= self.deco_end:
                self.deco_phase = False

        if not self.deco_phase and self.next_letter < self.N_LETT:
            elapsed = f - self.deco_end
            due = self.next_letter * self.letter_interval
            if elapsed >= due:
                self._launch_letter(self.next_letter)
                self.next_letter += 1

        if not self.deco_phase and f % 80 == 0 and random.random() < 0.5:
            self._launch_deco()

        self.cv.delete("dyn")

        alive_r = []
        for r in self.rockets:
            ok = r.update(self.free_parts, self.letter_parts)
            if ok:
                for j in range(len(r.trail)-1):
                    t = j / max(1, len(r.trail)-1)
                    x1,y1 = r.trail[j]
                    x2,y2 = r.trail[j+1]
                    self.cv.create_line(
                        x1,y1,x2,y2,
                        fill=dim(r.color, t*0.9), width=2, tags="dyn"
                    )
                self.cv.create_oval(
                    r.x-3, r.y-3, r.x+3, r.y+3,
                    fill="#ffffff", outline="", tags="dyn"
                )
                alive_r.append(r)
        self.rockets = alive_r

        alive_p = []
        for p in self.free_parts:
            if p.update():
                c = dim(p.color, p.alpha)
                s = max(1, p.size * p.alpha)
                if len(p.trail) >= 2:
                    x0,y0 = p.trail[-2]
                    self.cv.create_line(
                        x0,y0, p.x,p.y,
                        fill=dim(p.color, p.alpha*0.35),
                        width=max(1,int(s)), tags="dyn"
                    )
                self.cv.create_oval(
                    p.x-s, p.y-s, p.x+s, p.y+s,
                    fill=c, outline="", tags="dyn"
                )
                alive_p.append(p)
        self.free_parts = alive_p

        alive_l = []
        for lp in self.letter_parts:
            if lp.update():
                a   = lp.alpha
                col = dim(lp.color, a)
                s   = max(1.0, lp.size * (0.6 + 0.4*a))
                gs  = s * 2.4
                self.cv.create_oval(
                    lp.x-gs, lp.y-gs, lp.x+gs, lp.y+gs,
                    fill=dim(lp.color, a*0.22), outline="", tags="dyn"
                )
                self.cv.create_oval(
                    lp.x-s, lp.y-s, lp.x+s, lp.y+s,
                    fill=col, outline="", tags="dyn"
                )
                alive_l.append(lp)
        self.letter_parts = alive_l

        self.cv.tag_raise(self.fade)
        self.cv.tag_raise("dyn")

        self.root.after(16, self._animate)


# ══════════════════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()