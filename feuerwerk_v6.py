import tkinter as tk
import math
import random
import time

# ─────────────────────────────────────────────
#  Konfiguration
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 900, 650
BG_COLOR       = "#050510"
FADE_RECT      = "#050510"   # Nachzieh-Effekt

ROCKET_COLORS  = ["#ff4444", "#ffaa00", "#44aaff", "#ff44ff", "#44ffaa", "#ffffff"]
BURST_PALETTES = [
    ["#ff0000","#ff4400","#ff8800","#ffcc00","#ffffff"],
    ["#0044ff","#0088ff","#44ccff","#aaddff","#ffffff"],
    ["#ff00ff","#cc00ff","#8800ff","#4400ff","#ffffff"],
    ["#00ff88","#00ffcc","#00ccff","#ffffff","#aaffcc"],
    ["#ffff00","#ffcc00","#ff8800","#ff4400","#ffffff"],
    ["#ff4488","#ff0044","#cc0033","#ff88aa","#ffffff"],
]

# ─────────────────────────────────────────────
#  Hilfsfunktionen
# ─────────────────────────────────────────────
def lerp_color(c1, c2, t):
    """Interpoliert zwischen zwei Hex-Farben."""
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"

def dim_color(hex_color, factor):
    """Abdunkelt eine Farbe um factor (0-1)."""
    r = int(int(hex_color[1:3],16) * factor)
    g = int(int(hex_color[3:5],16) * factor)
    b = int(int(hex_color[5:7],16) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"

# ─────────────────────────────────────────────
#  Partikel
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, color, size=3, life=1.0, gravity=0.07):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.color       = color
        self.size        = size
        self.life        = life
        self.max_life    = life
        self.gravity     = gravity
        self.id          = None
        self.trail       = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.vx *= 0.97
        self.vy  = self.vy * 0.97 + self.gravity
        self.x  += self.vx
        self.y  += self.vy
        self.life -= 0.018
        return self.life > 0

    @property
    def alpha(self):
        return max(0, self.life / self.max_life)

# ─────────────────────────────────────────────
#  Rakete
# ─────────────────────────────────────────────
class Rocket:
    def __init__(self, canvas, target_x, target_y):
        self.canvas    = canvas
        self.x         = target_x + random.uniform(-60, 60)
        self.y         = HEIGHT + 20
        self.target_x  = target_x
        self.target_y  = target_y
        self.vx        = (target_x - self.x) / 28
        self.vy        = -random.uniform(14, 18)
        self.color     = random.choice(ROCKET_COLORS)
        self.trail     = []
        self.exploded  = False
        self.ids       = []
        self.spark_ids = []

    def update(self, particles):
        if self.exploded:
            return False

        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        self.vy += 0.25
        self.x  += self.vx
        self.y  += self.vy

        # Funken-Schweif
        if random.random() < 0.6:
            angle = math.atan2(-self.vy, -self.vx) + random.uniform(-0.4, 0.4)
            spd   = random.uniform(0.5, 2.0)
            particles.append(Particle(
                self.x, self.y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                random.choice(["#ffcc44","#ff8822","#ffffff"]),
                size=2, life=0.5, gravity=0.04
            ))

        # Explosion, wenn Höhepunkt erreicht
        if self.vy >= -1.0 or self.y <= self.target_y:
            self.explode(particles)
            return False
        return True

    def explode(self, particles):
        self.exploded = True
        palette = random.choice(BURST_PALETTES)
        n_particles = random.randint(90, 140)

        # Klassischer Rundausbruch
        for i in range(n_particles):
            angle = 2 * math.pi * i / n_particles + random.uniform(-0.1, 0.1)
            spd   = random.uniform(2.0, 7.5)
            color = random.choice(palette)
            particles.append(Particle(
                self.x, self.y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                color, size=random.randint(2,4),
                life=random.uniform(0.7, 1.2),
                gravity=random.uniform(0.04, 0.09)
            ))

        # Goldener Kern-Ring
        for i in range(30):
            angle = 2 * math.pi * i / 30
            spd   = random.uniform(1.0, 3.0)
            particles.append(Particle(
                self.x, self.y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                "#ffffff", size=2,
                life=random.uniform(0.3, 0.6),
                gravity=0.03
            ))

        # Glitzer-Sterne
        for _ in range(20):
            angle = random.uniform(0, 2*math.pi)
            spd   = random.uniform(0.2, 1.5)
            particles.append(Particle(
                self.x + random.uniform(-5,5),
                self.y + random.uniform(-5,5),
                math.cos(angle)*spd, math.sin(angle)*spd,
                "#ffffaa", size=3,
                life=random.uniform(0.4, 0.8),
                gravity=0.05
            ))

# ─────────────────────────────────────────────
#  TEXT-Enthüllung
# ─────────────────────────────────────────────
class TextReveal:
    def __init__(self, canvas):
        self.canvas  = canvas
        self.text    = "PYTHON"
        self.letters = []
        self.phase   = 0      # 0=warten, 1=enthüllen, 2=fertig
        self.timer   = 0
        self.ids     = []

    def start(self):
        self.phase = 1
        self.timer = 0

    def update(self):
        if self.phase == 0:
            return
        self.timer += 1

        # Alle IDs löschen
        for id_ in self.ids:
            try: self.canvas.delete(id_)
            except: pass
        self.ids.clear()

        cx = WIDTH // 2
        cy = HEIGHT // 2 + 40

        for i, ch in enumerate(self.text):
            reveal = (self.timer - i * 12) / 30.0
            if reveal <= 0:
                continue
            t = min(1.0, reveal)

            # Farb-Verlauf Snake→Gold→Weiß
            if t < 0.5:
                col = lerp_color("#00ff88", "#ffdd00", t*2)
            else:
                col = lerp_color("#ffdd00", "#ffffff", (t-0.5)*2)

            scale   = 0.3 + 0.7 * min(1.0, t * 1.5)
            font_sz = int(90 * scale)
            alpha_f = min(1.0, t * 2)

            x_off = (i - len(self.text)/2 + 0.5) * 95 + cx
            y_off = cy + (1-t) * 60

            # Glow-Schatten
            for dx, dy in [(-2,2),(2,2),(-2,-2),(2,-2),(0,3),(0,-3),(3,0),(-3,0)]:
                gid = self.canvas.create_text(
                    x_off+dx, y_off+dy,
                    text=ch,
                    font=("Courier", max(10,font_sz), "bold"),
                    fill=dim_color(col, 0.4 * alpha_f)
                )
                self.ids.append(gid)

            tid = self.canvas.create_text(
                x_off, y_off,
                text=ch,
                font=("Courier", max(10,font_sz), "bold"),
                fill=col
            )
            self.ids.append(tid)

        if self.timer > len(self.text)*12 + 60:
            self.phase = 2

# ─────────────────────────────────────────────
#  Haupt-App
# ─────────────────────────────────────────────
class FireworksApp:
    def __init__(self, root):
        self.root      = root
        self.root.title("🎆 Python Feuerwerk 🎆")
        self.root.resizable(False, False)

        self.canvas    = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                   bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        # Sterne-Hintergrund
        self.draw_stars()

        self.particles = []
        self.rockets   = []
        self.text_rev  = TextReveal(self.canvas)

        self.frame     = 0
        self.text_triggered = False

        # Fade-Overlay (Nachzieh-Effekt)
        self.fade_rect = self.canvas.create_rectangle(
            0, 0, WIDTH, HEIGHT, fill=BG_COLOR,
            stipple="gray25", outline=""
        )

        self.animate()

    def draw_stars(self):
        for _ in range(180):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            r = random.choice([0.5, 1, 1, 1.5])
            br = random.choice(["#ffffff","#aaaaff","#ffeecc","#ccddff"])
            self.canvas.create_oval(x-r,y-r,x+r,y+r, fill=br, outline="")

    def launch_rocket(self):
        # Ziele: über dem Textzentrum verteilen
        cx = WIDTH // 2
        cy = HEIGHT // 2 - 60
        tx = cx + random.uniform(-250, 250)
        ty = cy + random.uniform(-80, 80)
        self.rockets.append(Rocket(self.canvas, tx, ty))

    def animate(self):
        self.frame += 1

        # ── Neue Raketen abschießen ──────────────────
        if not self.text_triggered:
            if self.frame % 38 == 0:
                self.launch_rocket()
            if self.frame % 60 == 0 and random.random() < 0.4:
                self.launch_rocket()
        else:
            # Nach Text-Enthüllung: Gelegenheits-Raketen
            if self.frame % 70 == 0 and random.random() < 0.6:
                self.launch_rocket()

        # ── Text-Trigger nach 5 Explosionen ─────────
        if not self.text_triggered and self.frame > 200:
            self.text_triggered = True
            self.text_rev.start()

        # ── Canvas leeren (nur Partikel-Bereich) ────
        self.canvas.delete("particle")
        self.canvas.delete("rocket")

        # ── Raketen ─────────────────────────────────
        next_r = []
        for r in self.rockets:
            alive = r.update(self.particles)
            if alive:
                # Schweif zeichnen
                for j in range(len(r.trail)-1):
                    t = j / max(1, len(r.trail))
                    col = dim_color(r.color, t * 0.8)
                    x1,y1 = r.trail[j]
                    x2,y2 = r.trail[j+1]
                    self.canvas.create_line(x1,y1,x2,y2,
                                            fill=col, width=2,
                                            tags="rocket")
                # Raketenspitze
                self.canvas.create_oval(
                    r.x-3, r.y-3, r.x+3, r.y+3,
                    fill="#ffffff", outline="",
                    tags="rocket"
                )
                next_r.append(r)
        self.rockets = next_r

        # ── Partikel ────────────────────────────────
        next_p = []
        for p in self.particles:
            alive = p.update()
            if alive:
                col  = dim_color(p.color, p.alpha)
                size = max(1, p.size * p.alpha)
                # Kleiner Schweif
                if len(p.trail) >= 2:
                    x0,y0 = p.trail[-2]
                    tc = dim_color(p.color, p.alpha * 0.4)
                    self.canvas.create_line(
                        x0,y0, p.x, p.y,
                        fill=tc, width=max(1,int(size)),
                        tags="particle"
                    )
                self.canvas.create_oval(
                    p.x-size, p.y-size,
                    p.x+size, p.y+size,
                    fill=col, outline="",
                    tags="particle"
                )
                next_p.append(p)
        self.particles = next_p

        # ── Text ────────────────────────────────────
        self.text_rev.update()

        # ── Fade-Overlay immer oben ──────────────────
        self.canvas.tag_raise(self.fade_rect)
        # Text soll über allem liegen
        for tid in self.text_rev.ids:
            try: self.canvas.tag_raise(tid)
            except: pass

        # ── Nächster Frame ───────────────────────────
        self.root.after(16, self.animate)   # ~60 FPS


# ─────────────────────────────────────────────
#  Start
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = FireworksApp(root)
    root.mainloop()