from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from pathlib import Path

PATH = Path(r"D:\chat App\Multi_User_Chatroom_Application_Report_Asmi_Choudhary_Fixed.docx")
doc = Document(PATH)

appendices = [
("APPENDIX K: WORKED API EXCHANGE EXAMPLES", [
 ("K.1 Registration and login request examples", [
  "A registration request is a JSON object sent with POST /api/v1/auth/signup. Its fields are name, email and password, corresponding to SignupRequest. A representative local example might use a display name such as Mira Das, an email address such as mira@example.test and a development-only password. The example values are illustrative and should not be copied into a live account. The controller trims the name and email, converts the email to lowercase and validates the submitted password before storage.",
  "A successful signup returns HTTP 201 and an AuthResponse containing the saved identifier, name and normalized email. The response is not the User document's password field and should not expose the encoded password. A repeated email returns HTTP 409 with an error field. Invalid name, email or password values return HTTP 400 with an error field. These outcomes provide predictable branches for the landing page and for a future API client.",
  "A login request uses POST /api/v1/auth/login with email and password fields. The controller normalizes the email and checks that both values contain text. An unknown email or a mismatch against the stored BCrypt value returns HTTP 401 with a common invalid-credentials message. A successful login returns HTTP 200 with the same identity response shape as signup. This response does not contain a token or a server-issued session identifier.",
  "When documenting an example, distinguish the request from the result. The endpoint behavior is established by controller code, but a sample response with a particular MongoDB ID or created timestamp would be invented unless an execution trace were captured. For an academic example, show the field names and status code and label any concrete values as illustrative. A test should assert the shape without depending on an arbitrary generated identifier."
 ]),
 ("K.2 Room creation and lookup exchanges", [
  "A room creation request is submitted to POST /api/v1/rooms. The frontend sends JSON containing roomId, such as a development identifier with letters and hyphens. The backend extracts the identifier, trims it and applies a three-to-fifty-character range and an allowlist of letters, digits, underscore and hyphen. The frontend checks a similar pattern before sending, but server validation remains authoritative because requests can originate from outside the supplied interface.",
  "For a valid unused identifier, the controller creates a Room and returns HTTP 201 with the saved room object. If the identifier is already present, it returns HTTP 409. If the input is missing, too short, too long or contains unsupported characters, it returns HTTP 400. A client should treat these statuses as different conditions: a conflict suggests joining an existing room, while malformed input should be corrected before retrying.",
  "Room lookup uses GET /api/v1/rooms/{roomId}. A found room is returned with HTTP 200, and a missing room returns HTTP 404 with an error field. The returned object can contain the embedded message array, so clients should use the dedicated messages endpoint when they need a bounded history slice. The current frontend's join helper checks room existence; the chat page later loads messages and registers the live connection.",
  "The backend accepts more than one content type for creation and has a fallback for plain text, but the supplied React client uses JSON. Supporting multiple forms can be useful for compatibility, yet it expands the parsing cases that need tests. A typed request object would offer a clearer contract and delegate JSON parsing to Spring. If compatibility requires plain text, that behavior should have an explicit test and be documented as a deliberate alternative."
 ]),
 ("K.3 Message history and participant exchanges", [
  "A history request is a GET request to /api/v1/rooms/{roomId}/messages with page and size query parameters. The browser currently requests page zero and size fifty. The server returns a JSON array of Message objects containing sender, content and time. If the room exists but has no messages, the result is an empty array. If the room itself is not found, the result is HTTP 404 rather than an empty history.",
  "The server clamps a requested size to the interval from one to two hundred. Page zero selects the newest slice, and the items inside the slice remain chronological. A later page selects an older slice. Because the source loads the Room document and slices the embedded list in application memory, a successful bounded response should not be described as database-level pagination. The request controls the returned array size, not necessarily the amount of stored data read.",
  "The participant request uses GET /api/v1/rooms/{roomId}/participants and returns a JSON list of distinct usernames currently found in the process-local session maps. A room with no sessions yields an empty list. The endpoint does not return account profiles or a historical list. Since it reads volatile state, the result can change immediately after a join or disconnect event.",
  "A client should handle an empty participant list separately from an unavailable endpoint. The current ChatPage requests history and participants together, with a fallback to an empty participant list if that secondary request fails. This allows the main conversation load to proceed in some partial-failure cases. A future API response could include stronger freshness metadata, but the current interface presents only the current list and count supplied by the service."
 ]),
 ("K.4 Error response handling and client mapping", [
  "RoomApi and AuthApi read the response body as text and attempt JSON parsing. When parsing succeeds and the object contains error, that field becomes the Error message; otherwise, the code falls back to the string body or an HTTP status label. ApiError and AuthError preserve status and parsed data so a component can choose a status-specific response. A fetch TypeError is translated into a local server-connection message.",
  "The landing page uses status-aware handling for the common room cases. A create conflict produces a warning and encourages joining the room. A not-found or bad-request join result becomes a room-not-found prompt. Other errors are sent to the toast system. Registration and login cards can show endpoint validation feedback. These behaviors prevent a raw stack trace from appearing in the interface while still retaining useful response information for debugging.",
  "Error text should not become a substitute for protocol status. An HTTP 409 for a duplicate room is different from a network exception where no response arrived. An HTTP 401 for invalid credentials is different from a backend being unavailable. Keeping those categories separate improves recovery guidance and makes automated tests less dependent on exact prose. Error messages may evolve, whereas status semantics should be stable and documented.",
  "Future error contracts could define a consistent object with code, message and optional field errors. The current controllers use simple maps for many error responses and rely on Spring's default handling for some thrown messaging exceptions. A centralized exception handler could produce consistent JSON for validation, missing records and persistence failures. Any such change would need matching client tests and should preserve the existing useful status distinctions."
 ]),
 ("K.5 API compatibility and contract maintenance", [
  "The /api/v1 prefix communicates an intended version grouping, but no formal schema document or generated client appears in the inspected project. The frontend API helpers contain endpoint paths and request shapes in JavaScript. The Java controller annotations and DTO fields define the corresponding backend contract. These two sources should be reviewed together when changing a route, a field name or a response shape.",
  "A change to MessageRequest affects the frontend publisher, ChatController and potentially integration tests. A change to Message affects the broadcast payload, the history response and MessageBubble. A change to ParticipantEvent affects RoomParticipantService and the participant callback. Listing these cross-layer dependencies before an edit reduces the risk of a change that compiles on one side but leaves the browser reading a missing property.",
  "Compatibility tests can serialize representative DTOs, send requests to controller endpoints and validate JSON properties. For REST, contract cases should include status and body fields. For STOMP, tests should verify destination strings and event payload fields. A build succeeding is not sufficient evidence that two independently developed layers still agree on semantics such as room ID authority or timestamp formatting.",
  "When an API change is not backward compatible, incrementing a version path or supporting a transition period may be appropriate. For this small project, versioning can remain lightweight, but a written decision record should explain whether old clients are supported. The important principle is to treat protocol shape as a user-facing interface with explicit evolution rules rather than as an incidental consequence of Java field names."
 ]),
]),
("APPENDIX L: END-TO-END EVENT TRACE SCENARIOS", [
 ("L.1 First connection to a room", [
  "The first-connection sequence begins after the landing page has verified the room through REST and navigated to /chat/{roomId}. ChatPage resolves the username, initializes loading state and issues history and participant requests. In parallel, its useStompClient hook creates a STOMP client using the SockJS endpoint. The interface shows a connecting state until the connection callback runs.",
  "On connection, the hook subscribes to message, typing and participant topics for the current room. It stores the returned subscription handles for later cleanup. The hook then publishes a join event containing the sender and room identifier. The server receives the room-specific destination, obtains the transport session ID and registers the mapping. ParticipantService broadcasts an event based on the distinct current username list.",
  "The client history response seeds the conversation view and a deduplication Set. The participant response seeds a local list that is merged with the current user's name so the display does not depend solely on an event arriving at exactly the same time. A participant event may then update the count and list. The history and socket operations are asynchronous, so a correct client must tolerate either response arriving first.",
  "An implementation review should inspect the loading indicator, the connection badge, the participant sidebar and the empty-history state during this sequence. The important expected behavior is not that every request completes simultaneously, but that temporary partial states remain understandable. A failed history call should not be presented as a connected empty room. A successful history call with an unavailable participant endpoint should still preserve the message content while indicating only what the interface currently knows."
 ]),
 ("L.2 Successful message exchange", [
  "A sender composes text and submits it while the connection badge indicates readiness. The frontend checks that the content is nonblank and within the text area's configured maximum, then publishes a JSON MessageRequest to the room-specific application destination. The STOMP client uses its active-connection reference to avoid sending through an inactive client. The UI clears or retains the input according to the send handler's state transitions.",
  "The backend validates content and sender, verifies that the room exists and creates the Message with a server timestamp. It appends the message to the embedded room list and calls RoomRepo.save. After the method returns, Spring routes the result to the topic indicated by @SendTo. All subscribed sessions for the room can then receive the serialized Message. The server uses the destination's room ID to locate and route the data.",
  "The recipient parses the frame as JSON and invokes ChatPage's message callback. That callback computes a deduplication key, ignores the message if it has already been observed and otherwise appends it to state. The message list renders the sender, content and time through MessageBubble. A user whose display name matches the sender sees the own-message presentation. The client also considers whether auto-scroll is enabled before adjusting the viewport.",
  "A complete acceptance trace would record the initial room and database state, the submitted text, the backend log or saved document, the topic event and the resulting screen in both clients. No such trace should be claimed unless actually run. The source flow predicts the outcome under normal operation, but a database outage, dropped connection or concurrent retry can produce a different observation. Reproducible verification should capture both the successful path and a deliberate failure path."
 ]),
 ("L.3 Validation rejection and recovery", [
  "A blank message is rejected by server-side StringUtils.hasText even if a modified client bypasses the disabled composer. A message over two thousand characters is rejected. A blank sender is rejected as well. These conditions prevent certain malformed payloads from entering the message list, but they do not establish identity or content moderation. The destination room must also resolve to a Room document before the server appends or broadcasts a message.",
  "At the interface layer, a room identifier that does not match the allowed character rule is caught before the create or join request. A room that passes client validation but fails server validation receives a bad-request response. A duplicate room produces a conflict, while an unknown room produces not found. The landing page maps these outcomes to field messages or toasts instead of assuming that every rejected operation is a network failure.",
  "During history loading, a 404 is treated as evidence that the room cannot be opened and navigation returns to the landing page. Other history failures remain on the chat route with an error state and retry control. A participant-list failure is caught independently and replaced with an empty participant list. This is a deliberate partial-degradation behavior, but it can make the UI's presence view temporarily incomplete.",
  "Failure recovery should avoid losing user input unexpectedly. A future usability test should check what happens to unsent text when a connection drops, whether retry repeats a message, whether the user receives enough information to decide what to do and whether the app avoids announcing success before the backend confirms persistence. The current report does not claim durable offline queuing, automatic retry guarantees or exactly-once delivery."
 ]),
 ("L.4 Leave and unexpected disconnect", [
  "An explicit leave begins when the user selects the leave control. The client attempts to publish a leave event for the current room and username, cleans up local subscriptions and deactivates the STOMP client. The backend uses the session ID to remove the associated room and name mapping, removes the session from the room set and broadcasts a participant event when a known mapping existed. The interface then returns to the landing workflow.",
  "A browser close or transport loss may bypass the explicit leave action. Spring emits a SessionDisconnectEvent, and WebSocketEventListener wraps the event message to retrieve the session ID. The listener calls the same participant removal service. This ensures a normal disconnect path can clear a stale map entry, although timing and duplicate lifecycle events should still be covered by tests.",
  "The service removes a room set when its final session is removed. It also avoids broadcasting when its internal removeParticipant call is used as part of moving the same session to another room. The broadcast payload contains a current distinct user list and count. This count can be smaller than the number of sessions when one person uses the same display name in multiple tabs, because the published list is de-duplicated by username.",
  "A reliable lifecycle test should cover explicit leave, unexpected disconnect, double cleanup and the last session leaving a room. It should also verify that removal in one room does not affect another session's membership. Because the service is in-memory, a process crash loses the whole map without publishing a leave event. On restart, connected clients need a reconnect and join sequence to repopulate the state."
 ]),
 ("L.5 History/live overlap and reconnect considerations", [
  "The client obtains history through HTTP and live events through STOMP. These channels can overlap: a message may be stored before the history query completes and also arrive through a topic subscription. If the event arrives first, the key enters the seen set before the history response is applied; if history arrives first, the later event should be filtered. The current code initializes seen keys from history and checks the message array before appending a live item.",
  "A possible edge case occurs if history state is replaced after a live event has already updated the message list. The actual effect ordering and React state updates should be tested under controlled delays rather than assumed. A robust reconciliation method can merge both sources by stable message ID and sort by a documented server order. The current composite key is a useful prototype heuristic, but it cannot resolve every collision or ordering ambiguity.",
  "On reconnect, the hook's connection callback can establish subscriptions and send a join notice, while the page may need to refresh history and participants. The inspected code should be evaluated for actual automatic reconnect behavior and state reset behavior before claiming a complete recovery feature. If the library retries transparently, the app still needs to decide how to reconcile events missed during the outage.",
  "A future reconnect contract could include a last-seen message ID, a bounded history refresh and idempotent event merging. It could also make connection health, retry delay and terminal failure visible. Such behavior should be designed around the project's current event schema and storage model. No reconnect protocol or message offset is represented in the existing DTOs, so this remains a design recommendation."
 ]),
]),
("APPENDIX M: DETAILED TEST CASE CATALOG", [
 ("M.1 Account and identity cases", [
  "Case M-ACC-01 should submit a valid signup with a name, mixed-case email and a password meeting the configured minimum. Verify HTTP 201, a normalized lowercase email in the response, an identifier and name, and the absence of a password field. Verify the repository receives a User with a BCrypt-formatted password value rather than the literal submitted password. Record the database and test setup so the result is repeatable.",
  "Case M-ACC-02 should vary the display name across blank, one-character, exactly two-character, fifty-character and fifty-one-character values. Confirm the server's lower and upper boundaries and capture the HTTP status and error field. Test leading and trailing spaces to confirm that the server trims before measuring length. A corresponding frontend test should document the guest form's separate maximum of thirty characters.",
  "Case M-ACC-03 should exercise malformed email values, missing email, leading and trailing whitespace, uppercase characters and duplicate normalized addresses. A mixed-case duplicate should still conflict after normalization. If two simultaneous requests attempt the same address, the database unique index should be the final guard; test and document the observed exception mapping rather than assuming the pre-check is race-proof.",
  "Case M-ACC-04 should log in with a correct password, incorrect password, unknown email and blank field. Confirm successful login returns only identity fields and that the two credential failures do not reveal which part was wrong. Separately verify that the client restores local identity after refresh and clears the local keys on logout. Do not treat local-storage restoration as proof that the server authenticated a later chat request."
 ]),
 ("M.2 Room and history cases", [
  "Case M-ROOM-01 should create a valid unused room identifier and verify HTTP 201 plus the persisted roomId. Repeat with identifiers at length three and length fifty. Case M-ROOM-02 should test blank values, lengths below three and above fifty, spaces, punctuation, non-ASCII characters and JSON with a missing roomId field. Confirm the error status and that no invalid Room document is saved.",
  "Case M-ROOM-03 should attempt to create an identifier that already exists and verify HTTP 409. Case M-ROOM-04 should query a valid room and an unknown room, verifying HTTP 200 and HTTP 404 respectively. Test exact case differences because repository string matching does not imply case-insensitive room lookup. Include JSON and plain-text creation bodies if both formats are intended to remain supported.",
  "Case M-HIST-01 should test empty history and return an empty array. Case M-HIST-02 should create fewer than fifty messages and verify page zero returns them chronologically. Case M-HIST-03 should create more than one page, verify that page zero returns the most recent segment and page one returns the next older segment, with the expected chronological order inside each response.",
  "Case M-HIST-04 should test page boundaries and size clamping, including a requested size of zero, a negative size and a value above two hundred. Verify that the endpoint clamps rather than returning an invalid slice. A page beyond available history should return an empty array. Repeat with a large embedded history to measure current document retrieval cost without assuming the in-memory slice is a database-side pagination query."
 ]),
 ("M.3 Messaging and event cases", [
  "Case M-MSG-01 should submit a valid message to an existing room and verify that content and sender are trimmed, a server timestamp is assigned, the room document is saved and the event is published to the matching room topic. The request's roomId should intentionally differ from the path variable to verify that the destination is used for lookup. This case is about route consistency, not user authorization.",
  "Case M-MSG-02 should reject content that is blank, contains only spaces, exceeds two thousand characters or has a blank sender. Verify that rejected input does not modify the room history. Case M-MSG-03 should send to a missing room and verify that the operation does not create a new room implicitly. Capture the broker-visible result and any error frame behavior if the test client waits for a response.",
  "Case M-EVT-01 should connect two sessions to one room and one session to another room. Publish a message and verify delivery to both subscribers in the first room and no delivery to the other room. Case M-EVT-02 should send a typing-start event and verify room ID normalization, topic routing and absence of a MongoDB write. Follow with a typing-stop event and confirm the client removes the indicator.",
  "Case M-EVT-03 should verify deduplication when an identical message is observed through history and a live callback. Case M-EVT-04 should use two different messages with the same sender, timestamp and first forty content characters to expose the limitation of the current composite key. This is a characterization test; if a stable ID is introduced, update the test to assert correct unique rendering by that ID."
 ]),
 ("M.4 Participant lifecycle and concurrency cases", [
  "Case M-PRES-01 should add one session and verify the published participant event contains a count of one and the expected username. Add a second distinct session under a different name and verify the sorted distinct list. Add another session with the same name and verify how the event count differs from the raw session count. Assertions should match the current user-list-derived count rather than an assumed unique-account identity.",
  "Case M-PRES-02 should remove one participant explicitly and verify that remaining users stay listed. Remove the final session and verify the room's session set is discarded and its list becomes empty. Repeat removal for the same session to characterize idempotence. Move a session to another room and verify the old room update and new room registration follow the service's no-broadcast-then-add path.",
  "Case M-PRES-03 should trigger SessionDisconnectEvent and verify cleanup without a client leave message. Case M-PRES-04 should race an explicit leave against a disconnect callback and confirm that duplicate cleanup does not create an exception or a negative count. ConcurrentMap and concurrent sets protect individual data structures, but tests should watch cross-map invariants under simultaneous operations.",
  "Case M-PRES-05 should connect and disconnect participants rapidly across several rooms. Record stale membership observations and event ordering. A single-process test can characterize the current implementation, while a multi-instance test should be marked not applicable until shared session state and a distributed broker are added. Do not infer cluster safety from the use of concurrent collections."
 ]),
 ("M.5 Browser workflow and evidence record", [
  "Case M-UI-01 should open the landing route, switch between create and join modes, validate guest fields and verify that a valid operation navigates to the room route. Case M-UI-02 should simulate duplicate room, unknown room, server unavailable and malformed input outcomes. Confirm that field messages and toasts are understandable and that loading state clears after both success and failure.",
  "Case M-UI-03 should mount ChatPage with valid route state, with only a stored username, and with neither source available. Verify correct behavior for each condition. Exercise the loading, empty, populated and error states. Verify 404 navigation, retry behavior and participant endpoint failure handling. These cases cover the supported interface branches without assuming a persistent login token exists.",
  "Case M-UI-04 should verify composer keyboard semantics, send-button disabled state, input length, error feedback and scroll behavior. Case M-UI-05 should inspect narrow and wide viewport layouts, sidebar control, focus order and accessible names. A manual checklist should state browser version, viewport, operating system, exact navigation sequence, expected behavior and observed behavior.",
  "For every executed case, store a concise evidence record containing test identifier, build revision, environment, preconditions, input, expected outcome, observed outcome, pass/fail status and any defect reference. Attach logs or screenshots only when they show an actual test run. The cases in this appendix are proposed checks and are not a claim that all of them have already passed."
 ]),
]),
("APPENDIX N: SOURCE-TO-BEHAVIOR MAINTENANCE GUIDE", [
 ("N.1 Changing room validation safely", [
  "Room identifier behavior appears in both LandingPage validation and RoomController.createRoom. The frontend pattern currently permits letters, digits, hyphens and underscores and enforces a minimum length. The backend trims and validates the final request with its own length and character rules. A requirement change should update both layers, associated help text and tests so the browser does not reject values the backend accepts or promise values the backend rejects.",
  "The room controller's extractRoomId method supports JSON property names roomId and room_id through manual string search and also strips quotation marks from a plain body. This implementation is compact but has edge cases around escaped quotes and malformed nested JSON. Changing the accepted room format is an opportunity to move toward a DTO with Bean Validation, while preserving a compatibility path only if an actual client depends on the plain-text form.",
  "Room uniqueness is currently checked by a repository lookup before saving. Under concurrent create requests, two requests could both pass the lookup before either save completes unless storage also prevents duplicates. A unique index on logical roomId would enforce the rule at the database boundary. If added, the duplicate-key exception should be translated to the same conflict status so callers retain a stable contract.",
  "After a validation change, verify the landing page error text, backend response status, saved value normalization and join lookup behavior. A unit test for the predicate is not enough if routing and persistence also depend on the normalized identifier. Document whether room IDs are case-sensitive and whether normalization occurs; current code trims but does not lowercase room IDs."
 ]),
 ("N.2 Changing the message model", [
  "The current Message object has sender, content and LocalDateTime time. It is embedded in Room.messages, is returned by history and is broadcast by the STOMP handler. Adding a field therefore affects Java serialization, existing MongoDB records, frontend message rendering, deduplication and any example payloads. Before adding fields, decide whether older documents can omit the field and what default behavior the client should use.",
  "A server-generated message ID would provide a stable identity for React keys and duplicate detection. It could also support edit or delete operations later, although those actions require authorization and audit decisions. Introduce the ID in a backward-compatible way, make the client tolerate old records without it during migration and replace the composite key only after both persisted and live paths carry the new field.",
  "A timezone-aware timestamp is another possible evolution. LocalDateTime has no timezone offset and can be ambiguous when clients interpret it outside the server's local context. An Instant or offset-aware representation with a documented serialization format would improve cross-region interoperability. Existing data migration and sorting logic should be considered before changing the Java type.",
  "Moving messages to their own collection changes persistence semantics. The controller would no longer load, mutate and save the entire room to append one item. A repository query would need to select by room ID, sort by timestamp or sequence, and page from the database. This change should include indexes, retention policy, transaction or ordering decisions and migration tests rather than only a modified entity class."
 ]),
 ("N.3 Changing the participant event contract", [
  "ParticipantEvent is broadcast by RoomParticipantService and consumed by ChatPage. Its fields are roomId, count, type, username and users. The client uses count when present and prefers a nonempty full users list; otherwise, it applies a JOIN or LEAVE event to its local list. A contract change must coordinate the producer and consumer, including the behavior when users is intentionally empty.",
  "The current count comes from the distinct usernames list included in the event, whereas RoomParticipantService also exposes getCount based on the session set. These values can differ when multiple sessions use the same name. A future contract should decide whether count means sessions, accounts or distinct display names and use that definition consistently in the service, REST endpoint and interface.",
  "If account identities become trusted, a participant event should use a stable user identifier internally and a display name for presentation. Names are mutable and not unique. A browser may also intentionally connect more than once. Separating connection count from distinct member count makes the interface's semantics clearer and can support a separate active-session indicator if needed.",
  "Tests should assert both the event payload and client reconciliation. Verify join, leave, duplicate display name, empty room, disconnect and stale event behavior. Versioning may be warranted if a new payload shape is introduced while clients can be cached. During transition, the backend can publish a compatible shape or the client can accept both forms, provided the compatibility logic is covered and later removed deliberately."
 ]),
 ("N.4 Adding an API route or user-interface feature", [
  "A new REST feature should be represented across a controller mapping, a request or response DTO where appropriate, a service or repository operation, a frontend API helper and a UI state transition. Define validation, success status, error status, authorization assumptions and persistence effects before coding. A route should not be added only to make a button appear functional; its server behavior and client failure path are part of the feature.",
  "A new real-time event should define its destination, payload schema, sender, recipient scope, persistence policy and reconnect behavior. Add a controller handler, a topic publication path and a frontend subscription callback. Ensure the event is distinct from persisted messages if it is ephemeral. Test that a room subscriber receives it and that an unrelated room does not.",
  "A new reusable UI component should be evaluated for props, empty state, loading state, error feedback, keyboard behavior and CSS scope. Keep shared concerns such as API calls, authentication context, toasts and WebSocket subscriptions in their existing modules unless a refactor has a clear benefit. Include a browser test for the complete user journey, not just a component snapshot.",
  "The change record should identify altered files, user-visible behavior, new configuration, database effects and verification evidence. Update README instructions only after checking them against application.properties and package.json. This source-to-behavior map makes maintenance more reliable than editing the nearest screen while overlooking the server, transport or data model dependencies."
 ]),
 ("N.5 Review and release checklist", [
  "A code review should trace the complete data path and check untrusted inputs at the backend boundary. For account work, inspect normalization, password handling and authorization consequences. For room work, inspect identifier validation and uniqueness. For message work, inspect sender authority, content bounds, persistence-before-broadcast semantics, event destinations and client deduplication.",
  "A release candidate should be built from a known source revision with the Java and Node toolchains recorded. The backend test command and frontend build should be run, and any manual browser test should have a saved evidence record. Configuration should be checked for correct API base URL, WebSocket endpoint, server port, allowed origin and database URI. Secrets should not be committed in environment files.",
  "A deployment review should ask whether TLS is enabled, whether a real identity is enforced, whether rooms are private or public, whether rate limits exist, where logs are stored, how backups are restored and what happens when MongoDB is unavailable. These are gate questions for production deployment; they are not claims that the prototype currently implements those controls.",
  "After release, monitor connection failures, database exceptions and message processing errors. Keep a rollback path and a way to compare the deployed configuration with the tested configuration. The current repository does not include an operational monitoring system, so any such process would need to be designed and documented before a public deployment is described as production-ready."
 ]),
]),
("APPENDIX O: USABILITY AND ACCESSIBILITY EVALUATION GUIDE", [
 ("O.1 Labels, keyboard use and focus", [
  "The landing page uses labels associated with input identifiers and displays validation messages near relevant fields. Evaluation should confirm that a screen reader announces the field label, its error state and the error text when the user moves focus. The auth card, room field and display-name field should expose clear labels rather than relying only on placeholders. Placeholder text can disappear during typing and is not a substitute for a persistent label.",
  "The chat composer provides an explicit button label for sending and uses a keyboard convention where Enter sends while Shift+Enter adds a line break. This convention should be verified with keyboard-only use and communicated to assistive technology users. Ensure that keyboard focus remains visible, that disabled state is conveyed and that the send action can be triggered without a pointer.",
  "The sidebar menu and close controls should have meaningful accessible names and a predictable focus sequence. Opening the sidebar should not strand focus behind an overlay, and closing it should return focus to the control that opened it. The leave-room control is an important navigation action and should be distinguishable from merely closing the sidebar.",
  "Testing should use both automated accessibility checks and manual assistive technology review. Automated checks can identify missing labels and some contrast issues, but cannot determine whether a dynamic participant update is announced helpfully or whether the conversation reading order is sensible. Record the browser, screen reader and interaction sequence used for any accessibility claim."
 ]),
 ("O.2 Dynamic updates and status communication", [
  "The connection badge changes as the STOMP client connects, disconnects or encounters an error. A visual-only color cue may not convey the state to a person with color-vision differences or to a screen reader. The label should include readable text or an accessible status role. Evaluate whether frequent reconnect changes are announced once, without overwhelming a user with repetitive messages.",
  "The participant count and list can change as join and leave events arrive. The interface should communicate the updated information without shifting keyboard focus. A polite live region can announce meaningful changes, while a full list update may be too verbose. The desired behavior should be established with user testing rather than inferred from the presence of a React state update.",
  "Typing indicators are transient and may change repeatedly. Their accessibility behavior should avoid announcing each keystroke or flapping state. The existing hook throttles sender events and the client expires stale indicators after a timeout, which offers a starting point for a restrained announcement policy. If the indicator is decorative for assistive technology, that choice should be deliberate and documented.",
  "Loading, empty and error states should each have clear text and appropriate semantics. A retry button should be reachable and labeled. If history loading completes while focus is in another control, content should not unexpectedly steal focus. Validation errors should remain associated with their inputs, and toast notifications should be announced in a way that does not interrupt composing a message."
 ]),
 ("O.3 Readability, responsive layout and motion", [
  "Message bubbles should remain readable at browser zoom and narrow viewport widths. Evaluate long URLs, long words, multiple lines and messages near the maximum length. Text should wrap without widening the page or hiding the sender and timestamp context. The collapsible sidebar should preserve access to the participant list and connection state on small screens.",
  "The interface uses icons from Lucide React and decorative assets in the landing-page preview. Icons that communicate actions need accessible labels, while purely decorative graphics should be hidden from assistive technology. The chat preview on the landing page should not be mistaken for live content. Visual separation can help users understand the transition from demonstration preview to active room conversation.",
  "Typing dots and other transitions may involve motion. Users who prefer reduced motion should not be forced to view continuous animation. CSS should be checked for reduced-motion preferences and for transitions that do not delay an important state change. The interface's information should remain available when animation is disabled.",
  "Responsive evaluation should include both portrait and landscape layouts, browser zoom and virtual keyboard behavior on a mobile device. The composer must remain visible when the soft keyboard opens, and scroll-to-bottom behavior should not conceal the last message behind the composer. A screenshot at one desktop size is not sufficient evidence of responsive behavior across devices."
 ]),
 ("O.4 Usability study protocol", [
  "A small usability study could ask participants to create a room, invite a second browser session, exchange a message, locate a previous message and leave the room. Participants should receive neutral task instructions and should not be coached through hidden interface steps. The study should record task completion, observed confusion and participant feedback without capturing passwords or unnecessary personal data.",
  "Study metrics might include completion, time to task, input corrections, help requests and perceived clarity. These should be reported with the number and characteristics of participants and the test environment. A small formative study can identify obvious friction but should not be presented as statistically representative or as proof of broad usability.",
  "Privacy safeguards should include consent, a clear explanation of recorded observations and a retention plan for notes or recordings. Account creation can be tested with mock or disposable credentials where possible. If real messages are used, participants should know that the application stores messages in MongoDB and that the prototype does not claim production-grade access control.",
  "Findings should lead to traceable improvements. Each observation can be connected to a proposed change, a responsible component and a follow-up verification case. For example, confusion about a missing room can lead to revised error text in LandingPage and a regression test for the not-found response. No study outcomes are asserted in this report because no participant study evidence was supplied."
 ]),
 ("O.5 Content moderation and respectful communication", [
  "The current chat prototype provides room-based text exchange but does not implement reporting, blocking, moderation or administrator controls. If the application is opened to a wider audience, the project owner should decide how users can respond to abusive content and who may remove messages or participants. These policy decisions affect both the backend authorization model and the interface.",
  "A moderation design should distinguish a room-level removal action from deleting a user's account and from hiding content locally. It should record which identity performed an action, what target was affected, when it occurred and whether an appeal or reversal is possible. Such an audit trail should be protected from ordinary message authors and should have a defined retention period.",
  "Rate limiting and spam controls are relevant even for a small service because message endpoints can be flooded. A server should enforce limits independently of the browser composer. Content filtering alone is not a complete moderation strategy; human reporting and escalation routes may be necessary depending on deployment context.",
  "Any future moderation feature should be accompanied by user-facing policy language and tested for both ordinary and adversarial cases. The current report treats moderation as future work and does not claim that messages are screened, encrypted, deleted on request or governed by a completed community policy."
 ]),
]),
]

anchor = next(p for p in doc.paragraphs if p.text == "REFERENCES")
for appendix_title, topics in appendices:
    p = anchor.insert_paragraph_before(appendix_title, style="Heading 1")
    for run in p.runs:
        run.font.name = "Times New Roman"; run.font.color.rgb = RGBColor(0, 0, 0)
        run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
    for subheading, paragraphs in topics:
        hp = anchor.insert_paragraph_before(subheading, style="Heading 2")
        for run in hp.runs:
            run.font.name = "Times New Roman"; run.font.color.rgb = RGBColor(0, 0, 0)
            run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")
        for content in paragraphs:
            bp = anchor.insert_paragraph_before(content, style="Normal")
            bp.paragraph_format.page_break_before = False
            bp.paragraph_format.keep_together = False
            bp.paragraph_format.keep_with_next = False
            for run in bp.runs:
                run.font.name = "Times New Roman"; run.font.size = Pt(12); run.font.color.rgb = RGBColor(0, 0, 0)
                run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")

# Rebuild appendix entries in the contents pages in alphabetical order.
for p in list(doc.paragraphs):
    if p.text.startswith("APPENDIX ") and " . " in p.text:
        p._element.getparent().remove(p._element)
refs_entry = next(p for p in doc.paragraphs if p.text.startswith("REFERENCES ."))
appendix_titles = [title for title, _ in appendices]
# Existing A-J entries have reversed order from the first insertion; remove them
# and rebuild all fifteen entries between the Chapter 5 and References rows.
for p in list(doc.paragraphs):
    if p.text.startswith("APPENDIX ") and " . " in p.text:
        p._element.getparent().remove(p._element)
all_titles = [
 "APPENDIX A: SOURCE CODE AND MODULE INVENTORY",
 "APPENDIX B: HTTP API CONTRACT AND RESPONSE BEHAVIOR",
 "APPENDIX C: REAL-TIME PROTOCOL AND EVENT LIFECYCLE",
 "APPENDIX D: DATA MODEL AND PERSISTENCE REFERENCE",
 "APPENDIX E: USER INTERACTION AND CLIENT STATE REFERENCE",
 "APPENDIX F: VERIFICATION MATRIX AND TEST DESIGN",
 "APPENDIX G: LOCAL CONFIGURATION AND REPRODUCIBLE EXECUTION",
 "APPENDIX H: RELIABILITY, SECURITY AND SCALING REVIEW",
 "APPENDIX I: MAINTAINABILITY AND EXTENSION DESIGN",
 "APPENDIX J: REQUIREMENTS TRACEABILITY AND TECHNICAL GLOSSARY",
] + appendix_titles
for title in all_titles:
    p = refs_entry.insert_paragraph_before()
    p.style = refs_entry.style
    p.paragraph_format.space_after = Pt(0)
    for value in (title, " . " * 4, "30"):
        run = p.add_run(value)
        run.font.name = "Times New Roman"; run.font.size = Pt(12); run.font.color.rgb = RGBColor(0, 0, 0)
        run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")

# Add a compact appendix outline to the detailed contents page.
figure_entry = next(p for p in doc.paragraphs if p.text.startswith("Fig 1  "))
detail_titles = [title.replace("APPENDIX ", "Appendix ") for title in all_titles]
for title in detail_titles:
    item = figure_entry.insert_paragraph_before()
    item.paragraph_format.space_after = Pt(0)
    item.add_run("Appendix " + title)
    item.add_run(" . " * 4)
    item.add_run("30")
    for run in item.runs:
        run.font.name = "Times New Roman"; run.font.size = Pt(12); run.font.color.rgb = RGBColor(0, 0, 0)
        run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")

doc.save(PATH)
added = sum(len(paragraphs) for _, topics in appendices for _, paragraphs in topics)
words = sum(len(p.text.split()) for p in doc.paragraphs) + sum(
    len(cell.text.split()) for table in doc.tables for row in table.rows for cell in row.cells
)
print("saved", PATH, "new appendices", len(appendices), "paragraphs", added, "total words", words)
