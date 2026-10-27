import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_full_e2e_flow():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("=== 1. Health & Readiness ===")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("Health:", r.json())

    print("\n=== 2. AI Intake & Safety Escalation ===")
    intake_payload = {
        "message": "Hi, my 2021 Toyota Camry has spongy brakes and grinding noise on highway. Need urgent inspection.",
        "customer_name": "Alex Mercer",
        "customer_phone": "415-555-0199",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2021
    }
    r = client.post("/api/requests/intake", json=intake_payload)
    assert r.status_code == 200
    extracted = r.json()
    print("Extracted Service:", extracted["proposed_service_type"])
    print("Urgency:", extracted["urgency"])
    print("Safety Escalation:", extracted["safety_escalation"])
    assert extracted["safety_escalation"] is True
    assert extracted["urgency"] == "safety_critical"

    print("\n=== 3. Persist Service Request ===")
    r = client.post("/api/requests", json={
        "workshop_id": 1,
        "original_message": intake_payload["message"],
        "customer_name": intake_payload["customer_name"],
        "customer_phone": intake_payload["customer_phone"],
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2021
    })
    assert r.status_code == 200
    req_data = r.json()
    req_id = req_data["id"]
    print(f"Created Service Request #{req_id}, Status: {req_data['status']}")

    print("\n=== 4. Convert to Work Order ===")
    r = client.post("/api/work-orders", json={
        "workshop_id": 1,
        "request_id": req_id,
        "service_type": "brake_service",
        "estimated_duration_minutes": 90,
        "customer_complaint": intake_payload["message"]
    })
    assert r.status_code == 200
    wo_data = r.json()
    wo_id = wo_data["id"]
    print(f"Created Work Order #{wo_id}, Status: {wo_data['status']}")

    print("\n=== 5. Query Deterministic Feasible Slots ===")
    r = client.get("/api/availability", params={
        "workshop_id": 1,
        "service_type": "brake_service",
        "duration_minutes": 90,
        "target_date": "2026-10-26"
    })
    assert r.status_code == 200
    slots = r.json()
    available = [s for s in slots if s["available"]]
    print(f"Total slots returned: {len(slots)}, Available certified slots: {len(available)}")
    chosen_slot = available[0]
    print(f"Selected slot: {chosen_slot['start_at']} in {chosen_slot['bay_name']} (Tech: {chosen_slot['mechanic_name']})")

    print("\n=== 6. Book Appointment with Idempotency Key ===")
    idempotency_key = f"e2e_test_key_{wo_id}_1"
    booking_payload = {
        "workshop_id": 1,
        "work_order_id": wo_id,
        "bay_id": chosen_slot["bay_id"],
        "mechanic_id": chosen_slot["mechanic_id"],
        "start_at": chosen_slot["start_at"],
        "idempotency_key": idempotency_key
    }
    r = client.post("/api/appointments/confirm", json=booking_payload)
    assert r.status_code == 200
    app_data = r.json()
    app_id = app_data["id"]
    print(f"Booked Appointment #{app_id}, Calendar Sync: {app_data['calendar_sync_status']}")

    # Re-submit with same idempotency key (must succeed without error or duplicate)
    r_retry = client.post("/api/appointments/confirm", json=booking_payload)
    assert r_retry.status_code == 200
    assert r_retry.json()["id"] == app_id
    print("Idempotent retry successfully returned same appointment without duplicates!")

    print("\n=== 7. Calculate & Approve Estimate (Human-in-the-Loop) ===")
    r = client.post("/api/estimates", json={"workshop_id": 1, "work_order_id": wo_id, "labor_hours": 1.5})
    assert r.status_code == 200
    est = r.json()
    print(f"Draft Estimate #{est['id']}, Total: ${est['grand_total']}, Status: {est['status']}")
    assert est["status"] == "draft"

    # Human authorization
    r = client.post(f"/api/estimates/{est['id']}/approve", json={
        "approved_by": "Alex Mercer (Customer authorized via Advisor)",
        "notes": "Approved standard ceramic pads and brake fluid replacement"
    })
    assert r.status_code == 200
    approved_est = r.json()
    print(f"Approved Estimate #{approved_est['id']}, Status: {approved_est['status']}, Approver: {approved_est['approver_name']}")
    assert approved_est["status"] == "approved"

    print("\n=== 8. Calendar Sync Failure Injection & Recovery ===")
    # Force failure
    r_fail = client.post(f"/api/integrations/calendar/sync?appointment_id={app_id}&force_failure=true")
    assert r_fail.status_code == 200
    print("Simulated 503 Failure Result:", r_fail.json())
    assert r_fail.json()["success"] is False

    # Recover
    r_rec = client.post(f"/api/integrations/calendar/sync?appointment_id={app_id}&force_failure=false")
    assert r_rec.status_code == 200
    print("Recovery Sync Result:", r_rec.json())
    assert r_rec.json()["success"] is True

    print("\n=== 9. Open-Meteo Weather Integration ===")
    r_weather = client.get("/api/integrations/weather", params={"service_type": "detailing_and_wash"})
    assert r_weather.status_code == 200
    w = r_weather.json()
    print(f"Weather: {w['weather_condition']}, {w['temperature_c']}°C, Precip: {w['precipitation_probability']}%")
    print("Service Advisory:", w.get("advisory_for_service"))

    print("\n=== 10. Operational Analytics & Audit Trail ===")
    r_analytics = client.get("/api/analytics/summary")
    assert r_analytics.status_code == 200
    print("Analytics Summary:", json.dumps(r_analytics.json(), indent=2))

    r_audit = client.get("/api/audit-events", params={"limit": 5})
    assert r_audit.status_code == 200
    print(f"Audit Trail: {len(r_audit.json())} recent events verified.")

    print("\n=== 11. Customer Email OTP Authentication ===")
    r_otp = client.post("/api/customer/auth/send-code", json={"email": "alex.mercer@example.com"})
    assert r_otp.status_code == 200
    otp_data = r_otp.json()
    print("OTP Dispatched:", otp_data)
    code = otp_data["code_preview"]

    r_verify = client.post("/api/customer/auth/verify-code", json={"email": "alex.mercer@example.com", "code": code})
    assert r_verify.status_code == 200
    auth_data = r_verify.json()
    print("Customer Authenticated:", auth_data["customer"]["name"], f"(Verified: {auth_data['verified']})")

    print("\n=== 12. Vehicle Owner Garage & Live Email Outbox ===")
    r_garage = client.get("/api/customer/garage", params={"email": "alex.mercer@example.com"})
    assert r_garage.status_code == 200
    garage_data = r_garage.json()
    print(f"Vehicles in Garage: {len(garage_data['vehicles'])}, Active Repairs: {len(garage_data['active_repairs'])}")

    r_inbox = client.get("/api/customer/notifications/inbox")
    assert r_inbox.status_code == 200
    inbox = r_inbox.json()
    print(f"Dispatched Emails in Outbox: {len(inbox)} messages logged.")
    assert len(inbox) > 0

    print("\n[SUCCESS] ALL 12 END-TO-END WORKFLOW CHECKS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_full_e2e_flow()

