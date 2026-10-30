from docx import Document
from pypdf import PdfReader
import re

doc = Document(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.docx")
pdf = PdfReader(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.pdf")
pages = [" ".join((p.extract_text() or "").split()) for p in pdf.pages]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

for p in doc.paragraphs:
    if not (p.style and p.style.name.startswith("Heading") and p.text.strip()):
        continue
    query = norm(p.text)
    hits = [n + 1 for n, text in enumerate(pages) if query and query in norm(text)]
    print((hits[0] if hits else "?"), p.text)

print("FIGURES")
for n in range(1, 15):
    query = norm(f"Fig {n}")
    hits = [i + 1 for i, text in enumerate(pages) if query in norm(text) and i + 1 != 5]
    print(n, hits)
