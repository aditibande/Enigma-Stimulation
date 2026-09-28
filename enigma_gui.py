import tkinter as tk
from tkinter import ttk
from enigma import Enigma, ROTORS, REFLECTORS, A

ROWS = ["QWERTZUIOP", "ASDFGHJKL", "PYXCVBNM"]
BG = "#141414"
BRASS = "#b5924a"
CX = 430


def row_x(i, n):
    return CX + (i - (n - 1) / 2) * 72


def group(s):
    return " ".join(s[i:i + 5] for i in range(0, len(s), 5))[-72:]


class App:
    def __init__(self, root):
        self.root = root
        root.title("Enigma Machine")
        root.configure(bg=BG)
        root.resizable(False, False)
        self.start = [0, 0, 0]
        self.inp = ""
        self.out = ""
        self.current = None
        self.lit = None
        self.canvas = tk.Canvas(root, width=860, height=640, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.build_body()
        self.build_rotors()
        self.build_lamps()
        self.build_keys()
        self.build_controls()
        self.apply()
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

    def build_body(self):
        c = self.canvas
        c.create_rectangle(8, 8, 852, 632, fill="#1c1c1c", outline=BRASS, width=3)
        c.create_text(CX, 26, text="E N I G M A", fill=BRASS, font=("Georgia", 18, "bold"))
        c.create_rectangle(90, 175, 770, 385, fill="#0c0c0c", outline="#4a4a4a", width=2)
        c.create_rectangle(90, 420, 770, 618, fill="#101010", outline="#4a4a4a", width=2)

    def build_rotors(self):
        c = self.canvas
        self.win_text = []
        for i, cx in enumerate((CX - 100, CX, CX + 100)):
            c.create_rectangle(cx - 36, 62, cx + 36, 132, fill="#080808", outline=BRASS, width=3)
            self.win_text.append(
                c.create_text(cx, 97, text="A", fill="#f2e9d0", font=("Courier", 38, "bold"))
            )
            arrows = (
                (1, (cx - 16, 56, cx + 16, 56, cx, 40)),
                (-1, (cx - 16, 138, cx + 16, 138, cx, 154)),
            )
            for d, pts in arrows:
                item = c.create_polygon(*pts, fill=BRASS, outline="")
                c.tag_bind(item, "<Button-1>", lambda e, i=i, d=d: self.shift(i, d))

    def build_lamps(self):
        c = self.canvas
        self.lamps = {}
        for r, row in enumerate(ROWS):
            y = 215 + r * 62
            for i, ch in enumerate(row):
                x = row_x(i, len(row))
                halos = [
                    c.create_oval(x - rad, y - rad, x + rad, y + rad, fill=col, outline="", state="hidden")
                    for rad, col in ((42, "#2e2814"), (35, "#544817"), (29, "#8a7423"))
                ]
                bulb = c.create_oval(x - 24, y - 24, x + 24, y + 24, fill="#262626", outline="#5a5a5a", width=2)
                txt = c.create_text(x, y, text=ch, fill="#6a6a6a", font=("Helvetica", 17, "bold"))
                self.lamps[ch] = (halos, bulb, txt)

    def build_keys(self):
        c = self.canvas
        self.keys = {}
        for r, row in enumerate(ROWS):
            y = 462 + r * 60
            for i, ch in enumerate(row):
                x = row_x(i, len(row))
                tag = "k" + ch
                circ = c.create_oval(x - 26, y - 26, x + 26, y + 26, fill="#2a2a2a",
                                     outline="#8c8c8c", width=3, tags=(tag,))
                c.create_text(x, y, text=ch, fill="#e8e8e8", font=("Helvetica", 16, "bold"), tags=(tag,))
                c.tag_bind(tag, "<ButtonPress-1>", lambda e, ch=ch: self.press(ch))
                c.tag_bind(tag, "<ButtonRelease-1>", lambda e: self.release())
                self.keys[ch] = circ

    def build_controls(self):
        f = tk.Frame(self.root, bg=BG)
        f.pack(fill="x", padx=14, pady=(6, 10))
        lab = dict(bg=BG, fg=BRASS, font=("Helvetica", 10, "bold"))
        self.rotor_vars = [tk.StringVar(value=v) for v in ("I", "II", "III")]
        self.ring_vars = [tk.StringVar(value="1") for _ in range(3)]
        self.refl_var = tk.StringVar(value="B")
        self.plug_var = tk.StringVar()

        tk.Label(f, text="Rotors L/M/R", **lab).grid(row=0, column=0, sticky="w")
        for i, v in enumerate(self.rotor_vars):
            ttk.Combobox(f, textvariable=v, values=list(ROTORS), width=4,
                         state="readonly").grid(row=0, column=1 + i, padx=2)
        tk.Label(f, text="Reflector", **lab).grid(row=0, column=4, padx=(14, 4))
        ttk.Combobox(f, textvariable=self.refl_var, values=list(REFLECTORS), width=3,
                     state="readonly").grid(row=0, column=5)
        ttk.Button(f, text="Apply & Reset", command=self.apply).grid(row=0, column=6, padx=(14, 2))
        ttk.Button(f, text="Copy output", command=self.copy).grid(row=0, column=7)

        tk.Label(f, text="Rings", **lab).grid(row=1, column=0, sticky="w", pady=4)
        for i, v in enumerate(self.ring_vars):
            ttk.Spinbox(f, textvariable=v, from_=1, to=26, width=4).grid(row=1, column=1 + i, padx=2)
        tk.Label(f, text="Plugboard", **lab).grid(row=1, column=4, padx=(14, 4))
        ttk.Entry(f, textvariable=self.plug_var, width=28).grid(row=1, column=5, columnspan=3, sticky="w")

        mono = dict(bg=BG, fg="#cfcfcf", font=("Courier", 12), anchor="w", width=84)
        self.in_label = tk.Label(f, **mono)
        self.in_label.grid(row=2, column=0, columnspan=8, sticky="w")
        self.out_label = tk.Label(f, **dict(mono, fg="#ffd75e"))
        self.out_label.grid(row=3, column=0, columnspan=8, sticky="w")
        self.status = tk.Label(f, bg=BG, fg="#e07070", font=("Helvetica", 10), anchor="w")
        self.status.grid(row=4, column=0, columnspan=8, sticky="w")

    def apply(self):
        names = [v.get() for v in self.rotor_vars]
        if len(set(names)) < 3:
            return self.status.config(text="Each rotor must be different.")
        try:
            rings = tuple(int(v.get()) for v in self.ring_vars)
            assert all(1 <= r <= 26 for r in rings)
        except (ValueError, AssertionError):
            return self.status.config(text="Ring settings must be between 1 and 26.")
        pairs = self.plug_var.get().upper().split()
        used = "".join(pairs)
        if (len(pairs) > 10 or any(len(p) != 2 for p in pairs)
                or not all(ch in A for ch in used) or len(set(used)) != len(used)):
            return self.status.config(text="Plugboard: up to 10 pairs of distinct letters, e.g. AB CD EF.")
        self.status.config(text="")
        self.machine = Enigma(
            rotors=tuple(names),
            reflector=self.refl_var.get(),
            rings=rings,
            positions="".join(A[i] for i in self.start),
            plugboard=" ".join(pairs),
        )
        self.inp = ""
        self.out = ""
        self.refresh()
        self.root.focus_set()

    def shift(self, i, d):
        self.start[i] = (self.start[i] + d) % 26
        self.apply()

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.out)

    def refresh(self):
        rotors = (self.machine.left, self.machine.mid, self.machine.right)
        for t, rotor in zip(self.win_text, rotors):
            self.canvas.itemconfig(t, text=A[rotor.pos])
        self.in_label.config(text="IN   " + group(self.inp))
        self.out_label.config(text="OUT  " + group(self.out))

    def light(self, ch, on):
        halos, bulb, txt = self.lamps[ch]
        for h in halos:
            self.canvas.itemconfig(h, state="normal" if on else "hidden")
        self.canvas.itemconfig(bulb, fill="#fff2a8" if on else "#262626",
                               outline="#ffd75e" if on else "#5a5a5a")
        self.canvas.itemconfig(txt, fill="#2a2100" if on else "#6a6a6a")

    def key_style(self, ch, down):
        self.canvas.itemconfig(self.keys[ch], fill="#6b6b6b" if down else "#2a2a2a",
                               outline=BRASS if down else "#8c8c8c")

    def press(self, ch):
        if self.current:
            return
        self.current = ch
        out = self.machine.encrypt_char(ch)
        self.inp += ch
        self.out += out
        self.lit = out
        self.key_style(ch, True)
        self.light(out, True)
        self.refresh()

    def release(self):
        if not self.current:
            return
        self.key_style(self.current, False)
        self.light(self.lit, False)
        self.current = None

    def on_key_press(self, e):
        if isinstance(e.widget, (tk.Entry, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            return
        ch = e.keysym.upper()
        if len(ch) == 1 and ch in A:
            self.press(ch)

    def on_key_release(self, e):
        if e.keysym.upper() == self.current:
            self.release()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
