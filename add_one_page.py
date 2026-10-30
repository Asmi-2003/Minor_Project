from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from pathlib import Path

f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_72_Pages.docx")
d=Document(f)
anchor=next(p for p in d.paragraphs if p.text.strip().casefold() == '5.2. future work')
text=("A practical implementation roadmap should sequence these improvements so that each step has a verifiable outcome. First, define a message contract with a server-generated identifier, validated room reference, authenticated sender and timestamp, then cover its serialization with API and broker tests. Second, introduce authorization checks that derive the sender from the authenticated connection and confirm the requested room membership before accepting a message or presence event. Third, separate message persistence from the Room aggregate and provide indexed, bounded history queries with stable ordering. A migration should preserve existing room messages and validate their counts before the old representation is retired. Fourth, move ephemeral presence and broker routing to shared infrastructure only if a multi-instance deployment is an actual requirement. Each stage should include failure cases, such as expired credentials, inaccessible rooms, database outages and reconnects, so that the user interface can communicate the state accurately.\n\nThe roadmap also provides a basis for measurable evaluation. A test environment can record message acceptance, persistence completion and delivery to each subscribed client, then compare those outcomes under a stated number of concurrent sessions and message rates. Reliability checks should include a backend restart, a dropped network connection and recovery from the history endpoint. Security review should examine password handling, origin configuration, transport protection, authorization boundaries and accidental exposure in logs. Usability evaluation can observe whether participants understand the active room, connection indicator and transient typing cue. These measurements must be conducted and documented before they are presented as results. The source project currently establishes a functional educational prototype and provides a narrow context-load test; it does not supply such load, security or user-study evidence. Accordingly, the roadmap is a proposal for responsible extension, not a claim about completed work.")
p=anchor.insert_paragraph_before(text, style='Normal')
p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1
for r in p.runs:
 r.font.name='Times New Roman'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); r.font.size=Pt(12); r.font.color.rgb=RGBColor(0,0,0)
d.save(f)
print(len(text.split()))
