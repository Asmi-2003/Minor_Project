from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy
from pathlib import Path
import re

SRC=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_72_Pages.docx")
OUT=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx")
doc=Document(SRC)

mapping={
 'A':('3.7','Source Code Structure and Module Responsibilities'),
 'B':('3.8','REST API Design and Request Handling'),
 'C':('3.9','Real-Time Messaging and Event Processing'),
 'D':('3.10','Data Model and Persistence'),
 'E':('3.11','User Interaction and Client State'),
 'F':('4.3','Verification Strategy and Test Design'),
 'G':('3.12','Local Configuration and Reproducible Execution'),
 'H':('5.3','Security, Reliability and Scalability Review'),
 'I':('5.4','Maintainability and Extension Design'),
 'J':('3.13','Requirements Traceability and Technical Terminology'),
 'K':('3.14','Worked REST API Exchanges and Contract Compatibility'),
 'L':('4.4','End-to-End Communication Scenarios'),
 'M':('4.5','Detailed Test Case Design'),
 'N':('3.15','Source-to-Behavior Maintenance'),
 'O':('5.5','Usability, Accessibility and Responsible Use'),
 'P':('4.6','Acceptance Criteria and Requirement Verification'),
 'Q':('3.16','Data Fields, Payloads and Validation'),
 'R':('4.7','Error Handling and Recovery Analysis'),
 'S':('4.8','Performance Evaluation Plan'),
}

# Relabel the former appendix material as numbered sections under the matching
# design, validation, and conclusion chapters. Text and paragraph formatting
# remain in the document; only heading level and numbering are changed.
current_letter=None
sub_index=0
for p in doc.paragraphs:
    text=p.text.strip()
    m=re.match(r'^APPENDIX ([A-S]):\s*(.*)$',text,re.I)
    if m:
        letter=m.group(1).upper(); current_letter=letter; sub_index=0
        num,title=mapping[letter]
        p.text=f"{num} {title}"
        p.style='Heading 2'
        continue
    m=re.match(r'^([A-S])\.(\d+)\s+(.*)$',text)
    if m and m.group(1) in mapping:
        letter=m.group(1); num,_=mapping[letter]
        p.text=f"{num}.{m.group(2)} {m.group(3)}"
        p.style='Heading 3'
        continue
    if 'appendix' in text.casefold():
        p.text=re.sub(r'(?i)\bthis appendix\b','this section',p.text)
        p.text=re.sub(r'(?i)\bappendix\b','section',p.text)

# Change references in the two static contents blocks to match the new chapter
# hierarchy, then rebuild both lists from the actual Heading 1-3 paragraphs.
paras=doc.paragraphs
toc_title=next(p for p in paras if p.text.strip()=='Table Of Contents')
detail_title=next(p for p in paras if p.text.strip()=='Detailed Contents')
fig_title=next(p for p in paras if p.text.strip()=='LIST OF FIGURES')
chapter_body=next(p for p in paras if p.text.strip()=='CHAPTER 1')
toc_template=next(p for p in paras if p.text.strip().startswith('CHAPTER 1: INTRODUCTION .'))
detail_template=next(p for p in paras if re.match(r'^\d+\.\d+\.\d+\s',p.text.strip()))

def remove_between(a,b):
    cur=a._p.getnext()
    while cur is not None and cur is not b._p:
        nxt=cur.getnext(); cur.getparent().remove(cur); cur=nxt

def insert_row_before(anchor, template, label, page='?'):
    cloned=deepcopy(template._p)
    anchor._p.addprevious(cloned)
    runs=cloned.findall('.//'+qn('w:r'))
    # Keep the template's first label, dot leaders, and final page fields.
    tr=[]
    for run in runs:
        t=run.find(qn('w:t'))
        if t is not None: tr.append(t)
    if len(tr)<3: raise RuntimeError('Contents exemplar does not have label/dots/page runs')
    tr[0].text=label
    tr[1].text=' .  .  .  . '
    tr[2].text=str(page)
    for extra in tr[3:]: extra.text=''

def body_headings():
    result=[]
    started=False
    for p in doc.paragraphs:
        if p.text.strip()=='CHAPTER 1': started=True
        if not started: continue
        text=p.text.strip()
        if text=='REFERENCES': break
        if not text or not p.style or p.style.name not in ('Heading 1','Heading 2','Heading 3'): continue
        if text in ('CHAPTER 1','CHAPTER 2','CHAPTER 3','CHAPTER 4','CHAPTER 5'):
            continue
        if p.style.name=='Heading 1' and text in ('INTRODUCTION','BACKGROUND STUDY','DESIGN AND PROCESS','RESULT ANALYSIS AND VALIDATION','CONCLUSION AND FUTURE WORK'):
            continue
        level=int(p.style.name.split()[-1])
        result.append((p,level,text))
    return result

headings=body_headings()
remove_between(toc_title,detail_title)
remove_between(detail_title,fig_title)

# Use all real chapter titles and section headings in the main contents, with
# all third-level headings on the detailed contents page(s).
chapters=[('CHAPTER 1: INTRODUCTION','chapter 1'),('CHAPTER 2: BACKGROUND STUDY','chapter 2'),
          ('CHAPTER 3: DESIGN AND PROCESS','chapter 3'),('CHAPTER 4: RESULT ANALYSIS AND VALIDATION','chapter 4'),
          ('CHAPTER 5: CONCLUSION AND FUTURE WORK','chapter 5')]
for title,_ in chapters: insert_row_before(detail_title,toc_template,title,'?')
for p,level,text in headings:
    if level==2: insert_row_before(detail_title,toc_template,text,'?')
for ending in ('REFERENCES','PLAGIARISM REPORT'):
    insert_row_before(detail_title,toc_template,ending,'?')
for p,level,text in headings:
    if level==3: insert_row_before(fig_title,detail_template,text,'?')

# Keep static page-number placeholders until the PDF render is parsed; then the
# companion indexing pass replaces every value with a verified page number.
for p in doc.paragraphs:
    if p.text.strip().endswith('.  .  .  .  ?'):
        pass

doc.save(OUT)
print('saved',OUT,'numbered sections',len(mapping),'TOC headings',len(headings))
