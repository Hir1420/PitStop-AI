PitStop AI
AI-Powered Workshop Operations Platform
Revised Software Requirements Specification (SRS)and High-Level Solution DesignPrepared by Hiruy MengistuFor Brain3.ai — Project Design Review24 October 2026Revised draft for review and approval before implementation
Document Control
Field
Value
Project
PitStop AI
Document
Revised SRS and High-Level Solution Design
Version
2.0 — Expanded proposal
Prepared by
Hiruy Mengistu
Review audience
Brain3.ai
Status
Proposed; subject to reviewer feedback
Primary objective
Demonstrate AI-agent workflows, product thinking, and reliable full-stack engineering
1. Executive Summary
PitStop AI is an AI-powered operations platform for independent automotive workshops. It helps coordinate customer requests, work orders, mechanic capacity, parts availability, estimates, appointments, and customer communication through AI-assisted workflows and explicit business rules.
It is not a generic chatbot or an autonomous mechanic. Its AI agent gathers and structures information, selects from a limited set of authorized tools, proposes next steps, and coordinates multi-step workflows. Deterministic backend services validate data, enforce permissions, maintain consistency, and require human approval for consequential actions.
This revision emphasizes a coherent end-to-end service workflow, proactive automation, operational visibility, and engineering reliability. Implementation should prioritize a demonstrable vertical slice before expanding to secondary features.
2. Problem Statement and Opportunity
Independent workshops often coordinate customer messages, appointment books, mechanic schedules, parts inventory, quotes, and job status manually or across disconnected tools. This can cause incomplete intake information, scheduling conflicts, delays caused by missing parts, inconsistent customer updates, and limited visibility into daily operations.
PitStop AI maintains a shared operational record and helps staff coordinate the lifecycle of a service request—from intake to completed work—while leaving safety-sensitive and financially consequential decisions under human control.
3. Target Users and Roles
Customer: submits a service request, provides vehicle details, reviews proposed appointments and estimates, and receives updates.
Service advisor/workshop coordinator: reviews intake, creates work orders, prepares estimates, and coordinates bookings.
Mechanic: reviews assigned work, adds inspection notes, and updates job status.
Workshop manager/owner: configures services, rates, hours, staff skills, inventory, approval policies, and views analytics.
Platform administrator: manages platform-level configuration where needed for the prototype.
4. Product Goals and Success Criteria
Reduce manual effort needed to turn unstructured customer messages into actionable service requests.
Coordinate appointments using mechanic skills, service duration, working hours, bay capacity, existing bookings, and parts readiness.
Maintain a traceable record of AI tool calls, approvals, status changes, and integration outcomes.
Provide workshop visibility through work-order, inventory, scheduling, and operational dashboards.
Demonstrate reliability through automated tests, validation, idempotent actions, and recovery from integration failures.
Proposed success measures:
A customer message becomes a structured, reviewable work order.
The scheduling engine rejects conflicts and offers valid alternatives.
A repeated request does not create a duplicate appointment.
The dashboard reflects persisted backend data, not hard-coded demo values.
Important changes and AI-triggered actions appear in an audit trail.
The demo includes a successful path and at least one failure/recovery path.
5. Scope
5.1 In Scope
AI-assisted service intake and follow-up questions.
Structured service requests and work orders with lifecycle states.
Preliminary symptom triage without claiming definitive diagnosis.
Scheduling based on mechanic skills, service duration, business hours, bay capacity, and parts readiness.
Parts inventory tracking and estimates using configured prices and labor rates.
Customer-facing appointment and estimate confirmation workflows.
Google Calendar integration for availability and event synchronization, subject to API setup and permissions.
Open-Meteo integration for weather-sensitive services such as washing and detailing.
Background reminders, overdue-job checks, and integration retry handling.
Role-based dashboard, basic operational metrics, and audit history.
Automated tests, local setup instructions, and containerization.
5.2 Out of Scope for the Initial Prototype
Autonomous physical vehicle diagnosis or safety certification.
Automatic purchasing of parts, charging customers, or issuing refunds.
Real payment processor integration.
A public marketplace connecting many workshops and vehicle owners.
Predictive maintenance based on large-scale telematics or OEM data.
Production-grade multi-region deployment or formal regulatory certification.
These may be considered future extensions if time and reviewer expectations allow.
6. Core Product Workflows
6.1 Customer Intake to Work Order
Customer submits a message and basic vehicle information.
Gemini-powered logic extracts candidate vehicle, symptom, service, urgency, and preferred scheduling fields.
Backend validates the extracted data and identifies missing or ambiguous fields.
Agent asks targeted follow-up questions; configured safety-critical indicators trigger human review and cautious guidance.
System saves a draft request; an authorized staff member reviews it and converts it to a work order.
6.2 Scheduling and Capacity Coordination
Scheduling checks business hours, mechanic skills/availability, bay capacity, service duration, existing appointments, and required parts.
Deterministic rules generate feasible slots; AI can explain trade-offs but cannot override constraints.
Customer or staff selects a proposed slot.
Backend revalidates availability before committing and then synchronizes the calendar.
Idempotency keys and database constraints prevent duplicate bookings on retries.
6.3 Inventory and Estimate Preparation
Work order is associated with likely parts or service categories using staff configuration and intake data.
Inventory service checks stock and flags shortages.
Estimate service calculates a draft from configured prices, labor rates, and estimated duration.
Estimate requires approval under workshop policy; no purchase or payment is made automatically.
6.4 Proactive Job Monitoring
Background jobs identify upcoming appointments, overdue work orders, missing parts, and pending approvals.
System prepares reminders or alerts and records their status.
Transient failures are retried with bounded backoff; repeated failures become visible to staff.
6.5 Job Completion and Analytics
Mechanics record inspection notes, parts used, labor, and job status.
Authorized staff review completed work and close the work order.
Dashboard summarizes active and overdue jobs, appointment utilization, inventory shortages, and configured revenue totals.
AI summaries are grounded in permitted records and label the relevant time period and data source.
7. Functional Requirements
ID
Capability
Requirement
FR-01
Service intake
Accept customer requests and store the original message with structured fields.
FR-02
AI extraction
Extract candidate vehicle, symptom, service, urgency, and scheduling fields into a validated schema.
FR-03
Clarification
Identify missing fields and support follow-up questions before staff review.
FR-04
Safety escalation
Flag configured safety-critical patterns and direct cases to professional review without claiming diagnosis.
FR-05
Work orders
Allow authorized users to create, assign, update, and close work orders using defined states.
FR-06
Scheduling
Return feasible slots using hours, capacity, skills, duration, and existing bookings.
FR-07
Booking confirmation
Require explicit confirmation and revalidate availability before booking.
FR-08
Calendar integration
Synchronize confirmed appointments and record failures.
FR-09
Inventory
Maintain part records, stock quantities, reorder thresholds, and stock movements.
FR-10
Estimates
Calculate draft estimates from configured rates and require approval.
FR-11
Weather context
Retrieve Open-Meteo forecasts for weather-sensitive services.
FR-12
Background automation
Schedule reminders and monitor overdue jobs or pending approvals.
FR-13
Dashboard
Show role-appropriate operational information.
FR-14
Audit history
Record state changes, approvals, and integration outcomes with actor, time, and correlation ID.
FR-15
Resilience
Handle transient failures with bounded retries and visible failure states.
FR-16
Analytics
Calculate operational metrics from persisted data and label periods/definitions.
FR-17
Tenant isolation
Restrict workshop users to their authorized workshop data.
FR-18
Observability
Provide structured logs and health endpoints.
8. AI Agent Design and Guardrails
The AI agent is an orchestration and language-understanding layer, not the source of truth for business state. Gemini may interpret messages, propose tool calls, and summarize records. Backend code validates every tool input and output.
8.1 Proposed Agent Tools
extract_service_request(message, vehicle_context): return a schema-validated draft, uncertainty indicators, and missing fields.
get_available_slots(service_type, duration, preferred_window): query the deterministic scheduling service.
check_inventory(required_parts): retrieve current stock.
calculate_estimate(work_order_id): calculate a draft using configured rates and prices.
get_weather_forecast(location, date): retrieve Open-Meteo forecast data.
create_or_update_booking(approved_request): execute only after authorization and explicit confirmation.
update_work_order_status(work_order_id, next_status): enforce role permissions and allowed transitions.
prepare_customer_notification(event): draft a notification; backend policy controls delivery.
8.2 Tool Execution Policy
Enforce authentication, role permissions, workshop tenant boundaries, and input schemas for protected operations.
Use deterministic backend rules for scheduling, totals, inventory changes, and state transitions.
Require explicit approval for bookings, estimate acceptance, inventory adjustments, and other consequential changes.
Never expose secrets or unrestricted database access to the model.
Treat customer messages and external API responses as untrusted input.
Record tool invocation outcomes and correlation IDs while avoiding unnecessary sensitive content in logs.
Use timeouts, bounded retries, and idempotency for repeatable operations.
8.3 Human-in-the-Loop Model
The agent may prepare recommendations and draft actions. Backend policy or an authorized person must approve consequential operations. Safety-sensitive cases, uncertain extraction, conflicting records, and repeated integration failures are escalated to staff.
9. High-Level Architecture
Layer
Proposed responsibility / technology
Frontend
Next.js App Router, React, TypeScript, Tailwind CSS; customer request flow and staff operations dashboard.
API/application
Python + FastAPI; authentication, authorization, validation, application services, API contracts.
AI orchestration
Gemini API; structured extraction, tool selection, clarification, and grounded summaries.
Domain services
Intake, work orders, scheduling, inventory, estimates, notifications, and analytics.
Persistence
PostgreSQL with SQLAlchemy and Alembic migrations.
Background processing
Worker/queue for reminders, scheduled checks, and retries; specific technology confirmed during implementation.
External services
Google Calendar API and Open-Meteo; optional notification provider only if a suitable free option is verified.
Quality/operations
Pytest, frontend/API integration tests, structured logs, health checks, Docker local environment.
Conceptual flow: Next.js UI → FastAPI authentication and application services → AI orchestration and domain tools → PostgreSQL / background workers / external APIs. The model never bypasses backend authorization or business rules.
10. Proposed Data Model
Entity
Illustrative fields
Workshop
id, name, timezone, business_hours, settings, created_at
User
id, workshop_id, name, email, identity reference, role, active
Customer
id, workshop_id, name, contact details, notification preferences
Vehicle
id, workshop_id, customer_id, make, model, year, reference, optional mileage
ServiceRequest
id, workshop_id, customer_id, vehicle_id, original_message, structured_intake, priority, status, created_at
ConversationMessage
id, request_id, sender_type, content, safe metadata, created_at
WorkOrder
id, workshop_id, request_id, mechanic_id, service_type, status, duration, notes
Appointment
id, workshop_id, work_order_id, start_at, end_at, bay_id, calendar_event_id, status, idempotency_key
Mechanic
id, workshop_id, user_id, skills, working_hours, active
ServiceBay
id, workshop_id, name, supported_service_types, active
Part
id, workshop_id, SKU, name, quantity_on_hand, reorder_threshold, unit_cost, unit_price
InventoryMovement
id, workshop_id, part_id, quantity_delta, reason, work_order_id, actor_id, created_at
Estimate
id, workshop_id, work_order_id, line items, total, status, approver, approved_at
AutomationJob
id, workshop_id, job_type, payload reference, status, attempts, run_after, last_error_code
AuditEvent
id, workshop_id, actor_id, action, entity type/id, timestamp, correlation_id, safe metadata
IntegrationEvent
id, workshop_id, provider, operation, external reference, status, attempts, last error
Core transactional data will use relational tables. Flexible JSON may store AI extraction metadata, but business-critical values such as status, appointment times, stock quantities, and prices remain validated and queryable. Database constraints and transactions protect consistency.
11. Proposed API Design
Method
Route
Purpose
POST
/api/requests/intake
Structure a message and return missing fields; does not confirm bookings.
POST
/api/requests
Create a service request.
GET
/api/requests
List requests filtered by permitted status/date.
GET
/api/requests/{id}
Retrieve a request and authorized history.
POST
/api/work-orders
Create a work order from a reviewed request.
PATCH
/api/work-orders/{id}
Update permitted fields or status.
GET
/api/availability
Return feasible slots using deterministic rules.
POST
/api/appointments/confirm
Confirm an approved slot with idempotency and revalidation.
GET
/api/inventory/parts
List parts and stock status.
POST
/api/inventory/movements
Record authorized stock movements.
POST
/api/estimates
Generate a draft estimate.
POST
/api/estimates/{id}/approve
Approve an estimate under policy.
GET
/api/analytics/summary
Return role-filtered operational metrics.
GET
/api/integrations/weather
Retrieve weather context.
POST
/api/integrations/calendar/sync
Retry/request authorized calendar synchronization.
GET
/api/audit-events
Retrieve authorized audit history.
GET
/api/health
Basic application health.
GET
/api/ready
Readiness check for required dependencies.
12. Security, Privacy, and Reliability
Authentication and role-based authorization for customers, mechanics, coordinators, and managers.
Workshop-scoped access enforced on the server, not only in the user interface.
Secrets kept in environment variables and excluded from source control.
Input validation, safe error responses, and protection against prompt injection in customer-provided content.
Transactional updates for bookings, inventory movements, and work-order state changes.
Idempotency for booking and external side-effect operations.
Audit records for approvals and important mutations.
Retries only for suitable transient failures; no blind retries for non-idempotent actions.
Timeouts and graceful degradation when Gemini or external services are unavailable.
Data minimization and no storage of payment-card data.
AI output is treated as an untrusted suggestion and validated before persistence.
Logs avoid credentials and unnecessary sensitive customer information.
13. Non-Functional Requirements
Maintainability: modular domain services, typed schemas, clear boundaries, and migrations.
Correctness: business rules enforced in backend services and database constraints where appropriate.
Performance: responsive operations on a small demonstration dataset; no unsupported production SLA claims.
Reliability: integration failures remain visible and must not silently corrupt core records.
Testability: unit tests for domain rules, API/database integration tests, and end-to-end tests for the main workflow.
Usability: responsive interface, clear statuses/errors, and reviewable AI-generated content.
Portability: Docker-based local setup and documented environment variables.
Accessibility: semantic controls, keyboard-accessible workflows, and readable status indicators.
14. Proposed Technology Stack
Area
Proposed choice
Frontend
Next.js App Router, React, TypeScript, Tailwind CSS
Backend
Python, FastAPI, Pydantic
Database / ORM / migrations
PostgreSQL, SQLAlchemy, Alembic
AI
Gemini API with structured output and tool calling
External integrations
Google Calendar API and Open-Meteo API
Background jobs
A lightweight queue/worker selected based on deadline and environment; Celery/Redis is one candidate.
Testing
Pytest, API integration tests, and an appropriate frontend/e2e test tool.
Developer tools
Git/GitHub, Postman or equivalent API client, Docker, environment-based configuration.
Deployment
Local-first; cloud hosting only after verifying current free-tier access, quotas, and billing requirements.
15. Implementation Plan
Phase 1 — Foundation and core records
Set up repositories, frontend, FastAPI, PostgreSQL, migrations, environment configuration, and Docker development workflow.
Implement the initial user/role model and workshop-scoped records.
Build service request, customer, vehicle, work-order, and audit models with tests.
Phase 2 — AI intake and workflow
Integrate Gemini for structured intake and clarification.
Add schema validation, tool registry, approval boundaries, and safe fallbacks.
Demonstrate request-to-work-order conversion.
Phase 3 — Scheduling and integrations
Implement deterministic capacity/conflict checks.
Integrate Google Calendar with authorization, idempotency, and sync status.
Integrate Open-Meteo for weather-aware services.
Phase 4 — Inventory, estimates, and proactive tasks
Implement inventory and stock movements.
Generate draft estimates from configured prices.
Add reminders, overdue checks, and bounded retries.
Phase 5 — Dashboard, quality, and demo
Build staff dashboard, work-order detail, inventory status, and operational summaries.
Test primary and failure paths.
Prepare seed data, setup instructions, architecture notes, and demo video.
Prioritization rule: if time is constrained, complete the vertical slice of AI intake → work order → scheduling → explicit approval → booking before broadening secondary features.
16. Acceptance Criteria
A request can be entered, structured by AI, validated, and saved.
Missing fields trigger clarification rather than invented details.
Staff can review a request and create a work order.
Scheduling respects configured hours, capacity, skills, duration, and existing bookings.
A booking requires confirmation, revalidates availability, and avoids duplicate retries.
Calendar synchronization status is visible and failures can be retried safely.
Inventory and estimates use configured stored data; estimates remain drafts until approved.
Weather context includes source/time information and does not independently make consequential decisions.
Role boundaries prevent unauthorized reads or writes.
Important actions appear in an audit history.
Tests cover the main workflow and at least one failure scenario.
Documented setup works without committing secrets.
17. Risks, Assumptions, and Open Questions
Google Calendar API setup, OAuth configuration, and test-account availability must be confirmed early.
Gemini model access, quotas, and tool-calling behavior depend on the selected API/model and current account limits.
Open-Meteo forecast coverage varies by location and date range.
Background processing may need to be simplified to fit the assignment deadline.
The prototype will demonstrate one workshop first, while records and authorization are workshop-scoped.
Pricing, service duration, mechanic skills, and inventory are configured data; the AI must not invent these values.
Initial operational policies are demo assumptions until validated with a real workshop.
Feature priorities and acceptance criteria should be confirmed with Brain3.ai before implementation.
18. Demonstration Scenario
A customer reports a brake-related concern and requests an appointment. PitStop AI asks for missing context, extracts a structured request, and flags configured safety indicators for human review. A service advisor reviews the request and creates a work order. The system checks mechanic capacity, bay availability, and parts readiness, then presents feasible appointment options and a draft estimate. After explicit confirmation, the backend revalidates the slot, persists the appointment, and synchronizes Google Calendar. A background task schedules a reminder. The dashboard displays the request, work order, appointment, inventory state, and audit trail. The demo also shows a calendar/API failure and the system's visible recovery path.
19. Deliverables
Revised SRS and high-level solution design.
Working full-stack prototype and source code.
Database schema and migration files.
Documented API endpoints and example requests.
Automated tests for core business rules and the main workflow.
Environment example file without secrets, Docker/local setup guide, and README.
Architecture overview and key design decisions.
Demo video explaining the problem, workflow, architecture, implementation, and trade-offs.
Known limitations and future improvement notes.
20. Approval Request
This revised proposal expands PitStop AI from a basic appointment assistant into an AI-powered workshop operations platform with an end-to-end workflow, operational constraints, proactive automation, and explicit reliability controls. Before implementation, I would appreciate confirmation that the revised scope and prioritized vertical slice meet the assignment expectations, along with any recommended adjustments to feature priorities or technical depth.