import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak

# Import build_pdf or extract the pages
import build_clean_professional_report as b

styles = getSampleStyleSheet()

# Test wrap heights of pages
print("Printable height:", 792 - 68, "pt = 724 pt")
print("Target usable height: ~640-660 pt")
