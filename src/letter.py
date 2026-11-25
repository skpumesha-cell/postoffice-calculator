import datetime
import os
import tempfile

def create_letter(values):
    from docx import Document
    doc = Document()
SECTIONS = [
    ("1. MONTHLY CONTRIBUTIONS & LONG-TERM SCHEMES", [
        ("Monthly Investment Amount", "monthly"),
        ("RD 5 Year Maturity", "rd5"),
        ("RD 10 Year With Deposit", "rd10w"),
        ("RD 10 Year Without Deposit", "rd10wo"),
        ("PPF (15 Years)", "ppf"),
        ("SSA (21 Years)", "ssa"),
    ]),
    ("2. FIXED DEPOSIT & CERTIFICATE COMPARISON", [
        ("FD Amount", "fd"),
        ("1 Year TD", "td1"),
        ("2 Year TD", "td2"),
        ("3 Year TD", "td3"),
        ("5 Year TD", "td5"),
        ("5 Year NSC", "nsc"),
        ("KVP Maturity", "kvp"),
        ("KVP doubles in (months)", "kvp_months"),
    ]),
    ("3. REGULAR INCOME SCHEMES (MIS & SCSS)", [
        ("Investment Amount", "ret_amt"),
        ("Monthly Returns (MIS)", "mis"),
        ("Quarterly Returns (SCSS)", "scss"),
        ("Average Monthly MIS", "avg_mis"),
        ("Average Monthly SCSS", "avg_scss"),
    ]),
    ("4. INTEREST ROUTED FOR RD INVESTMENT", [
        ("MIS to RD Maturity", "mis_rd"),
        ("MIS to RD Denomination", "mis_rd_den"),
        ("SCSS to RD Maturity", "scss_rd"),
        ("SCSS to RD Denomination", "scss_rd_den"),
    ]),
]


def create_letter(values):
    doc = Document()
    doc.add_heading("POST OFFICE INVESTMENT PLAN SUMMARY", level=1)
    doc.add_paragraph("Date: " + datetime.date.today().strftime("%d-%m-%Y"))
    doc.add_paragraph("Dear Investor,")
    doc.add_paragraph(
        "Thank you for evaluating your savings options using our Post Office "
        "Investment Calculator. Below is the summary of your projected "
        "investment returns based on your inputs:"
    )
    for title, items in SECTIONS:
        doc.add_heading(title, level=2)
        for label, key in items:
            doc.add_paragraph(f"{label}: {values.get(key) or '-'}", style="List Bullet")
    doc.add_paragraph("For any further queries, please feel free to reach out.")
    doc.add_paragraph(
        "Designed By: Umesha H N LSGPA, Hassan Division, Karnataka 573201\n"
        "Contact: 9449759640 | Email: skpumesha@gmail.com"
    )

    folder = os.path.join(os.path.expanduser("~"), "Documents")
    if not os.path.isdir(folder):
        folder = tempfile.gettempdir()
    name = "Investment_Letter_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".docx"
    path = os.path.join(folder, name)
    doc.save(path)
    try:
        os.startfile(path)
    except Exception:
        pass
    return path
