from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
import re

f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx")
d=Document(f)
paras=d.paragraphs
toc=next(p for p in paras if p.text.strip()=='Table Of Contents')
detail=next(p for p in paras if p.text.strip()=='Detailed Contents')
fig=next(p for p in paras if p.text.strip()=='LIST OF FIGURES')
chapter_body=next(p for p in paras if p.text.strip()=='CHAPTER 1')

# Keep the project's detailed technical subheadings visible and styled in the
# body, but remove them from outline-based TOC generation. Custom styles retain
# the corresponding Heading 2/3/1 appearance and use the body-text outline level.
def make_detail_style(level):
    name=f'Report Detail Heading {level}'
    if name in d.styles: return d.styles[name]
    base=d.styles[f'Heading {level}']
    style=d.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    style.base_style=d.styles['Normal']
    style.font.name=base.font.name or 'Times New Roman'
    style.font.size=base.font.size or Pt(12)
    style.font.bold=base.font.bold
    style.font.italic=base.font.italic
    style.font.color.rgb=base.font.color.rgb or RGBColor(0,0,0)
    pf=style.paragraph_format; bf=base.paragraph_format
    pf.alignment=bf.alignment; pf.left_indent=bf.left_indent; pf.right_indent=bf.right_indent
    pf.first_line_indent=bf.first_line_indent; pf.space_before=bf.space_before; pf.space_after=bf.space_after
    pf.line_spacing=bf.line_spacing; pf.keep_with_next=bf.keep_with_next
    pf.keep_together=bf.keep_together; pf.page_break_before=bf.page_break_before
    ppr=style._element.get_or_add_pPr()
    outline=ppr.find(qn('w:outlineLvl'))
    if outline is None: outline=OxmlElement('w:outlineLvl'); ppr.append(outline)
    outline.set(qn('w:val'),'9')
    return style

keep={
 '1.1 Need Identification','1.2 Identification of problem','1.3 Identification of tasks',
 '1.4 Timeline','1.5 Organization of the report',
 '2.1 Timeline of the reported problem','2.2 Proposed Solution','2.3 Bibliometric analysis',
 '2.4 Review Summary','2.5 Problem Definition','2.6 goals/ Objective',
 '2.7 Why Use Technologies Over Other',
 '3.1 Evaluation & Selection of Specifications/Features','3.2 Design Constraints',
 '3.3 Design Flow','3.4 Creation of “Multi-user Chatroom Application”',
 '3.5 Logo Designing and Naming','3.6 Implementation plan/methodology',
 '4.1 Implementation of solution','4.1.1 Report preparation',
 '4.1.2 Project management and communication',
 '4.1.3 Testing/characterization/interpretation/data validation',
 '5.1 Conclusion','5.2 Future Work'
}

body_started=False
for p in d.paragraphs:
    text=p.text.strip()
    if text=='CHAPTER 1': body_started=True
    if not body_started or not p.style or not p.style.name.startswith('Heading'): continue
    if text in {'CHAPTER 1','CHAPTER 2','CHAPTER 3','CHAPTER 4','CHAPTER 5',
                'INTRODUCTION','BACKGROUND STUDY','DESIGN AND PROCESS',
                'RESULT ANALYSIS AND VALIDATION','CONCLUSION AND FUTURE WORK'}:
        continue
    # Normalize the original main headings in the report body.
    replacements={
      '1.1. Need Identification':'1.1 Need Identification',
      '1.2. Identification of Problem':'1.2 Identification of problem',
      '1.3. Identification of Tasks':'1.3 Identification of tasks',
      '1.4. Timeline':'1.4 Timeline',
      '1.5. Organization of the Report':'1.5 Organization of the report',
      '2.1. Timeline of the Reported Problem':'2.1 Timeline of the reported problem',
      '2.2. Proposed Solution':'2.2 Proposed Solution',
      '2.3. Bibliometric Analysis':'2.3 Bibliometric analysis',
      '2.4. Review Summary':'2.4 Review Summary',
      '2.5 Problem Definition':'2.5 Problem Definition',
      '2.6 Goals/Objectives':'2.6 goals/ Objective',
      '2.7 Why Use These Technologies Over Others':'2.7 Why Use Technologies Over Other',
      '3.1 Evaluation and Selection of Specifications/Features':'3.1 Evaluation & Selection of Specifications/Features',
      '3.4 Creation of the Chatroom Application':'3.4 Creation of “Multi-user Chatroom Application”',
      '3.6 Implementation Plan/Methodology':'3.6 Implementation plan/methodology',
      '4.1 Implementation of Solution':'4.1 Implementation of solution',
      '4.1.1 Report preparation':'4.1.1 Report preparation',
      '4.1.2 Project management and communication':'4.1.2 Project management and communication',
      '4.1.3 Testing, characterization, interpretation and data validation':'4.1.3 Testing/characterization/interpretation/data validation',
      '5.1. Conclusion':'5.1 Conclusion',
      '5.2. Future Work':'5.2 Future Work',
    }
    if text in replacements:
        p.text=replacements[text]
        text=p.text.strip()
    if text not in keep:
        level=int(p.style.name.split()[-1])
        p.style=make_detail_style(level)

# Remove the old detailed contents block and rebuild the concise first index.
def remove_between(a,b):
    cur=a._p.getnext()
    while cur is not None and cur is not b._p:
        nxt=cur.getnext(); cur.getparent().remove(cur); cur=nxt
remove_between(toc,detail)
detail._p.getparent().remove(detail._p)

chapter_rows=[
 ('CHAPTER 1: INTRODUCTION','range'),
 ('CHAPTER 2: BACKGROUND STUDY','range'),
 ('CHAPTER 3: DESIGN AND PROCESS','range'),
 ('CHAPTER 4: RESULT ANALYSIS AND VALIDATION','range'),
 ('CHAPTER 5: CONCLUSION AND FUTURE WORK','range'),
]
section_rows=[
 ('1.1 Need Identification',1),('1.2 Identification of problem',1),
 ('1.3 Identification of tasks',1),('1.4 Timeline',1),('1.5 Organization of the report',1),
 ('2.1 Timeline of the reported problem',1),('2.2 Proposed Solution',1),
 ('2.3 Bibliometric analysis',1),('2.4 Review Summary',1),('2.5 Problem Definition',1),
 ('2.6 goals/ Objective',1),('2.7 Why Use Technologies Over Other',1),
 ('3.1 Evaluation & Selection of Specifications/Features',1),('3.2 Design Constraints',1),
 ('3.3 Design Flow',1),('3.4 Creation of “Multi-user Chatroom Application”',1),
 ('3.5 Logo Designing and Naming',1),('3.6 Implementation plan/methodology',1),
 ('4.1 Implementation of solution',1),('4.1.1 Report preparation',2),
 ('4.1.2 Project management and communication',2),
 ('4.1.3 Testing/characterization/interpretation/data validation',2),
 ('5.1 Conclusion',1),('5.2 Future Work',1),
]
section=d.sections[0]
right_tab=section.page_width-section.left_margin-section.right_margin-Inches(.15)

def add_row(label,indent,chapter=False):
    p=fig.insert_paragraph_before('',style='Normal')
    p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(6 if chapter else 3 if indent==1 else 1)
    p.paragraph_format.line_spacing=1
    p.paragraph_format.left_indent=Inches(0 if chapter else .48 if indent==1 else 1.18)
    p.paragraph_format.first_line_indent=Inches(0)
    p.paragraph_format.tab_stops.add_tab_stop(right_tab,WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    a=p.add_run(label); a.font.name='Times New Roman'; a._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); a.font.size=Pt(12); a.font.color.rgb=RGBColor(0,0,0)
    p.add_run('\t')
    b=p.add_run('?'); b.font.name='Times New Roman'; b._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); b.font.size=Pt(12); b.font.color.rgb=RGBColor(0,0,0)

for title,_ in chapter_rows:
    add_row(title,0,True)
    # preserve the original chapter order by inserting its subsections here
    chapter=title.split(':')[0].replace('CHAPTER ','')
    if chapter=='1': subset=section_rows[0:5]
    elif chapter=='2': subset=section_rows[5:12]
    elif chapter=='3': subset=section_rows[12:18]
    elif chapter=='4': subset=section_rows[18:22]
    else: subset=section_rows[22:24]
    for label,indent in subset: add_row(label,indent)

toc.alignment=1
fig.paragraph_format.page_break_before=True
d.save(f)
print('Rebuilt concise contents with',len(chapter_rows)+len(section_rows),'entries; detail headings excluded from outline TOC.')
