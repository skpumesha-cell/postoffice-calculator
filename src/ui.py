import tkinter as tk
from tkinter import messagebox

import calculators as calc
import letter
from rates import Rates

BG = "#d4d0c8"
RED = "#cc0000"
BLUE = "#2a3a9c"
BROWN = "#7a4a1a"
FONT = ("Segoe UI", 11)


def inr(n):
    """Indian digit grouping: 1234567 -> 12,34,567"""
    n = int(round(n))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + s


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Post Office Investment Calculator")
        self.configure(bg=BG)
        self.geometry("1200x740")
        self.rates = Rates()
        self.v = {}
        self.joint = tk.BooleanVar(value=False)

        tk.Label(self, text="Postoffice Investment Calculator",
                 font=("Courier New", 26, "underline"), bg=BG
                 ).grid(row=0, column=0, columnspan=4, pady=10)

        self.left = self.panel("Monthly Contributions", 0)
        self.mid = self.panel("FD Comparison", 1)
        self.right = self.panel("Monthly or Quarterly Returns", 2)
        self.build_left()
        self.build_mid()
        self.build_right()
        self.build_side()

        tk.Label(self, text="Designed By : Umesha H N LSGPA, Hassan Division, Karnataka 573201\n"
                            "Contact: 9449759640  eMail : skpumesha@gmail.com",
                 font=("Segoe UI", 10, "bold"), fg=BLUE, bg=BG, justify="left"
                 ).grid(row=2, column=0, columnspan=3, sticky="w", padx=12, pady=8)

    # ---------- helpers ----------
    def panel(self, title, col):
        f = tk.LabelFrame(self, text=title, font=("Segoe UI", 16), fg=RED,
                          bg=BG, padx=10, pady=8)
        f.grid(row=1, column=col, sticky="n", padx=8, pady=4)
        return f

    def var(self, key):
        if key not in self.v:
            self.v[key] = tk.StringVar()
        return self.v[key]

    def row(self, parent, r, label, key, readonly=True, width=18):
        tk.Label(parent, text=label, bg=BG, font=FONT, anchor="w"
                 ).grid(row=r, column=0, sticky="w", pady=3)
        tk.Entry(parent, textvariable=self.var(key), width=width, font=FONT,
                 justify="right", state="readonly" if readonly else "normal",
                 readonlybackground="white"
                 ).grid(row=r, column=1, pady=3, padx=4)

    def button(self, parent, r, text, cmd):
        tk.Button(parent, text=text, command=cmd, width=14,
                  font=("Segoe UI", 11, "bold")
                  ).grid(row=r, column=0, columnspan=2, pady=6)

    def note(self, parent, r, key, color="black"):
        tk.Label(parent, textvariable=self.var(key), bg=BG, fg=color,
                 font=("Segoe UI", 9), wraplength=300, justify="left"
                 ).grid(row=r, column=0, columnspan=2, sticky="w")

    def header(self, parent, r, text, color):
        tk.Label(parent, text=text, bg=BG, fg=color, font=("Segoe UI", 11, "bold"),
                 wraplength=320, justify="left"
                 ).grid(row=r, column=0, columnspan=2, sticky="w", pady=(10, 2))

    def num(self, key):
        try:
            return float(self.var(key).get().replace(",", "").strip())
        except ValueError:
            return None

    def set_all(self, mapping):
        for k, val in mapping.items():
            self.var(k).set(inr(val))

    # ---------- panels ----------
    def build_left(self):
        p = self.left
        self.row(p, 0, "Monthly Invest:", "monthly", readonly=False)
        self.button(p, 1, "Fetch", self.do_fetch)
        self.row(p, 2, "RD 5 Year:", "rd5")
        self.row(p, 3, "RD 10 Year With Deposit:", "rd10w")
        self.row(p, 4, "RD 10 Year Without Depo:", "rd10wo")
        self.row(p, 5, "PPF in 15 Years:", "ppf")
        self.row(p, 6, "SSA in 21 Years:", "ssa")
        tk.Label(p, text="Why '0' Appears:", bg=BG, font=("Segoe UI", 9)
                 ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.note(p, 8, "why", "red")

    def build_mid(self):
        p = self.mid
        self.row(p, 0, "FD Amount:", "fd", readonly=False)
        self.button(p, 1, "Compare", self.do_compare)
        self.row(p, 2, "1 Year TD:", "td1")
        self.row(p, 3, "2 Year TD:", "td2")
        self.row(p, 4, "3 Year TD:", "td3")
        self.row(p, 5, "5 Year TD:", "td5")
        self.row(p, 6, "5 Year NSC:", "nsc")
        self.row(p, 7, "KVP:", "kvp")
        self.row(p, 8, "KVP Double In (Months):", "kvp_months", width=8)

    def build_right(self):
        p = self.right
        self.row(p, 0, "Amount:", "ret_amt", readonly=False)
        self.button(p, 1, "Returns", self.do_returns)
        tk.Checkbutton(p, text="Check it if Joint A/C", variable=self.joint,
                       bg=BG, font=FONT, activebackground=BG
                       ).grid(row=2, column=0, columnspan=2, sticky="w")
        self.row(p, 3, "Monthly Returns-MIS:", "mis")
        self.note(p, 4, "mis_msg")
        self.row(p, 5, "Quarterly Returns-SCSS:", "scss")
        self.note(p, 6, "scss_msg")
        self.header(p, 7, "Comparison MIS to SCSS Monthly Average Returns", BROWN)
        self.row(p, 8, "Average Monthly-MIS:", "avg_mis")
        self.row(p, 9, "Average Monthly-SCSS:", "avg_scss")
        self.header(p, 10, "If Interest of MIS/SCSS Routed for RD Investment", BLUE)
        self.row(p, 11, "MIS-RD:", "mis_rd")
        self.row(p, 12, "RD Denom:", "mis_rd_den")
        self.row(p, 13, "SCSS-RD:", "scss_rd")
        self.row(p, 14, "RD Denom:", "scss_rd_den")

    def build_side(self):
        f = tk.Frame(self, bg=BG)
        f.grid(row=1, column=3, sticky="n", padx=10, pady=10)
        for text, cmd in [("Current Rates of Interest", lambda: self.show_rates(False)),
                          ("Change the Rate of Interest", lambda: self.show_rates(True)),
                          ("Generate Letter", self.make_letter)]:
            tk.Button(f, text=text, command=cmd, width=24, height=2, font=FONT
                      ).pack(pady=8)

    # ---------- actions ----------
    def do_fetch(self):
        p = self.num("monthly")
        if p is None or p <= 0:
            messagebox.showwarning("Missing Information",
                                   "Please enter a valid Monthly Contribution amount.")
            return
        r = calc.monthly_contributions(p, self.rates)
        self.set_all({k: r[k] for k in ("rd5", "rd10w", "rd10wo", "ppf", "ssa")})
        self.var("why").set(r["message"])

    def do_compare(self):
        p = self.num("fd")
        if p is None or p <= 0:
            messagebox.showwarning("Missing Amount", "Please enter a valid FD Amount.")
            return
        r = calc.fd_comparison(p, self.rates)
        self.set_all(r)
        self.var("kvp_months").set(str(r["kvp_months"]))

    def do_returns(self):
        p = self.num("ret_amt")
        if p is None or p <= 0:
            messagebox.showwarning("Invalid Input", "Please enter a valid amount.")
            return
        r = calc.returns(p, self.joint.get(), self.rates)
        self.var("mis_msg").set(r.pop("mis_msg"))
        self.var("scss_msg").set(r.pop("scss_msg"))
        self.set_all(r)

    def show_rates(self, edit):
        win = tk.Toplevel(self)
        win.title("Change the Rate of Interest" if edit else "Current Rates of Interest")
        win.configure(bg=BG)
        win.grab_set()
        entries = {}
        for i, name in enumerate(sorted(self.rates.data)):
            tk.Label(win, text=name, bg=BG, font=FONT, anchor="w", width=14
                     ).grid(row=i, column=0, padx=10, pady=3)
            if edit:
                e = tk.Entry(win, width=8, font=FONT, justify="right")
                e.insert(0, str(self.rates.data[name]))
                e.grid(row=i, column=1, padx=4)
                tk.Label(win, text="%", bg=BG).grid(row=i, column=2)
                entries[name] = e
            else:
                tk.Label(win, text=f"{self.rates.data[name]}%", bg=BG, font=FONT
                         ).grid(row=i, column=1, padx=10)
        if edit:
            def save():
                try:
                    new = {n: float(e.get()) for n, e in entries.items()}
                except ValueError:
                    messagebox.showerror("Invalid", "Enter numbers only, e.g. 7.4", parent=win)
                    return
                self.rates.data.update(new)
                self.rates.save()
                messagebox.showinfo("Saved", "Interest rates updated.", parent=win)
                win.destroy()
            tk.Button(win, text="Save", command=save, width=12, font=FONT
                      ).grid(row=len(entries), column=0, columnspan=3, pady=10)

        def make_letter(self):
        values = {k: s.get() for k, s in self.v.items()}
        try:
            letter.create_letter(values)
        except Exception as ex:
            messagebox.showerror("Error", f"Could not open report:\n{ex}")
            return
        messagebox.showinfo("Success", f"Letter saved:\n{path}")
