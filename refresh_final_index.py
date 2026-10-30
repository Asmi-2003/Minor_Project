from docx import Document
from pypdf import PdfReader
from pathlib import Path
import re

root=Path(r"D:\chat App")
doc_path=root/'Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.docx'
pdf_path=root/'Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Final.pdf'
doc=Document(doc_path)
pages=[p.extract_text() or '' for p in PdfReader(str(pdf_path)).pages]
norm=lambda s:re.sub(r'[^a-z0-9]','',s.casefold())

def locate(label,start=None):
    if start is None: start=body_start
    q=norm(label)
    for n,text in enumerate(pages,1):
        if n>=start and any(norm(line).startswith(q) for line in text.splitlines()): return n
    for n,text in enumerate(pages,1):
        if n>=start and q in norm(text): return n
    return None

paras=doc.paragraphs
toc_i=next(i for i,p in enumerate(paras) if p.text.strip()=='Table Of Contents')
fig_i=next(i for i,p in enumerate(paras) if p.text.strip()=='LIST OF FIGURES')
chapter_i=next(i for i,p in enumerate(paras) if p.text.strip()=='CHAPTER 1')
chapter_titles=['CHAPTER 1: INTRODUCTION','CHAPTER 2: BACKGROUND STUDY',
                'CHAPTER 3: DESIGN AND PROCESS','CHAPTER 4: RESULT ANALYSIS AND VALIDATION',
                'CHAPTER 5: CONCLUSION AND FUTURE WORK']
def chapter_start(n):
    key=f'chapter{n}'
    return next((i for i,t in enumerate(pages,1) if i>=3 and any(norm(line)==key for line in t.splitlines())),None)
starts=[chapter_start(n) for n in range(1,6)]
body_start=starts[0]
refs=next((n for n,t in enumerate(pages,1) if n>=3 and any(norm(x)=='references' for x in t.splitlines())),None)
plag=next((n for n,t in enumerate(pages,1) if n>=3 and any(norm(x)=='plagiarismreport' for x in t.splitlines())),None)
if any(x is None for x in starts) or refs is None or plag is None: raise RuntimeError((starts,refs,plag))
range_map={title:f'{starts[i]}-{starts[i+1]-1}' for i,title in enumerate(chapter_titles[:4])}
range_map[chapter_titles[4]]=f'{starts[4]}-{refs-1}'
unresolved=[]

def update(start,end,figure=False):
    for p in paras[start+1:end]:
        if len(p.runs)<3: continue
        label=p.runs[0].text.strip()
        if not label or not p.runs[-1].text.strip(): continue
        if figure: label=re.sub(r'^Fig\s+\d+\s*','',label)
        n=norm(label)
        if n=='references': page=refs
        elif n=='plagiarismreport': page=plag
        else: page=locate(label)
        value=range_map.get(label,str(page) if page is not None else None)
        if value is None: unresolved.append(label)
        else: p.runs[-1].text=value

update(toc_i,fig_i)
update(fig_i,chapter_i,figure=True)
doc.save(doc_path)
print('rendered pages',len(pages),'chapter starts',starts,'references',refs,'plagiarism',plag,'unresolved',len(unresolved))
if unresolved: print('\n'.join(unresolved))
