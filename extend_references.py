from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from pathlib import Path
f=Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_72_Pages.docx")
d=Document(f)
anchor=next(p for p in d.paragraphs if p.text.strip().startswith('Project-specific implementation claims are based'))
refs=[
"16. Oracle. Java Platform, Standard Edition 21 API Specification. https://docs.oracle.com/en/java/javase/21/docs/api/",
"17. Spring. Spring Framework Web MVC Reference. https://docs.spring.io/spring-framework/reference/web/webmvc.html",
"18. Spring. STOMP over WebSocket Messaging. https://docs.spring.io/spring-framework/reference/web/websocket/stomp.html",
"19. World Wide Web Consortium. STOMP Protocol Specification, Version 1.2. https://stomp.github.io/stomp-specification-1.2.html",
"20. IETF. RFC 6455: The WebSocket Protocol. https://www.rfc-editor.org/rfc/rfc6455",
"21. OWASP Foundation. Authentication Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
"22. OWASP Foundation. Password Storage Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
"23. MongoDB. Embedded Data Models. https://www.mongodb.com/docs/manual/data-modeling/embedding/",
"24. Spring. Spring Boot Testing Reference. https://docs.spring.io/spring-boot/reference/testing/index.html",
"25. React Router. Routing Documentation. https://reactrouter.com/start/declarative/routing",
"26. W3C. Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/",
"27. Mozilla. Using the WebSocket API. https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API",
]
for text in refs:
 p=anchor.insert_paragraph_before(text,style='Normal')
 p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1
 for r in p.runs:
  r.font.name='Times New Roman'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman'); r.font.size=Pt(12); r.font.color.rgb=RGBColor(0,0,0)
d.save(f)
print('Added',len(refs),'technical references')
