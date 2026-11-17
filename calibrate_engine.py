import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas

# Available width = 612 - 72 = 540 pt
# Available height = 792 - 68 = 724 pt
# Header line at h - 28, Footer line at 29
# Usable vertical content height: approx 655 pt. Target: 630 - 655 pt (96-99% coverage).

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=16,
    leading=19.5,
    textColor=colors.HexColor('#0f172a'),
    spaceAfter=4,
    alignment=0
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=13.5,
    textColor=colors.HexColor('#0369a1'),
    spaceAfter=6,
    alignment=0
)

h1_style = ParagraphStyle(
    'SecH1',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=13.5,
    leading=17,
    textColor=colors.HexColor('#0f172a'),
    spaceBefore=5,
    spaceAfter=3,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'SecH2',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=14.5,
    textColor=colors.HexColor('#0369a1'),
    spaceBefore=4,
    spaceAfter=2,
    keepWithNext=True
)

# Maximized body font: 10.5 pt with 14.2 pt leading!
body_style = ParagraphStyle(
    'SecBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10.5,
    leading=14.2,
    textColor=colors.HexColor('#1e293b'),
    spaceAfter=4
)

body_bold = ParagraphStyle(
    'SecBodyBold',
    parent=body_style,
    fontName='Helvetica-Bold'
)

tbl_body = ParagraphStyle(
    'TblBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=12.5,
    textColor=colors.HexColor('#1e293b')
)

tbl_bold = ParagraphStyle(
    'TblBold',
    parent=tbl_body,
    fontName='Helvetica-Bold'
)

def measure_flowables(flowables, width=540):
    total_h = 0
    for f in flowables:
        w, h = f.wrap(width, 1000)
        total_h += h
    return total_h

print("Styles initialized successfully for height measurement.")

