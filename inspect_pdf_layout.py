import pypdf

reader = pypdf.PdfReader('BioCrypt_DNA_Comprehensive_Report.pdf')
print(f"Total pages: {len(reader.pages)}")

for idx, page in enumerate(reader.pages):
    p_num = idx + 1
    text = page.extract_text() or ""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_3 = " // ".join(lines[:3]) if lines else "EMPTY"
    last_line = lines[-1] if lines else "EMPTY"
    print(f"Page {p_num:02d} ({'EVEN' if p_num%2==0 else 'ODD '}): len={len(text):4d}, lines={len(lines):2d}, imgs={len(page.images)}")
    print(f"   Top: {first_3[:75]}")
    print(f"   Btm: {last_line[:75]}")
    print("-" * 80)

