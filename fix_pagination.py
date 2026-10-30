from docx import Document
from pathlib import Path
from docx.oxml.ns import qn
from pypdf import PdfReader
import re

source = r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary.docx"
output = r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.docx"
doc = Document(source)
paragraphs = doc.paragraphs
print("paragraphs", len(paragraphs), "sections", len(doc.sections))

# Keep the supplied cover/certificate/contents/list pages and the chapter,
# references, and final-report boundaries. Subsection-level breaks are removed.
keep_before = {
    "BONAFIDE CERTIFICATE",
    "Table Of Contents",
    "Detailed Contents",
    "CHAPTER 1",
    "CHAPTER 2",
    "CHAPTER 3",
    "CHAPTER 4",
    "CHAPTER 5",
    "REFERENCES",
    "Plagiarism Report",
}

removed = 0
for i in range(len(paragraphs) - 1, -1, -1):
    paragraph = paragraphs[i]
    page_breaks = paragraph._p.xpath('.//w:br[@w:type="page"]')
    if not page_breaks:
        continue
    next_text = paragraphs[i + 1].text.strip() if i + 1 < len(paragraphs) else ""
    if next_text in keep_before:
        continue
    # These are dedicated, empty page-break paragraphs; remove the paragraph
    # itself so it cannot continue reserving vertical space.
    if not paragraph.text.strip():
        paragraph._element.getparent().remove(paragraph._element)
        removed += 1
    else:
        for br in page_breaks:
            br.getparent().remove(br)
        removed += 1

# Let body paragraphs split naturally. Heading keep-with-next rules already
# present in the document are retained so headings stay with their first line.
for paragraph in doc.paragraphs:
    fmt = paragraph.paragraph_format
    if paragraph.style and paragraph.style.name.startswith("Heading"):
        fmt.page_break_before = False
        fmt.keep_together = False
        fmt.keep_with_next = True
    else:
        fmt.page_break_before = False
        fmt.keep_together = False

# Preserve row borders and styling while avoiding fixed minimum heights.
for table in doc.tables:
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        for cant_split in tr_pr.findall(qn("w:cantSplit")):
            tr_pr.remove(cant_split)

# Refresh the existing static index and figure-list page references from the
# rendered pagination. This changes only page-number fields' displayed text.
pdf_path = Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.pdf")
if pdf_path.exists():
    rendered = PdfReader(str(pdf_path))
    page_text = [p.extract_text() or "" for p in rendered.pages]
    normalize = lambda value: re.sub(r"[^a-z0-9]", "", value.lower())

    def locate(label, start_page=6):
        query = normalize(label)
        if not query:
            return None
        for page_no, text in enumerate(page_text, 1):
            if page_no < start_page:
                continue
            if any(normalize(line).startswith(query) for line in text.splitlines()):
                return page_no
        for page_no, text in enumerate(page_text, 1):
            if page_no >= start_page and query in normalize(text):
                return page_no
        return None

    body_headings = [
        p.text.strip() for p in doc.paragraphs
        if p.style and p.style.name.startswith("Heading") and p.text.strip()
    ]

    def locate_by_number(label):
        match = re.match(r"^(\d+(?:\.\d+)*)", label)
        if not match:
            return None
        number = match.group(1)
        parts = number.split(".")
        for length in range(len(parts), 0, -1):
            prefix = ".".join(parts[:length])
            for title in body_headings:
                if re.match(r"^" + re.escape(prefix) + r"(?:\.|\s|$)", title):
                    found = locate(title)
                    if found is not None:
                        return found
        return None

    chapter_starts = [
        locate("CHAPTER 1 INTRODUCTION"), locate("CHAPTER 2 BACKGROUND STUDY"),
        locate("CHAPTER 3 DESIGN AND PROCESS"),
        locate("CHAPTER 4 RESULT ANALYSIS AND VALIDATION"),
        locate("CHAPTER 5 CONCLUSION AND FUTURE WORK"),
    ]
    references_page = next(
        (page_no for page_no, text in enumerate(page_text, 1)
         if page_no >= 6 and any(normalize(line) == normalize("REFERENCES") for line in text.splitlines())),
        None,
    )
    chapter_ranges = {
        "CHAPTER 1: INTRODUCTION": f"{chapter_starts[0]}-{chapter_starts[1]-1}",
        "CHAPTER 2: BACKGROUND STUDY": f"{chapter_starts[1]}-{chapter_starts[2]-1}",
        "CHAPTER 3: DESIGN AND PROCESS": f"{chapter_starts[2]}-{chapter_starts[3]-1}",
        "CHAPTER 4: RESULT ANALYSIS AND VALIDATION": f"{chapter_starts[3]}-{chapter_starts[4]-1}",
        "CHAPTER 5: CONCLUSION AND FUTURE WORK": f"{chapter_starts[4]}-{references_page-1}",
    }

    all_paragraphs = doc.paragraphs
    toc_start = next(i for i, p in enumerate(all_paragraphs) if p.text == "Table Of Contents")
    detail_start = next(i for i, p in enumerate(all_paragraphs) if p.text == "Detailed Contents")
    figure_start = next(i for i, p in enumerate(all_paragraphs) if p.text == "LIST OF FIGURES")
    chapter1_start = next(i for i, p in enumerate(all_paragraphs) if p.text == "CHAPTER 1")
    unresolved = []

    def update_rows(start, stop, figures=False):
        for p in all_paragraphs[start + 1:stop]:
            if len(p.runs) < 3 or not p.runs[-1].text.strip():
                continue
            label = p.runs[0].text.strip()
            if figures:
                label = re.sub(r"^Fig\s+\d+\s+", "", label)
            page_no = references_page if normalize(label) == normalize("REFERENCES") else locate(label)
            if page_no is None:
                page_no = locate_by_number(label)
            value = chapter_ranges.get(label)
            if value is None and page_no is not None:
                value = str(page_no)
            if value is None:
                unresolved.append(label)
                continue
            p.runs[-1].text = value

    update_rows(toc_start, detail_start)
    update_rows(detail_start, figure_start)
    update_rows(figure_start, chapter1_start, figures=True)
    print("unresolved index entries", unresolved)

doc.save(output)
print("removed subsection page breaks", removed)
print("saved", output)
