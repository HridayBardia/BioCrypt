import pypdf

reader = pypdf.PdfReader('BioCrypt_DNA_Comprehensive_Report.pdf')
num_pages = len(reader.pages)
print(f"Total pages in PDF: {num_pages}")

for i in range(num_pages):
    page_num = i + 1
    page = reader.pages[i]
    text = page.extract_text() or ''
    num_chars = len(text.strip())
    num_images = len(page.images)
    kind = "EVEN" if page_num % 2 == 0 else "ODD "
    first_line = text.split("\n")[0] if text else "[BLANK / EMPTY]"
    print(f"Page {page_num:2d} ({kind}): {num_chars:4d} chars, {num_images} images | First line: {first_line[:65]}")
