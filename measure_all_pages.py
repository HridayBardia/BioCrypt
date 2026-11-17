with open('build_clean_professional_report.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find build_pdf and insert measurement before doc.build
new_lines = []
for line in lines:
    if "doc.build(story, canvasmaker=NumberedCanvas)" in line:
        new_lines.append("""
    page_map = {'Page 01': p1, 'Page 03': p3, 'Page 05': p5, 'Page 07': p7, 'Page 09': p9, 'Page 11': p11, 'Page 12': p12, 'Page 13': p13, 'Page 14': p14, 'Page 15': p15}
    print("=== EXACT PAGE FLOWABLE HEIGHTS ===")
    for name, flowables in page_map.items():
        h_total = 0
        for f in flowables:
            w, h = f.wrap(540, 1000)
            h_total += h
        fill_pct = (h_total / 660.0) * 100.0
        print(f"{name}: Height = {h_total:5.1f} pt / 660 pt -> Fill: {fill_pct:5.1f}%")
""")
    new_lines.append(line)

code_mod = "".join(new_lines)
exec(code_mod, globals())
build_pdf()
