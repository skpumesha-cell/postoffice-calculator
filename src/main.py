# Post Office Investment Calculator - single file version
import datetime
import html
import json
import math
import os
import sys
import tempfile
import tkinter as tk
import webbrowser
from tkinter import messagebox

# =====================================================================
#  RATES  (percent values; edit inside the app or verify with India Post)
# =====================================================================
DEFAULTS = {
    "RD": 6.7,
    "PPF": 7.1,
    "SSA": 8.2,
    "1 Year TD": 6.9,
    "2 Year TD": 6.9,
    "3 Year TD": 7.0,
    "5 Year TD": 7.5,
    "NSC": 7.7,
    "KVP": 7.5,
    "MIS": 7.4,
    "SCSS": 8.2,
}


def rates_path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    folder = os.path.join(base, "PostOfficeCalc")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = tempfile.gettempdir()
    return os.path.join(folder, "rates.json")


class Rates:
    def __init__(self):
        self.data = dict(DEFAULTS)
        try:
            with open(rates_path(), "r", encoding="utf-8") as f:
                self.data.update(json.load(f))
        except Exception:
            pass

    def get(self, name):
        """Return the rate as a decimal (7.5 -> 0.075)."""
        return float(self.data.get(name, DEFAULTS.get(name, 0))) / 100.0

    def save(self):
        with open(rates_path(), "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


# =====================================================================
#  CALCULATIONS
# =====================================================================
def rd_maturity(p, rate, months):
    """RD with quarterly compounding on each instalment."""
    total = 0.0
    for m in range(1, months + 1):
        q = (months - m + 1) / 3.0
        total += p * (1 + rate / 4.0) ** q
    return total


def yearly_scheme(p, rate, deposit_years, total_years):
    """PPF / SSA style: monthly deposits, yearly interest credit."""
    bal = 0.0
    for yr in range(1, total_years + 1):
        opening = bal
        running = opening
        interest = 0.0
        depositing = yr <= deposit_years
        for _ in range(12):
            if depositing:
                running += p
            interest += running * rate / 12.0
        interest = round(interest)
        bal = opening + (p * 12 if depositing else 0) + interest
    return bal


def monthly_contributions(p, rates):
    rd = rates.get("RD")
    ppf = rates.get("PPF")
    ssa = rates.get("SSA")

    ok_rd = p >= 100 and p % 10 == 0
    ok_ssa = p >= 250 and p % 50 == 0
    ok_ppf = p >= 500 and p % 50 == 0

    out = {"rd5": 0, "rd10w": 0, "rd10wo": 0, "ppf": 0, "ssa": 0}
    if ok_rd:
        out["rd5"] = round(rd_maturity(p, rd, 60))
        out["rd10w"] = round(rd_maturity(p, rd, 120))
        out["rd10wo"] = round(rd_maturity(p, rd, 60) * (1 + rd / 4.0) ** 20)
    if ok_ppf:
        out["ppf"] = round(yearly_scheme(p, ppf, 15, 15))
    if ok_ssa:
        out["ssa"] = round(yearly_scheme(p, ssa, 15, 21))

    bad = []
    if not ok_rd:
        bad.append("RD (min 100, multiple of 10)")
    if not ok_ppf:
        bad.append("PPF (min 500, multiple of 50)")
    if not ok_ssa:
        bad.append("SSA (min 250, multiple of 50)")
    out["message"] = ("Invalid denomination for: " + "; ".join(bad)) if bad \
        else "Denomination is valid for all schemes"
    return out


def fd_comparison(p, rates):
    def td(name, years):
        r = rates.get(name)
        annual = round(p * ((1 + r / 4.0) ** 4 - 1))
        return round(p + annual * years)

    rkvp = rates.get("KVP")
    months = round(12 * math.log(2) / math.log(1 + rkvp)) if rkvp > 0 else 0
    return {
        "td1": td("1 Year TD", 1),
        "td2": td("2 Year TD", 2),
        "td3": td("3 Year TD", 3),
        "td5": td("5 Year TD", 5),
        "nsc": round(p * (1 + rates.get("NSC")) ** 5),
        "kvp": round(p * 2),
        "kvp_months": months,
    }


def returns(p, joint, rates):
    mis_rate = rates.get("MIS")
    scss_rate = rates.get("SCSS")
    rd = rates.get("RD")

    mis_limit = 1500000 if joint else 900000
    mis_ok = p >= 1000 and p % 1000 == 0 and p <= mis_limit
    scss_ok = p >= 1000 and p % 1000 == 0 and p <= 3000000

    mis_m = round(p * mis_rate / 12.0) if mis_ok else 0
    scss_q = round(p * scss_rate / 12.0 * 3) if scss_ok else 0
    scss_m = round(p * scss_rate / 12.0) if scss_ok else 0

    def route(monthly):
        if monthly < 100:
            return 0, 0
        denom = int(monthly // 10 * 10)
        return denom, round(rd_maturity(denom, rd, 60)) + round(p)

    mis_den, mis_rd = route(mis_m)
    scss_den, scss_rd = route(scss_m)

    return {
        "mis": mis_m,
        "mis_msg": "Maximum limit is 9L single / 15L joint" if mis_ok else "Invalid Investment",
        "scss": scss_q,
        "scss_msg": "Maximum limit is 30 Lakhs" if scss_ok else "Invalid Investment",
        "avg_mis": mis_m,
        "avg_scss": scss_m,
        "mis_rd": mis_rd,
        "mis_rd_den": mis_den,
        "scss_rd": scss_rd,
        "scss_rd_den": scss_den,
    }


# =====================================================================
#  HTML REPORT (opens in the browser, nothing saved in Documents)
# =====================================================================
SECTIONS = [
    ("1. Monthly Contributions & Long-Term Schemes", [
        ("Monthly Investment Amount", "monthly"),
        ("RD 5 Year Maturity", "rd5"),
        ("RD 10 Year With Deposit", "rd10w"),
        ("RD 10 Year Without Deposit", "rd10wo"),
        ("PPF (15 Years)", "ppf"),
        ("SSA (21 Years)", "ssa"),
    ]),
    ("2. Fixed Deposit & Certificate Comparison", [
        ("FD Amount", "fd"),
        ("1 Year TD", "td1"),
        ("2 Year TD", "td2"),
        ("3 Year TD", "td3"),
        ("5 Year TD", "td5"),
        ("5 Year NSC", "nsc"),
        ("KVP Maturity", "kvp"),
        ("KVP doubles in (months)", "kvp_months"),
    ]),
    ("3. Regular Income Schemes (MIS & SCSS)", [
        ("Investment Amount", "ret_amt"),
        ("Monthly Returns (MIS)", "mis"),
        ("Quarterly Returns (SCSS)", "scss"),
        ("Average Monthly MIS", "avg_mis"),
        ("Average Monthly SCSS", "avg_scss"),
    ]),
    ("4. Interest Routed for RD Investment", [
        ("MIS to RD Maturity", "mis_rd"),
        ("MIS to RD Denomination", "mis_rd_den"),
        ("SCSS to RD Maturity", "scss_rd"),
        ("SCSS to RD Denomination", "scss_rd_den"),
    ]),
]

CSS = """
body{font-family:Segoe UI,Arial,sans-serif;max-width:800px;margin:20px auto;
     padding:0 16px;color:#222}
h1{text-align:center;border-bottom:3px solid #cc0000;padding-bottom:8px;
   color:#cc0000;font-size:24px}
h2{color:#2a3a9c;font-size:17px;margin-top:26px;border-bottom:1px solid #ccc;
   padding-bottom:4px}
table{width:100%;border-collapse:collapse}
td{padding:6px 10px;border-bottom:1px solid #e3e3e3}
td.v{text-align:right;font-weight:bold;white-space:nowrap}
.logo{text-align:center;margin-bottom:6px}
.logo img{height:110px}
.footer{margin-top:30px;padding-top:10px;border-top:1px solid #999;
        font-size:13px;color:#2a3a9c}
.btn{display:block;margin:0 auto 16px;padding:8px 22px;font-size:15px;cursor:pointer}
@media print{.btn{display:none}}
"""


def create_report(values, logo_uri=""):
    esc = html.escape
    p = []
    p.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    p.append("<title>Post Office Investment Plan Summary</title>")
    p.append("<style>" + CSS + "</style></head><body>")
    p.append("<button class='btn' onclick='window.print()'>Print / Save as PDF</button>")
    if logo_uri:
        p.append("<div class='logo'><img src='" + logo_uri + "'></div>")
    p.append("<h1>POST OFFICE INVESTMENT PLAN SUMMARY</h1>")
    p.append("<p><b>Date:</b> " + datetime.date.today().strftime("%d-%m-%Y") + "</p>")
    p.append("<p>Dear Investor,</p>")
    p.append("<p>Thank you for evaluating your savings options using our Post Office "
             "Investment Calculator. Below is the summary of your projected "
             "investment returns based on your inputs:</p>")
    for title, items in SECTIONS:
        p.append("<h2>" + esc(title) + "</h2><table>")
        for label, key in items:
            val = values.get(key) or "-"
            p.append("<tr><td>" + esc(label) + "</td><td class='v'>" + esc(str(val)) + "</td></tr>")
        p.append("</table>")
    p.append("<p>For any further queries, please feel free to reach out.</p>")
    p.append("<div class='footer'>Post office Investment is very safest and "
             "guaranteed by the Government of India</div>")
    p.append("</body></html>")

    path = os.path.join(tempfile.gettempdir(), "PostOfficeReport.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(p))
    webbrowser.open("file:///" + path.replace("\\", "/"))
    return path


# =====================================================================
#  USER INTERFACE
# =====================================================================
BG = "#d4d0c8"
RED = "#cc0000"
BLUE = "#2a3a9c"
BROWN = "#7a4a1a"
FONT = ("Segoe UI", 11)


def asset(name):
    """Find a bundled file (inside the built app, or when run from source)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(getattr(sys, "_MEIPASS", here), "assets", name),
              os.path.join(here, "..", "assets", name),
              os.path.join(here, "assets", name)):
        if os.path.exists(c):
            return c
    return None


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
        self.title("Kavasu - Post Office Investment Calculator")
        self.configure(bg=BG)
        self.geometry("1240x760")
        self.rates = Rates()
        self.v = {}
        self.joint = tk.BooleanVar(value=False)

        ico = asset("icon.ico")
        if ico:
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        # header: emblem + title
        head = tk.Frame(self, bg=BG)
        head.grid(row=0, column=0, columnspan=4, pady=8)
        mark = asset("logo_mark.png")
        if mark:
            try:
                self.mark_img = tk.PhotoImage(file=mark)
                tk.Label(head, image=self.mark_img, bg=BG).pack(side="left", padx=14)
            except Exception:
                pass
        tk.Label(head, text="Postoffice Investment Calculator",
                 font=("Courier New", 26, "underline"), bg=BG).pack(side="left")

        self.left = self.panel("Monthly Contributions", 0)
        self.mid = self.panel("FD Comparison", 1)
        self.right = self.panel("Monthly or Quarterly Returns", 2)
        self.build_left()
        self.build_mid()
        self.build_right()
        self.build_side()

        tk.Label(self, text="Designed By: Umesha H N LSGPA, Hassan Division, Karnataka 573201\n"
                            "Contact: 9449759640 | Email: skpumesha@gmail.com",
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
        # full Kavasu logo inside the form (white card)
        full = asset("logo_full.png")
        if full:
            try:
                self.full_img = tk.PhotoImage(file=full)
                tk.Label(f, image=self.full_img, bg="white", bd=1, relief="solid"
                         ).pack(pady=(24, 0))
            except Exception:
                pass

    # ---------- actions ----------
    def do_fetch(self):
        p = self.num("monthly")
        if p is None or p <= 0:
            messagebox.showwarning("Missing Information",
                                   "Please enter a valid Monthly Contribution amount.")
            return
        r = monthly_contributions(p, self.rates)
        self.set_all({k: r[k] for k in ("rd5", "rd10w", "rd10wo", "ppf", "ssa")})
        self.var("why").set(r["message"])

    def do_compare(self):
        p = self.num("fd")
        if p is None or p <= 0:
            messagebox.showwarning("Missing Amount", "Please enter a valid FD Amount.")
            return
        r = fd_comparison(p, self.rates)
        self.set_all(r)
        self.var("kvp_months").set(str(r["kvp_months"]))

    def do_returns(self):
        p = self.num("ret_amt")
        if p is None or p <= 0:
            messagebox.showwarning("Invalid Input", "Please enter a valid amount.")
            return
        r = returns(p, self.joint.get(), self.rates)
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
                tk.Label(win, text=str(self.rates.data[name]) + "%", bg=BG, font=FONT
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
        uri = ""
        try:
            import base64
            lg = asset("logo_full.png")
            if lg:
                with open(lg, "rb") as f:
                    uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
        except Exception:
            uri = ""
        try:
            create_report(values, uri)
        except Exception as ex:
            messagebox.showerror("Error", "Could not open report:\n" + str(ex))


if __name__ == "__main__":
    App().mainloop()
