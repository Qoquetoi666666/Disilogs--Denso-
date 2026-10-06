from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT_DIR = Path("data/samples/documents")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "CNC-003_demo_maintenance.pdf"

def draw_lines(c, lines, x=60, start_y=780, step=24):
    y = start_y
    for line in lines:
        c.drawString(x, y, line)
        y -= step

c = canvas.Canvas(str(OUTPUT), pagesize=A4)

c.setTitle("CNC-003 Demo Maintenance Guide")

# PAGE 1
c.setFont("Helvetica-Bold", 18)
c.drawString(
    60,
    800,
    "DIGI-LOGS DEMO MAINTENANCE GUIDE",
)

c.setFont("Helvetica", 12)

draw_lines(
    c,
    [
        "DEMO / SYNTHETIC DOCUMENT - NOT AN OFFICIAL OKUMA MANUAL",
        "",
        "Machine ID: CNC-003",
        "Asset Code: ASSET-CNC-003",
        "Manufacturer: OKUMA",
        "Series: GENOS",
        "Model: M560-V",
        "",
        "Purpose:",
        "This document is synthetic demo data for Digi-Logs.",
        "It is used to test PDF ingestion, retrieval and citation.",
    ],
    start_y=755,
)

c.showPage()

# PAGE 2
c.setFont("Helvetica-Bold", 16)
c.drawString(
    60,
    800,
    "Demo Maintenance Case - Spindle Vibration",
)

c.setFont("Helvetica", 12)

draw_lines(
    c,
    [
        "Symptom:",
        "Abnormal vibration occurs when the spindle runs at high speed.",
        "",
        "Possible cause:",
        "Spindle belt tension may be below the expected operating range.",
        "",
        "Recommended inspection:",
        "1. Stop the machine safely.",
        "2. Inspect spindle belt condition.",
        "3. Verify belt tension.",
        "4. Adjust belt tension if required.",
        "5. Run a controlled verification test.",
        "",
        "Expected result:",
        "Spindle vibration returns to the normal baseline after adjustment.",
        "",
        "Safety note:",
        "This is synthetic demonstration content for Digi-Logs testing.",
    ],
    start_y=755,
)

c.save()

print(f"Created: {OUTPUT}")
