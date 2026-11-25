import datetime
import html
import os
import tempfile
import webbrowser

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
.footer{margin-top:30px;padding-top:10px;border-top:1px solid #999;
        font-size:13px;color:#2a3a9c}
.btn{display:block;margin:0 auto 16px;padding:8px 22px;font-size:15px;cursor:pointer}
@media print{.btn{display:none}}
"""


def create_letter(values):
    esc = html.escape
    parts = []
    parts.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    parts.append("<title>Post Office Investment Plan Summary</title>")
    parts.append("<style>" + CSS + "</style></head><body>")
    parts.append("<button class='btn' onclick='window.print()'>Print / Save as PDF</button>")
    parts.append("<h1>POST OFFICE INVESTMENT PLAN SUMMARY</h1>")
    parts.append("<p><b>Date:</b> " + datetime.date.today().strftime("%d-%m-%Y") + "</p>")
    parts.append("<p>Dear Investor,</p>")
    parts.append("<p>Thank you for evaluating your savings options using our Post Office "
                 "Investment Calculator. Below is the summary of your projected "
                 "investment returns based on your inputs:</p>")

    for title, items in SECTIONS:
        parts.append("<h2>" + esc(title) + "</h2><table>")
        for label, key in items:
            val = values.get(key) or "-"
            parts.append("<tr><td>" + esc(label) + "</td><td class='v'>"
                         + esc(str(val)) + "</td></tr>")
        parts.append("</table>")

    parts.append("<p>For any further queries, please feel free to reach out.</p>")
    parts.append("<div class='footer'>Designed By: Umesha H N LSGPA, Hassan Division, "
                 "Karnataka 573201<br>Contact: 9449759640 | Email: skpumesha@gmail.com</div>")
    parts.append("</body></html>")

    path = os.path.join(tempfile.gettempdir(), "PostOfficeReport.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    webbrowser.open("file:///" + path.replace("\\", "/"))
    return path
