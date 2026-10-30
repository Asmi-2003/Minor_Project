from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

path = r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.docx"
doc = Document(path)
paras = doc.paragraphs
fig_heading = next(p for p in paras if p.text == "LIST OF FIGURES")
fig_index = paras.index(fig_heading)
fig1 = next(p for p in paras[fig_index + 1:] if p.text.startswith("Fig 1  "))
fig1_index = paras.index(fig1)
section_break = next(p for p in paras if p._p.xpath('./w:pPr/w:sectPr'))

# Appendix detail entries were inserted after the figure-list heading. Move
# them back to the Detailed Contents page, before the existing section break.
detail_rows = [p for p in paras[fig_index + 1:fig1_index]
               if p.text.startswith("Appendix ") and " . " in p.text]
values = [(p.runs[0].text, p.runs[-1].text) for p in detail_rows]
for p in detail_rows:
    p._element.getparent().remove(p._element)
for title, page in values:
    p = section_break.insert_paragraph_before()
    p.paragraph_format.space_after = Pt(0)
    for value in (title, " . " * 4, page):
        r = p.add_run(value)
        r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.color.rgb = RGBColor(0, 0, 0)
        r._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")

# Allow the final references note to share the available page space.
for p in doc.paragraphs:
    if p.text.startswith("Project-specific implementation claims"):
        p.paragraph_format.page_break_before = False
        p.paragraph_format.keep_together = False
        p.paragraph_format.keep_with_next = False
        break

doc.save(path)
print("moved appendix index rows", len(values), "before the figures section")
