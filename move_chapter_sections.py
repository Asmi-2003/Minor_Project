from docx import Document
from pathlib import Path
from docx.oxml.ns import qn
import re

f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx")
d=Document(f)
body=d._body._element
children=list(body)

def para_text(el):
    if el.tag!=qn('w:p'): return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t'))).strip()

def heading_num(text):
    m=re.match(r'^(\d+)\.(\d+)\s+',text)
    return m.group(1) if m else None

chapter3_heads={'3.7','3.8','3.9','3.10','3.11','3.12','3.13','3.14','3.15','3.16'}
chapter4_heads={'4.3','4.4','4.5','4.6','4.7','4.8'}
chapter5_heads={'5.3','5.4','5.5'}
recognized=chapter3_heads|chapter4_heads|chapter5_heads

# Identify the back-matter section blocks by their new top-level section labels.
refs=next(el for el in children if para_text(el)=='REFERENCES')
ref_index=children.index(refs)
chapter5_body=next(el for el in children if para_text(el)=='CHAPTER 5')
chapter5_index=children.index(chapter5_body)
start_candidates=[]
for i,el in enumerate(children[chapter5_index+1:ref_index],chapter5_index+1):
    txt=para_text(el)
    m=re.match(r'^(\d+\.\d+)\s+',txt)
    if m and m.group(1) in recognized: start_candidates.append((i,m.group(1)))
if len(start_candidates)!=19: raise RuntimeError(f'Expected 19 moved sections, found {len(start_candidates)}')

blocks=[]
for j,(start,label) in enumerate(start_candidates):
    end=start_candidates[j+1][0] if j+1<len(start_candidates) else ref_index
    nodes=children[start:end]
    dest='chapter3' if label in chapter3_heads else 'chapter4' if label in chapter4_heads else 'chapter5'
    blocks.append((dest,nodes,label))

chapter4=next(el for el in children if para_text(el)=='CHAPTER 4')
chapter5=next(el for el in children if para_text(el)=='CHAPTER 5')

# Detach the back-matter blocks, preserving all paragraphs, tables, drawings,
# captions and local formatting, then insert them into the matching chapter.
for _,nodes,_ in blocks:
    for el in nodes:
        if el.getparent() is body: body.remove(el)

for destination,anchor in [('chapter3',chapter4),('chapter4',chapter5),('chapter5',refs)]:
    for dest,nodes,label in blocks:
        if dest==destination:
            for el in nodes: anchor.addprevious(el)

d.save(f)
print('moved sections',len(blocks),'to chapters 3, 4, and 5')
