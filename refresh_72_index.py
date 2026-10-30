from docx import Document
from pypdf import PdfReader
from pathlib import Path
import re

base = Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_72_Pages")
doc = Document(str(base.with_suffix(".docx")))
pdf = PdfReader(str(base.with_suffix(".pdf")))
pages = [p.extract_text() or "" for p in pdf.pages]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def locate(label, start=6):
    q = norm(label)
    for n, text in enumerate(pages, 1):
        if n >= start and any(norm(line).startswith(q) for line in text.splitlines()):
            return n
    for n, text in enumerate(pages, 1):
        if n >= start and q in norm(text):
            return n
    return None

body_headings = [p.text.strip() for p in doc.paragraphs
                 if p.style and p.style.name.startswith("Heading") and p.text.strip()]

def locate_number(label):
    m = re.match(r"^(\d+(?:\.\d+)*)", label)
    if not m:
        return None
    parts = m.group(1).split(".")
    for width in range(len(parts), 0, -1):
        prefix = ".".join(parts[:width])
        for title in body_headings:
            if re.match(r"^" + re.escape(prefix) + r"(?:\.|\s|$)", title):
                page = locate(title)
                if page:
                    return page
    return None

refs_page = next((n for n, text in enumerate(pages, 1)
                  if n >= 6 and any(norm(line) == "references" for line in text.splitlines())), None)
plag_page = next((n for n, text in enumerate(pages, 1)
                  if n >= 6 and any(norm(line) == "plagiarismreport" for line in text.splitlines())), None)
chapter_titles = [
    "CHAPTER 1 INTRODUCTION", "CHAPTER 2 BACKGROUND STUDY",
    "CHAPTER 3 DESIGN AND PROCESS", "CHAPTER 4 RESULT ANALYSIS AND VALIDATION",
    "CHAPTER 5 CONCLUSION AND FUTURE WORK",
]
chapter_starts = [locate(x) for x in chapter_titles]
appendix_a = locate("APPENDIX A: SOURCE CODE AND MODULE INVENTORY")
range_map = {
    "CHAPTER 1: INTRODUCTION": f"{chapter_starts[0]}-{chapter_starts[1]-1}",
    "CHAPTER 2: BACKGROUND STUDY": f"{chapter_starts[1]}-{chapter_starts[2]-1}",
    "CHAPTER 3: DESIGN AND PROCESS": f"{chapter_starts[2]}-{chapter_starts[3]-1}",
    "CHAPTER 4: RESULT ANALYSIS AND VALIDATION": f"{chapter_starts[3]}-{chapter_starts[4]-1}",
    "CHAPTER 5: CONCLUSION AND FUTURE WORK": f"{chapter_starts[4]}-{appendix_a-1}",
}

paras = doc.paragraphs
toc_i = next(i for i, p in enumerate(paras) if p.text == "Table Of Contents")
detail_i = next(i for i, p in enumerate(paras) if p.text == "Detailed Contents")
fig_i = next(i for i, p in enumerate(paras) if p.text == "LIST OF FIGURES")
chapter_i = next(i for i, p in enumerate(paras) if p.text == "CHAPTER 1")
unresolved = []

def update_rows(start, end, figure=False):
    for p in paras[start + 1:end]:
        if len(p.runs) < 3:
            continue
        label = p.runs[0].text.strip()
        if not label or not p.runs[-1].text.strip():
            continue
        if label.startswith("Appendix Appendix "):
            label = label.replace("Appendix Appendix ", "Appendix ", 1)
            p.runs[0].text = label
        if figure:
            label = re.sub(r"^Fig\s+\d+\s+", "", label)
        if norm(label) == "references":
            page = refs_page
        elif norm(label) == "plagiarismreport":
            page = plag_page
        else:
            page = locate(label)
            if page is None:
                page = locate_number(label)
        value = range_map.get(label)
        if value is None and page is not None:
            value = str(page)
        if value is None:
            unresolved.append(label)
        else:
            p.runs[-1].text = value

update_rows(toc_i, detail_i)
update_rows(detail_i, fig_i)
update_rows(fig_i, chapter_i, figure=True)
doc.save(str(base.with_suffix(".docx")))
print("page count", len(pages), "chapter starts", chapter_starts,
      "appendix A", appendix_a, "references", refs_page, "plagiarism", plag_page)
print("unresolved index rows", unresolved)

