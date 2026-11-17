import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak

# Let's import or extract the story from build_perfect_report.py
# We can run a modified script that collects pages as lists of flowables and measures their wrap height.

print("Measuring available height...")
print(f"Letter height = {792} pt, margins: top=34, bottom=34 -> printable = {724} pt")

