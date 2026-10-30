from docx import Document
from docx.shared import Pt
from pathlib import Path
f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx")
d=Document(f)
active=False
for p in d.paragraphs:
    t=p.text.strip()
    if t=='Table Of Contents': active=True; continue
    if t=='LIST OF FIGURES': break
    if not active or not t: continue
    if t.startswith('CHAPTER '): p.paragraph_format.space_after=Pt(9)
    elif t.startswith('4.1.1 ') or t.startswith('4.1.2 ') or t.startswith('4.1.3 '): p.paragraph_format.space_after=Pt(5)
    else: p.paragraph_format.space_after=Pt(7)
d.save(f)
print('Adjusted TOC row spacing to match the reference page.')
