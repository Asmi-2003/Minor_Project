from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml.ns import qn
from pathlib import Path

f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx")
d=Document(f)
toc=next(p for p in d.paragraphs if p.text.strip()=='Table Of Contents')
fig=next(p for p in d.paragraphs if p.text.strip()=='LIST OF FIGURES')
cur=toc._p.getnext()
while cur is not None and cur is not fig._p:
    nxt=cur.getnext(); cur.getparent().remove(cur); cur=nxt

chapters=[
 ('CHAPTER 1: INTRODUCTION',[('1.1 Need Identification',1),('1.2 Identification of problem',1),('1.3 Identification of tasks',1),('1.4 Timeline',1),('1.5 Organization of the report',1)]),
 ('CHAPTER 2: BACKGROUND STUDY',[('2.1 Timeline of the reported problem',1),('2.2 Proposed Solution',1),('2.3 Bibliometric analysis',1),('2.4 Review Summary',1),('2.5 Problem Definition',1),('2.6 goals/ Objective',1),('2.7 Why Use Technologies Over Other',1)]),
 ('CHAPTER 3: DESIGN AND PROCESS',[('3.1 Evaluation & Selection of Specifications/Features',1),('3.2 Design Constraints',1),('3.3 Design Flow',1),('3.4 Creation of “Multi-user Chatroom Application”',1),('3.5 Logo Designing and Naming',1),('3.6 Implementation plan/methodology',1)]),
 ('CHAPTER 4: RESULT ANALYSIS AND VALIDATION',[('4.1 Implementation of solution',1),('4.1.1 Report preparation',2),('4.1.2 Project management and communication',2),('4.1.3 Testing/characterization/interpretation/data validation',2)]),
 ('CHAPTER 5: CONCLUSION AND FUTURE WORK',[('5.1 Conclusion',1),('5.2 Future Work',1)]),
]
sec=d.sections[0]
right_tab=sec.page_width-sec.left_margin-sec.right_margin-Inches(.12)
for chapter,items in chapters:
    for label,level in [(chapter,0)]+items:
        p=fig.insert_paragraph_before('',style='Normal')
        p.paragraph_format.space_before=Pt(0)
        p.paragraph_format.space_after=Pt(5 if level==0 else 3 if level==1 else 1)
        p.paragraph_format.line_spacing=1
        p.paragraph_format.left_indent=Inches(0 if level==0 else .5 if level==1 else 1.25)
        p.paragraph_format.first_line_indent=Inches(0)
        p.paragraph_format.tab_stops.add_tab_stop(right_tab,WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
        for val in [label,'\t','?']:
            r=p.add_run(val); r.font.name='Times New Roman'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); r.font.size=Pt(12); r.font.color.rgb=RGBColor(0,0,0)
toc.alignment=1
fig.paragraph_format.page_break_before=True
d.save(f)
print('Rebuilt index with',sum(1+len(items) for _,items in chapters),'entries and removed old detailed index rows.')
