import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)

styles = getSampleStyleSheet()

# Calibrated Typographic Hierarchy
title_style = ParagraphStyle(
    'DocTitle', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=15.5, leading=19,
    textColor=colors.HexColor('#0f172a'), spaceAfter=3
)
subtitle_style = ParagraphStyle(
    'DocSubTitle', parent=styles['Normal'],
    fontName='Helvetica', fontSize=9.8, leading=13,
    textColor=colors.HexColor('#0369a1'), spaceAfter=5
)
h1_style = ParagraphStyle(
    'SecH1', parent=styles['Heading1'],
    fontName='Helvetica-Bold', fontSize=13.0, leading=16.5,
    textColor=colors.HexColor('#0f172a'), spaceBefore=5, spaceAfter=2.5,
    keepWithNext=True
)
h2_style = ParagraphStyle(
    'SecH2', parent=styles['Heading2'],
    fontName='Helvetica-Bold', fontSize=11.0, leading=14.5,
    textColor=colors.HexColor('#0369a1'), spaceBefore=4, spaceAfter=2,
    keepWithNext=True
)
# Maximized body text: 10.5 pt font with 14.2 pt leading
body_style = ParagraphStyle(
    'SecBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=10.5, leading=14.2,
    textColor=colors.HexColor('#1e293b'), spaceAfter=3.5
)
body_bold = ParagraphStyle(
    'SecBodyBold', parent=body_style,
    fontName='Helvetica-Bold'
)
tbl_body = ParagraphStyle(
    'TblBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=9.5, leading=12.5,
    textColor=colors.HexColor('#1e293b')
)
tbl_bold = ParagraphStyle(
    'TblBold', parent=tbl_body,
    fontName='Helvetica-Bold'
)
caption_title = ParagraphStyle(
    'CapTitle', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=11.0, leading=14.5,
    textColor=colors.HexColor('#0369a1'), alignment=1
)

def measure(flowables, width=540):
    total = 0
    for f in flowables:
        w, h = f.wrap(width, 1000)
        total += h
    return total

print("Test harness ready.")

