import math


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
