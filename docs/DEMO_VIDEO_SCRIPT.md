# PitStop AI — Official Submission & Video Presentation Guide 🚀

**Submission Recipient**: `kidus@brain3.ai`  
**Subject Line**: `PitStop AI Submission - Hiruy Mengistu - AI SWE Evaluation`  
**Author**: Hiruy Mengistu  

This guide directly addresses the **5 evaluation requirements** from Brain3.ai:
1. **Explain the problem statement and your thought process**
2. **Walk through your problem-solving approach and solution design**
3. **Demonstrate the AI agent in action via the UI**
4. **Provide a high-level code walkthrough of both frontend and backend**
5. **Clean source code and documentation package**

---

## 🎬 Part A: Word-for-Word Video Recording Script

**Target Duration**: 7 – 9 Minutes  
**Structure**: Follows the 4 video sections required by Brain3.ai.

---

### SECTION 1: Problem Statement & Thought Process (0:00 – 1:30)

**[Screen Visual]**: Start with camera on yourself or on the PitStop AI Dashboard landing page.

> **Voiceover / Presentation**:  
> *"Hello Kidus and the Brain3.ai team. I'm Hiruy Mengistu, and this is my submission for PitStop AI—an AI-powered operations platform for independent automotive workshops.*  
>  
> *When approaching this assignment, I analyzed how independent automotive workshops actually run. They don't need a novelty chatbot that invents car advice. Independent shops operate in high-friction, two-sided environments where:*  
> *1. Customer requests come in as unstructured, panicked descriptions—often leaving out key vehicle details and urgency.*  
> *2. Scheduling is complex: you can't just book any slot; you have to match technician certifications—like brake or engine skills—with specialized bays, such as heavy hydraulic lifts.*  
> *3. Estimates and parts orders carry real financial and legal liability.*  
> *4. Vehicle owners are left in the dark about repair progress, causing dozens of phone interruptions, delayed quote approvals, and lost revenue.*  
>  
> *My thought process was built on a foundational engineering principle:*  
> ***The AI model must be an orchestration and language-understanding layer, never the unconstrained source of truth for business state, pricing, or schedules.***  
> *We leverage Gemini for natural language extraction and conversational triage, while deterministic backend services enforce business rules, idempotency, human-in-the-loop governance, and event-driven email notifications for both workshop staff and vehicle owners."*

---

### SECTION 2: Solution Design & Problem-Solving Approach (1:30 – 3:00)

**[Screen Visual]**: Switch to the Architecture Diagram in `README.md` or a slide.

> **Voiceover / Presentation**:  
> *"Let's examine how this philosophy translated into our solution design.*  
>  
> *We implemented a full-stack, modular architecture serving two core user roles:*  
> - ***Frontend***: Next.js 14 App Router, TypeScript, and Tailwind CSS. We designed a sleek, high-visibility dark mode interface with glassmorphism featuring a dual-mode toggle between **[Workshop Staff Hub]** and the **[Vehicle Owner Garage Portal]**, plus a live interactive **Email Outbox**.  
> - ***Backend API***: Python 3.12+ with FastAPI and Pydantic v2. FastAPI gives us high-performance asynchronous endpoints, strict validation contracts, and automated OpenAPI documentation.  
> - ***Persistence Layer***: SQLAlchemy 2.0 with PostgreSQL 16 for production and SQLite with Write-Ahead Logging (WAL) for instant, zero-friction local developer testing.  
> - ***AI Orchestration***: A hybrid intake engine. When an API key is present, it invokes Google Gemini with structured JSON output schemas. When offline or during integration timeouts, it seamlessly falls back to a deterministic rule-based NLP engine.  
>  
> *Key Architectural Decisions:*  
> *1. **Safety Triage Guardrails (FR-04)**: If symptoms indicate brake loss, steering failure, or smoke, the system automatically flags `safety_escalation=True` and issues cautious guidance without attempting autonomous mechanical diagnosis.*  
> *2. **Deterministic Scheduling Engine (FR-06)**: Slot calculations are purely mathematical. They evaluate mechanic certifications, bay lift capabilities, and business operating hours.*  
> *3. **Idempotency Protection (FR-07)**: Every booking requires an idempotency key to prevent accidental duplicate bookings on client retries.*  
> *4. **Human-in-the-Loop Governance (FR-10)**: Generated estimates remain strictly in `draft` status until explicitly authorized by a certified service advisor or the vehicle owner.*  
> *5. **Passwordless Email OTP & Notification Engine**: Vehicle owners log in securely via 6-digit email OTP codes, while automated event-driven triggers dispatch responsive HTML transactional emails for confirmations, estimate ready notices, and vehicle pickup alerts."*

---

### SECTION 3: Live Demonstration of AI Agent & UI Workflows (3:00 – 6:00)

**[Screen Visual]**: Switch to browser at `http://localhost:3000`.

#### Step 1: AI Intake & Safety Guardrails
> **Voiceover / Presentation**:  
> *"Now let's see the system in action.*  
> *Under Tab 1: AI Intake & Triage, we'll run the primary scenario from our approved SRS. A customer, Alex Mercer, reports: 'My 2021 Toyota Camry has a severe grinding noise when applying the brakes, and the pedal felt unusually spongy on the highway today.'*  
> *I click **Run AI Agent Extraction**.*  
>  
> *(Point to right panel)*  
> *Notice three immediate outcomes:*  
> - *The vehicle is extracted as a 2021 Toyota Camry, categorized into `brake_service` with a 90-minute estimated duration.*  
> - *Notice the prominent red alert: **SAFETY-CRITICAL ESCALATION TRIGGERED**. Because brakes are a life-safety system, our guardrails advise the customer against driving at highway speeds and route the case directly for certified mechanic inspection.*  
> - *The AI also identifies missing context and generates a targeted follow-up question regarding pedal travel.*  
>  
> *I click **Persist Draft Request**, submit the clarification answer, and click **Approve & Convert to Work Order**."*

#### Step 2: Work Orders & Human-in-the-Loop Estimates
> **Voiceover / Presentation**:  
> *"Now we are in Tab 2: Work Orders. Here is Work Order #2 in `pending_approval`.*  
> *The technician can add physical inspection notes.*  
> *Next, I click **Calculate Draft Estimate**. The backend retrieves real parts from our inventory catalog—ceramic brake pads and DOT4 brake fluid—and calculates labor using our shop’s configured $95/hr labor rate.*  
> *Notice it is saved as **DRAFT**. The system will never automatically charge the customer. It requires authorized human sign-off."*

#### Step 3: Deterministic Scheduling & Rescheduling
> **Voiceover / Presentation**:  
> *"In Tab 3: Bay Scheduling, I query feasible certified slots for today.*  
> *The engine only offers slots where a certified brake mechanic (Marcus Vance) and a heavy hydraulic lift bay (Bay 1) are simultaneously free.*  
> *I select the 09:30 AM slot and click **Confirm Slot**.*  
> *The appointment is committed and synchronized with Google Calendar.*  
> *If the customer needs to reschedule to 2:00 PM, clicking the new slot reschedules the appointment cleanly without database collision errors."*

#### Step 4: External Resilience & 503 Failure Recovery
> **Voiceover / Presentation**:  
> *"In the appointments table below, we demonstrate resilience (FR-15).*  
> *If an external calendar API fails, I click **Trigger 503 Failure**. The appointment reflects the `FAILED` state, logs an IntegrationEvent, and queues an automated retry job.*  
> *When the external service recovers, clicking **Sync OK** restores synchronization to `SYNCED` and generates a persistent calendar event ID.*  
>  
> *Under Tab 5, we can also see live weather context retrieved from the **Open-Meteo API**, which generates advisories for weather-sensitive detailing or post-repair road testing."*

#### Step 5: Vehicle Owner Garage Portal & Passwordless Email OTP
> **Voiceover / Presentation**:  
> *(Click the mode toggle in the top navbar: **[🚗 Vehicle Owner Garage]**)*  
> *"Now, let's look at the customer side of PitStop AI.*  
> *Vehicle owners don't want complex passwords. They want passwordless email access.*  
> *I enter Alex Mercer's email `alex.mercer@example.com` and click **Send Verification Code**.*  
> *A 6-digit OTP code is generated, cryptographically signed with a 15-minute expiry, and logged into the outbox.*  
> *I enter the code and click **Verify & Enter Garage**.*  
>  
> *(Show Alex Mercer's Garage)*  
> *Instantly, Alex sees his registered 2021 Toyota Camry with mileage counters and recommended maintenance intervals."*

#### Step 6: 5-Stage Live Service Tracker & 1-Click Digital Estimate Authorization
> **Voiceover / Presentation**:  
> *"Right below, Alex has a real-time **Live Vehicle Service & Repair Tracker** displaying a 5-stage progress stepper: Intake Logged, Bay Inspection, Estimate Ready, In Repair, and Ready for Pickup.*  
> *Notice the quote card: Alex sees the itemized brake pad replacement and labor breakdown totaling $352.50.*  
> *Alex clicks **Digitally Authorize & Start Work**.*  
> *The estimate instantly updates to `approved` in the database, the repair stage advances, and an email confirmation is sent to both the shop and customer."*

#### Step 7: Live Transactional Email Outbox
> **Voiceover / Presentation**:  
> *(Click the **Email Outbox** button with the live badge in the top bar)*  
> *"Finally, we built a live interactive **Email Outbox** into the UI so evaluators can inspect every transactional message dispatched by the engine.*  
> *Here you can see the OTP verification code, the Appointment Confirmation with Google Calendar details, the Estimate Ready notice, and the Vehicle Ready for Pickup alert—all rendered with responsive, branded HTML templates."*

---

### SECTION 4: High-Level Code Walkthrough (6:00 – 8:00)

**[Screen Visual]**: Switch to VS Code / IDE showing project file tree.

> **Voiceover / Presentation**:  
> *"Now, let's walk through the codebase.*  
>  
> *1. **Backend AI Intake Engine** (`backend/app/services/ai_intake_service.py`):*  
> *(Show file on screen)*  
> *Here you see `extract_service_request_agent()`. It issues structured tool extraction prompts to Google Gemini. If Gemini is unreachable or offline, it falls back to `heuristic_extraction()`. Notice our `SAFETY_CRITICAL_KEYWORDS` list that triggers our safety escalation logic and cautious customer advisories.*  
>  
> *2. **Deterministic Scheduling Engine** (`backend/app/services/scheduling_service.py`):*  
> *(Show file on screen)*  
> *Here is `get_feasible_slots()` and `book_appointment_deterministic()`. Notice how it cross-references technician skills, bay capability types, and existing bookings. Notice the idempotency check and the clean rescheduling logic that prevents unique constraint crashes.*  
>  
> *3. **Email Notification & Customer Portal Service** (`backend/app/services/email_service.py` & `backend/app/routers/customer_portal.py`):*  
> *(Show file on screen)*  
> *We have `send_verification_otp()`, `verify_email_otp()`, and `dispatch_transactional_email()`. These generate responsive HTML transactional emails with SHA-256 OTP hashes, expiring in 15 minutes, and log them into `EmailNotification` for full auditability.*  
>  
> *4. **Domain Models & Audit Events** (`backend/app/models/entities.py`):*  
> *(Show file on screen)*  
> *We have relational tables for Workshops, Mechanics, Service Bays, Parts, Inventory Movements, Estimates, Email Notifications, and Audit Events. Every significant mutation calls `log_audit_event()`, ensuring a tamper-proof audit trail.*  
>  
> *5. **Frontend Architecture** (`frontend/src/app/page.tsx` & `frontend/src/lib/api.ts`):*  
> *(Show file on screen)*  
> *In `frontend/src/lib/api.ts`, we use relative paths (`/api/...`) in the browser with Next.js reverse-proxy rewrites to `http://127.0.0.1:8000`. This completely eliminates CORS preflight overhead and IPv6 localhost resolution mismatches.*  
>  
> *6. **Automated Testing Suite** (`backend/tests/test_pitstop.py`):*  
> *(Open terminal and run: `pytest backend/tests -v`)*  
> *Finally, our test suite runs 5 comprehensive tests verifying AI safety guardrails, deterministic scheduling, idempotency, inventory deduction, and calendar failure recovery—passing with 100% success."*

---

### SECTION 5: Wrap-Up & Conclusion (8:00 – 8:30)

**[Screen Visual]**: Return to camera or dashboard with all KPIs active.

> **Voiceover / Presentation**:  
> *"In summary, PitStop AI delivers a complete, cohesive two-sided product that automotive workshops and vehicle owners can rely on: AI speed for intake and triage, combined with deterministic software engineering for safety, scheduling, customer transparency, and financial accountability.*  
>  
> *Thank you Kidus and the Brain3.ai team for reviewing this proposal and implementation. I look forward to your feedback!"*

---

## ✉️ Part B: Submission Email Template

Copy and fill this email to submit your project before midnight:

```text
To: kidus@brain3.ai
Subject: PitStop AI Submission - Hiruy Mengistu - AI SWE Evaluation

Hi Kidus,

I have completed the implementation and verification of PitStop AI according to our approved Revised SRS v2.0 specification.

Here are the submission materials:

1. Demonstration Video:
   [Insert Loom / Google Drive / YouTube Video Link Here]
   (Follows the exact 4-part presentation: Problem Statement, Solution Design, UI & AI Demonstration including the Vehicle Owner Portal, and Full-Stack Code Walkthrough).

2. Source Code Repository:
   https://github.com/Hir1420/PitStop-AI
   (Monorepo containing Next.js 14 frontend, FastAPI backend, Docker Compose, and automated tests).

3. Key Highlights & Deliverables:
   - Two-Sided Operations Platform: Workshop Staff Operations Hub alongside a dedicated Vehicle Owner Portal ("My PitStop Garage") with passwordless email OTP verification.
   - AI Intake & Safety Guardrails: Hybrid Google Gemini API with deterministic fallback engine; automatically escalates safety-critical brake/hydraulic issues with cautious guidance.
   - Deterministic Scheduling Engine: Mathematically enforces mechanic skill certifications, bay hydraulic lift capability, and business hours with idempotency key protection.
   - Human-in-the-Loop Governance: Financial estimates require authorized sign-off, with customer digital authorization directly from their mobile-ready garage portal.
   - Event-Driven Email Notification Engine: Automated responsive HTML transactional emails for OTP logins, booking confirmations, estimate authorizations, and vehicle pickup alerts, viewable in a live in-app Outbox drawer.
   - Resilient Integrations: Google Calendar sync with simulated 503 failure and retry recovery path; Open-Meteo live weather context.
   - Comprehensive Testing: 5/5 automated unit/integration tests with Pytest and 10/10 end-to-end verification passing with 100% success.
   - Documentation: Complete README.md quickstart guide, architecture diagrams, and approved SRS v2.0 in /docs.

4. Quickstart Command:
   - Backend: $env:PYTHONPATH="backend"; .\backend\venv\Scripts\python -m uvicorn app.main:app --port 8000
   - Frontend: npm run dev (in frontend directory, opens at http://localhost:3000)
   - Docker: docker compose up --build

Thank you for the opportunity to work on this assignment. I look forward to your thoughts and feedback!

Best regards,
Hiruy Mengistu
```

