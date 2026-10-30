from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from pathlib import Path

PATH = Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_72_Pages.docx")
doc = Document(PATH)

expansions = {
 "Real-time delivery and data persistence": [
  "The users of the application include a person entering a room as a guest, a person using an account, and other browser sessions already subscribed to the same room. Their shared need is not merely to submit text, but to observe a conversation as it develops and to understand which room is active. The interface therefore combines room identity, message history, current connection state and participant feedback. Each of these concerns is represented by a different part of the implementation, so their coordination is an important part of the project problem.",
  "A room-based conversation also creates expectations about continuity. A user who returns to an existing room expects to see recent messages, while transient activity such as typing should not be mistaken for durable conversation. The code addresses these expectations through MongoDB-backed Room and Message data for history and in-memory session state for presence. This distinction establishes a useful functional boundary: persisted records survive navigation when the database is available, whereas presence and typing describe current activity and are reconstructed or allowed to expire.",
  "The project is intended as a browser application for small collaborative conversations. Its current implementation supports text messages and a bounded initial history response, with a visible participant list and connection badge. It does not establish a private group through authorization, nor does it provide media transfer, moderation or a guaranteed delivery protocol. Stating this context prevents a reader from interpreting the term chatroom as a claim that every capability of a commercial messaging service is present.",
 ],
 "1.2. Identification of Problem": [
  "The communication problem can be expressed through a typical interaction. A user opens a room, receives the most recent stored messages, and then remains subscribed to new events. Another user submits a message. The service must validate the content, associate it with the room selected by the destination, save it, and make it available to active subscribers. If the room identifier is missing or does not resolve, the service must not silently create a room as a side effect of sending a message.",
  "The interface and server also have to handle partial failure. The HTTP request used to retrieve history can fail independently of the WebSocket connection, and the participant endpoint can fail without necessarily preventing history from loading. A live connection can be lost while a user is composing text. These cases require distinct states rather than one generic success/failure flag. The current client uses separate loading, history error and connection status state, which provides a foundation for communicating those differences.",
  "A further problem is identity and trust. Registration and password checking exist, but the message sender field is supplied by the browser and is not bound to a verified principal by the current message handler. A room identifier is used as a locator, not as proof of membership. Therefore, the core project problem is real-time coordination and persistence, while production-grade identity enforcement remains outside the implemented boundary and must be treated as a limitation.",
 ],
 "1.3. Identification of Tasks": [
  "The work can be traced to concrete artifacts in the repository. The React route setup and pages provide the user journey; API modules provide account and room requests; the STOMP hook provides subscriptions and sends; Java controllers handle HTTP and broker messages; repositories and MongoDB entities provide durable storage; and RoomParticipantService provides process-local session state. This mapping is a description of the delivered structure and does not assign dates or claim a project schedule that is not present in the source history.",
  "Integration tasks include agreeing on endpoint paths, request properties, message destinations and event fields across JavaScript and Java. The frontend's MessageRequest JSON must correspond to the DTO consumed by ChatController. The route's room identifier must correspond to the identifier used to find a Room document and construct a topic. The participant event fields must be interpreted consistently by the service and the React callback. These cross-layer agreements are where otherwise independent modules become one working application.",
  "A refinement task is to distinguish implementation from verification. The repository includes a Spring context-load test, but that test does not prove all account, persistence, WebSocket or browser behavior. A complete task plan should therefore separate code construction from functional verification and record which checks were actually run. The report describes the implemented behaviors and proposes additional cases without reporting unobserved results.",
 ],
 "Persistent data and session state": [
  "The need for ongoing communication arises because an HTTP request/response exchange is naturally finite. A client can ask for a page of messages and receive a response, but repeated polling would require the browser to ask again even when nothing changed. A persistent messaging connection gives the server a path to publish an event when a new message or room update occurs. This is useful for a chatroom because several clients can be waiting for the same room topic at the same time.",
  "The project separates this live channel from its history interface. REST is used for account operations, room creation and lookup, message history and participant reads. STOMP over SockJS is used for message, typing, join and leave events. The split makes the responsibilities visible: a finite query returns a snapshot, while a subscription stays available for future events. Neither channel replaces the other; history supports reload and catch-up, while the subscription supports interaction during an active session.",
  "Real-time delivery does not by itself define durable storage, ordering or acknowledgement. The backend explicitly saves an accepted message to the room document before returning it to the topic broker, and the history endpoint later reads the stored list. The typing event follows a different path and is not saved. This is a deliberate distinction between conversation data and transient activity, but it still leaves reconnect recovery and exactly-once delivery as future design concerns.",
 ],
 "Room and history capabilities": [
  "The proposed system is organized as a React client, a Spring Boot application and a MongoDB data store. The browser handles form interaction, route selection and local presentation state. The backend validates requests, performs room and account lookups, writes accepted messages and routes room events. MongoDB stores User and Room documents, with messages embedded inside their Room. The simple broker routes live events within the running application process.",
  "Each interaction type has a separate path through this architecture. Account submission travels from an auth card through authApi to AuthController and UserRepo. Room creation and lookup travel through roomApi to RoomController and RoomRepo. History follows a room-specific REST endpoint. Live message submission uses the STOMP client and ChatController, then proceeds to the repository and room topic. Presence updates pass through the STOMP join/leave handlers and the in-memory participant service.",
  "This arrangement reduces the need for each page to know database details, but it does not eliminate coupling. The browser and server still depend on compatible JSON property names and destinations. Configuration values must agree on API base URL, SockJS endpoint, port and allowed origin. For example, changing the server port requires updating both the HTTP and messaging URLs used by the browser and the corresponding origin configuration.",
 ],
 "WebSocket and STOMP messaging": [
  "The technology review is qualitative and based on the project's source and official documentation referenced in the report. It compares technologies by role in this implementation rather than asserting a universal ranking. REST is suitable for finite requests such as sign-in and history retrieval. STOMP provides named destinations and subscriptions for room events. SockJS is configured as the browser/server transport library around the /chat endpoint. MongoDB is used for document persistence, while React components update the browser interface as asynchronous data arrives.",
  "For a chat application, message delivery and message retention are different problems. A broker can distribute an event to current subscribers, while an application database can preserve that event for a later history request. The project uses both mechanisms: Spring's simple broker publishes room topics, and RoomRepo saves a changed Room document. This combination is appropriate for demonstrating a full-stack prototype, but it should not be confused with a broker that durably retains events or coordinates multiple backend nodes.",
  "The source does not provide publication counts, a search strategy or a formal bibliometric dataset. The background discussion therefore focuses on concepts that can be connected to the implementation: request/response communication, publish/subscribe routing, document persistence, concurrent in-memory state and component-based rendering. This method avoids unsupported claims about the number of studies or the measured superiority of one framework over another.",
 ],
 "Functional specifications": [
  "The functional requirements are linked to observable operations. Account requirements map to signup and login endpoints. Room requirements map to create and lookup operations. Messaging requirements map to a validated STOMP send and a room-topic broadcast. History requirements map to a paginated REST read. Presence and typing requirements map to separate transient event types. Connection awareness maps to the STOMP hook status and the ConnectionBadge. This traceability makes it possible to locate the implementation for each requirement and to design a focused test.",
  "A requirement should also identify its boundary. For example, the account requirement means that the server can validate credentials and return user fields; it does not mean that every later room operation requires an authenticated token. The participant requirement means that active WebSocket sessions are tracked in one process and distinct names are published; it does not mean that a persistent member directory exists. Precise boundaries make a feature list more useful than broad labels such as secure login or global presence.",
  "Non-functional requirements also affect design choices. Concurrent collections support updates to in-memory participant maps, a two-thousand-character limit bounds one message payload, and a size clamp bounds one history response. These measures do not establish a performance target or a measured capacity. They are implementation constraints that can be verified with tests and later evaluated under a documented workload.",
 ],
 "Technology and environment": [
  "A browser client, REST API and WebSocket connection operate across separate network boundaries. The browser can be refreshed or closed, requests can fail independently, and the server can be restarted while persistent data remains in MongoDB. The design therefore treats connection state as explicit client state and participant state as process-local server state. It does not assume that a browser tab is continuously connected or that the in-memory service survives a backend restart.",
  "The database model is another constraint. A Room document contains a list of embedded Message objects, and the history handler retrieves the Room before selecting a slice in application memory. This keeps the prototype simple, but the history endpoint's page size does not limit the amount of document data that MongoDB must load. As the embedded list grows, write and read costs may increase. A separate message collection is a possible redesign, not a current feature.",
  "Security constraints include the difference between password hashing and authorization. BCrypt protects the stored password representation, and selected inputs are validated. However, the WebSocket sender remains a client-provided display name, and the inspected chat routes do not enforce room membership using an authenticated principal. A production-oriented design would require identity propagation, authorization checks, secure transport and controls for abuse. The current code should be evaluated accurately against that boundary.",
 ],
 "3.3 Design Flow: frontend development": [
  "At runtime, a room interaction begins with a route containing roomId and a display name available from navigation state or local storage. ChatPage starts its history and participant reads and the STOMP hook establishes a client connection. After connection, the client subscribes to message, typing and participant topics and publishes a join event. These operations can complete in different orders, so the page must treat loading, connection and participant state as related but separate signals.",
  "A message then follows a server-mediated path. The composer checks local state and calls the hook. The client publishes a JSON payload to an application destination containing the room identifier. ChatController validates text and sender, resolves the room from the destination, creates the timestamped object, saves the updated room and returns the message. Spring sends that result to the room topic. Each subscribed client parses the frame and passes it to ChatPage for duplicate checking and rendering.",
  "The REST path supplies a complementary snapshot. When the room is opened, the messages endpoint returns a recent page in chronological order within the selected slice. The live subscription supplies later events. The client uses a composite key made from sender, time and a content prefix to reduce duplicates when those sources overlap. Because the key is not a server-generated identifier, it is a mitigation rather than a formal identity guarantee.",
  "Participant and typing events use different data lifecycles. A join registers the session ID in RoomParticipantService and a leave or disconnect removes that mapping. The service publishes a participant snapshot derived from distinct names. Typing is forwarded to a room topic without a database write; the client removes stale indicators on a timer. This flow shows why event type and persistence policy should be documented together.",
 ],
 "Account and room setup": [
  "The frontend and backend divide validation work. The landing page checks room identifier syntax and guest name length before sending a request, giving immediate feedback. RoomController repeats the authoritative room checks, trims the identifier and handles conflict or lookup results. AuthController normalizes email and validates account fields at the server. Message validation occurs in ChatController rather than relying only on the text area's maximum length.",
  "The account path begins with a SignupRequest or LoginRequest and ends with AuthResponse. Signup checks duplicate email, hashes the password with BCrypt and saves a User. Login retrieves the normalized address and verifies the supplied password against the hash. The response contains identity fields but no JWT or durable token. AuthContext stores the returned user data in local storage to support client presentation. These steps do not bind later message senders to an authenticated principal.",
  "The room path creates or looks up a Room by its logical roomId. The database's document identifier and the user-facing room identifier have different roles. The latter appears in route paths and message destinations. New rooms begin with an empty message list. A message send to a room that cannot be found is rejected instead of creating a room implicitly, which keeps room lifecycle separate from conversation posting.",
  "History handling is an algorithmic part of the implementation. The controller clamps the requested size, computes an end index from the total message count and page number, then computes a start index and returns that sublist. Page zero selects the newest segment; page one selects an older segment. The slice is returned in storage order. Since the entire embedded room document is loaded first, this is application-level slicing rather than indexed database pagination.",
 ],
 "Setup and execution": [
  "A reproducible local run uses the configuration in the project rather than relying on generic defaults. The backend properties set port 8081 and the MongoDB URI to localhost on the standard database port with the chatApp database. The frontend Vite environment variables can override the HTTP API base and the SockJS URL. The allowed-origin lists include the documented local development origins. These values need to agree for both HTTP and messaging traffic.",
  "The source repository does not provide a dated work log or a reliable calendar schedule. A useful implementation plan can still be described in dependency order: inspect requirements, define data and API contracts, implement server endpoints and broker configuration, build the client workflow, integrate history and events, then verify boundary cases. This is an engineering sequence inferred from module dependencies, not a claim about when individual tasks were completed.",
  "Validation should use the same dependency order. First confirm that MongoDB is reachable and the backend starts, then verify HTTP operations, then test the STOMP endpoint and room routing, and finally exercise the browser workflow with multiple sessions. If a lower layer is unavailable, higher-layer observations may be misleading. Results should record versions, ports, test data and whether a dependency was mocked or real.",
 ],
 "Report preparation and project evidence": [
  "The implementation evidence consists of source files, package manifests, Maven configuration, application properties and the single context-load test definition. These sources establish technologies and control flow, but they do not establish measured latency, concurrent-user capacity, a completed user study or a public deployment. The report therefore separates code-observed behavior from test plans and recommendations.",
  "The backend test mocks RoomRepo, UserRepo and SimpMessagingTemplate and substitutes a test database URI. Its purpose is to check Spring application-context wiring. It does not call every controller method or assert room and message semantics. The frontend project contains build configuration, but a build alone does not validate the browser's interaction with a live server. Additional evidence would require endpoint, repository, messaging and browser tests.",
  "A result analysis should state what the source demonstrates: a message handler validates, persists and publishes; the room API provides lookup and paginated history; participant sessions are mapped and cleaned up; and the client exposes loading, error and connection states. These are implementation findings. They should not be described as performance results or as proof that every failure case has been tested.",
 ],
 "Message delivery and persistence": [
  "Qualitative outcomes can be organized around each user-visible capability. The account flow supports registration and credential checking; the room flow supports creation and lookup; the conversation flow combines a stored history slice with live room messages; and presence and typing provide temporary activity context. Each capability crosses at least one frontend component and one backend endpoint or event handler, making integration an important part of the observed design.",
  "The central message result is the save-before-broadcast sequence in ChatController. The service resolves the destination room, constructs a server-timestamped Message, appends it to the Room and saves through RoomRepo before Spring publishes the returned object. This ordering aligns the live event with a persistence attempt. It does not by itself prove exactly-once delivery, durable broker retention or recovery from every network interruption.",
  "The main implementation trade-off is simplicity against long-term scale. Embedded messages allow a room and recent history to be handled through one document lookup, but the document grows as messages accumulate. A simple broker and local maps keep the runtime compact, but they are scoped to one process. These outcomes explain why the project is suitable as an academic prototype and identify specific next steps without claiming production readiness.",
 ],
 "Functional validation": [
  "Functional validation should cover both successful and rejected cases. Account tests should verify normalized email, duplicate handling, password hashing and the absence of a password in AuthResponse. Room tests should cover the accepted identifier pattern, duplicate creation, missing lookup and case sensitivity. Message tests should cover blank content, length boundaries, a nonexistent destination room, server timestamp assignment and save-before-broadcast behavior.",
  "Protocol validation should connect more than one session to the same room and a separate session to a different room. Confirm that room topics isolate the event, that join and leave update the participant list and that disconnect cleanup removes stale mappings. Typing events should reach the typing topic but should not be stored as messages. These are proposed execution cases; the project folder does not contain a completed report of their results.",
  "Frontend validation should exercise the route guard, guest identity fallback, history loading, empty and error states, retry action, send disabled state while disconnected and message deduplication when history and live events overlap. It should include delayed responses to expose race conditions. A test result should record the browser and server environment instead of presenting source-level expectations as observed behavior.",
  "Non-functional evaluation can be added through reproducible experiments. A performance test should state the number of rooms and sessions, message size, duration and database placement. A usability review should record tasks and participants. Security validation should check sender impersonation, room authorization, origin policy and TLS in the deployed configuration. None of these outcomes should be claimed until the corresponding test has actually been executed.",
 ],
 "Project contribution and implementation limits": [
  "The project demonstrates integration of a browser interface, HTTP APIs, a broker-based event channel and a document database in one room-oriented workflow. It makes the distinction between finite REST operations and ongoing message delivery visible in the code. It also separates durable room history from transient typing and participant state. These are useful design outcomes for understanding how a small real-time application can be decomposed.",
  "Its limitations are equally important to the result. The room history is embedded and loaded before slicing; presence is process-local; the simple broker is not a distributed durable service; and message identity is inferred on the client. Account password hashing exists, but message identity and room membership are not enforced by an authenticated server principal. These boundaries narrow the claim from a production chat platform to a functional academic prototype.",
  "The strongest next step is to improve identity and authorization before adding features that rely on trust. Once sender identity and room membership are enforced, moderation, private rooms and audit behavior can be designed safely. In parallel, stable message identifiers and database-side pagination can support reconnect recovery and growing history. This ordering follows dependencies in the current architecture rather than a generic feature wish list.",
 ],
 "Scalable message storage": [
  "A staged roadmap should begin with requirements and acceptance cases for authenticated identity, room membership and message ownership. The backend can then issue a signed credential or establish a server session, validate it on REST and STOMP paths, and derive sender identity from the verified principal. Room access checks should apply consistently to history, participant reads and message publication. Tests should include forged names and cross-room access attempts.",
  "The next stage can introduce stable message IDs and a separate message collection if the expected history volume justifies the migration. Define sort order, indexes, retention, cursor or page semantics and compatibility with existing embedded records before changing the schema. A migration should be tested on empty, small and large sample rooms, and the client should merge history and live events using the stable identifier.",
  "A later scaling stage can replace or augment the in-process broker and presence maps when measured usage requires multiple backend instances. A shared event broker, shared or expiring presence store, reconnect synchronization and health metrics must be considered together. Deployment choices should be based on a documented workload and test results rather than assumptions about future demand.",
 ],
 "Automated testing and operations": [
  "Further validation should be added alongside these changes. Unit tests can cover room and message validation; repository tests can cover document mapping and indexes; messaging integration tests can exercise multiple room subscribers; and frontend tests can cover route, history and composer behavior. Each test should state its dependencies and whether a database or broker is real, embedded or mocked.",
  "Operational work includes externalized configuration, TLS, secret management, health checks, structured logs, backup and restore, and a documented retention policy. Accessibility improvements should include keyboard focus, screen-reader labels, contrast and reduced-motion behavior. Rich features such as attachments, search and moderation should be considered only after identity, storage and policy foundations are clear.",
  "The roadmap should use measured evidence to decide priorities. If room documents grow beyond an acceptable size, migrate persistence; if reconnect gaps are observed, design catch-up behavior; if multiple instances are needed, evaluate shared messaging and presence. This evidence-led sequence keeps future work connected to the actual implementation and avoids presenting proposed changes as completed capabilities.",
 ],
}

paragraphs_added = 0
selected_paragraphs = {
 "Real-time delivery and data persistence": 2,
 "1.2. Identification of Problem": 2,
 "1.3. Identification of Tasks": 1,
 "Persistent data and session state": 2,
 "Room and history capabilities": 1,
 "WebSocket and STOMP messaging": 2,
 "Functional specifications": 1,
 "Technology and environment": 1,
 "3.3 Design Flow: frontend development": 2,
 "Account and room setup": 2,
 "Setup and execution": 1,
 "Report preparation and project evidence": 1,
 "Message delivery and persistence": 1,
 "Functional validation": 2,
 "Project contribution and implementation limits": 1,
 "Scalable message storage": 1,
 "Automated testing and operations": 0,
}
for anchor_text, additions in expansions.items():
    anchor = next((p for p in doc.paragraphs if p.text == anchor_text), None)
    if anchor is None:
        raise ValueError(f"Could not find insertion anchor: {anchor_text}")
    for text in additions[:selected_paragraphs[anchor_text]]:
        p = anchor.insert_paragraph_before(text, style="Normal")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.page_break_before = False
        p.paragraph_format.keep_together = False
        p.paragraph_format.keep_with_next = False
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(0, 0, 0)
            run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
        paragraphs_added += 1

# Extend the existing chapter-four evidence table with source-supported planned
# checks. These rows are clearly labeled as planned, not executed results.
for table in doc.tables:
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    if headers == ["Area", "Implemented behavior", "Evidence boundary"]:
        new_rows = [
            ["STOMP routing", "Two sessions in one room and a session in another can verify topic isolation", "Integration test proposed; not reported as run"],
            ["Session cleanup", "Explicit leave and disconnect paths can verify removal from in-memory participant state", "Lifecycle test proposed; not reported as run"],
            ["History paging", "Page zero and subsequent pages can be checked for size and chronological order", "Database-backed test proposed; not reported as run"],
        ]
        for values in new_rows:
            cells = table.add_row().cells
            for cell, value in zip(cells, values):
                cell.text = value
                for para in cell.paragraphs:
                    para.paragraph_format.space_before = Pt(0)
                    para.paragraph_format.space_after = Pt(0)
                    para.paragraph_format.line_spacing = 1.0
                    for run in para.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(12)
                        run.font.color.rgb = RGBColor(0, 0, 0)
                        run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
        print("expanded chapter-four evidence table by", len(new_rows), "rows")
        break

doc.save(PATH)
total_words = sum(len(p.text.split()) for p in doc.paragraphs) + sum(
    len(cell.text.split()) for table in doc.tables for row in table.rows for cell in row.cells
)
print("saved", PATH, "paragraphs added", paragraphs_added, "total words", total_words)
