import re

with open('build_perfect_report.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's split by PageBreak
sections = code.split('story.append(PageBreak())')
print(f"Total sections: {len(sections)-1}")

for i, sec in enumerate(sections[:-1], 1):
    is_even = (i % 2 == 0)
    title_match = re.search(r'# PAGE \d+.*?: (.*)', sec)
    title = title_match.group(1) if title_match else "Unknown"
    has_img = "add_even_page_big_image" in sec
    print(f"Page {i:02d} ({'EVEN' if is_even else 'ODD '}): Image={has_img} | Title={title[:40]} | RawLen={len(sec)}")

