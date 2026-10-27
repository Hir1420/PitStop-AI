import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.config import settings
from app.models.entities import EmailVerification, EmailNotification, Customer
from app.services.audit_service import log_audit_event

import httpx

def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"

def deliver_via_resend(recipient: str, subject: str, html_content: str) -> bool:
    """Delivers real transactional email via Resend API."""
    if not settings.RESEND_API_KEY:
        return False
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": settings.RESEND_FROM,
            "to": [recipient],
            "subject": subject,
            "html": html_content
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                print(f"[Resend Delivery OK] Real email successfully sent to {recipient}")
                return True
            else:
                err_data = resp.json()
                print(f"[Resend Notice] {resp.status_code}: {err_data.get('message', resp.text)}")
                return False
    except Exception as e:
        print(f"[Resend Error] Failed to send via Resend: {e}")
        return False

def deliver_smtp(recipient: str, subject: str, html_content: str) -> bool:
    """Attempts to deliver a real email over SMTP (e.g. Gmail) if credentials are configured in .env."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        from_name = settings.SMTP_FROM_NAME or "PitStop AI Workshop"
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = recipient

        part = MIMEText(html_content, "html")
        msg.attach(part)

        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(from_email, [recipient], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP Delivery Error] Failed sending real email to {recipient}: {e}")
        return False

def deliver_real_email(recipient: str, subject: str, html_content: str) -> bool:
    """Dispatches a real email via Resend API or SMTP if either is configured."""
    if settings.RESEND_API_KEY and deliver_via_resend(recipient, subject, html_content):
        return True
    if settings.SMTP_USER and settings.SMTP_PASSWORD and deliver_smtp(recipient, subject, html_content):
        return True
    return False


def send_verification_otp(db: Session, email: str, workshop_id: int = 1) -> Dict[str, Any]:
    """Generates a 6-digit OTP code, stores it with expiration, and drafts an email."""
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    verif = EmailVerification(
        email=email.strip().lower(),
        code=code,
        is_verified=False,
        created_at=datetime.utcnow(),
        expires_at=expires_at
    )
    db.add(verif)

    # HTML template for verification email
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0c1222; color: #f1f5f9; padding: 30px; border-radius: 16px; border: 1px solid #1e293b;">
        <div style="border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px;">
            <span style="font-size: 22px; font-weight: 800; color: #f97316;">PitStop AI</span>
            <span style="font-size: 12px; background-color: rgba(249, 115, 22, 0.1); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); padding: 3px 8px; border-radius: 999px; margin-left: 8px;">Vehicle Owner Garage</span>
        </div>
        <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">Sign In Verification Code</h2>
        <p style="color: #94a3b8; font-size: 14px; line-height: 1.5;">Use the single-use verification code below to access your PitStop AI Vehicle Owner Portal, view real-time repair progress, and authorize estimates.</p>
        <div style="background-color: #172554; border: 1px solid #1d4ed8; padding: 18px; text-align: center; border-radius: 12px; margin: 25px 0;">
            <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #38bdf8; font-family: monospace;">{code}</span>
        </div>
        <p style="color: #64748b; font-size: 12px;">This code expires in 15 minutes. If you did not request this code, you can safely ignore this email.</p>
    </div>
    """

    # Attempt real email delivery (Resend API or SMTP) if configured
    is_delivered = deliver_real_email(email.strip().lower(), "Your PitStop AI Garage Sign-In Code", html_content)

    notif = EmailNotification(
        recipient_email=email.strip().lower(),
        subject="Your PitStop AI Garage Sign-In Code",
        content_html=html_content,
        notification_type="auth_code",
        status="delivered" if is_delivered else "sent",
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="email_verification_sent",
        entity_type="auth",
        entity_id=email,
        actor_id=email,
        actor_role="customer",
        metadata={
            "expires_at": expires_at.isoformat(),
            "real_delivered": is_delivered
        }
    )

    return {
        "success": True,
        "message": f"Verification code sent to {email}",
        "code_preview": code  # Available for easy review during demo
    }

def verify_email_otp(db: Session, email: str, code: str, workshop_id: int = 1) -> Dict[str, Any]:
    """Validates the OTP code, logs in the customer, and returns their profile."""
    clean_email = email.strip().lower()
    now = datetime.utcnow()

    verif = db.query(EmailVerification).filter(
        EmailVerification.email == clean_email,
        EmailVerification.code == code.strip(),
        EmailVerification.is_verified == False,
        EmailVerification.expires_at >= now
    ).order_by(EmailVerification.created_at.desc()).first()

    if not verif:
        raise ValueError("Invalid or expired verification code. Please request a new code.")

    verif.is_verified = True

    # Find or auto-provision Customer profile
    customer = db.query(Customer).filter(
        Customer.email == clean_email,
        Customer.workshop_id == workshop_id
    ).first()

    if not customer:
        customer_name = clean_email.split("@")[0].replace(".", " ").title()
        customer = Customer(
            workshop_id=workshop_id,
            name=customer_name,
            email=clean_email,
            phone="Not Provided",
            created_at=now
        )
        db.add(customer)

    db.commit()
    db.refresh(customer)

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="customer_email_verified",
        entity_type="customer",
        entity_id=str(customer.id),
        actor_id=customer.name,
        actor_role="customer",
        metadata={"email": clean_email}
    )

    return {
        "verified": True,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        },
        "session_token": f"pitstop_cust_{customer.id}_{int(now.timestamp())}"
    }

def dispatch_transactional_email(
    db: Session,
    recipient_email: str,
    subject: str,
    headline: str,
    body_text: str,
    notification_type: str,
    customer_id: Optional[int] = None,
    badge_label: str = "Status Update",
    highlight_text: Optional[str] = None
) -> EmailNotification:
    """Dispatches a branded HTML transactional update email to vehicle owners."""
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0c1222; color: #f1f5f9; padding: 30px; border-radius: 16px; border: 1px solid #1e293b;">
        <div style="border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 22px; font-weight: 800; color: #f97316;">PitStop AI</span>
                <span style="font-size: 11px; color: #94a3b8; display: block; margin-top: 2px;">Apex Workshop Operations</span>
            </div>
            <span style="font-size: 11px; background-color: rgba(56, 189, 248, 0.1); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 3px 8px; border-radius: 999px;">{badge_label}</span>
        </div>
        <h2 style="color: #ffffff; font-size: 18px; margin-top: 0;">{headline}</h2>
        <p style="color: #94a3b8; font-size: 14px; line-height: 1.6;">{body_text}</p>
        {f'<div style="background-color: #1e293b; border-left: 4px solid #f97316; padding: 14px 18px; border-radius: 8px; margin: 20px 0; font-size: 14px; color: #f8fafc;">{highlight_text}</div>' if highlight_text else ''}
        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b;">
            Track your vehicle progress anytime at <a href="http://localhost:3000" style="color: #f97316; text-decoration: none;">PitStop AI Garage</a>.
        </div>
    </div>
    """

    # Attempt real email delivery (Resend API or SMTP) if configured
    is_delivered = deliver_real_email(recipient_email.strip().lower(), subject, html_content)

    notif = EmailNotification(
        customer_id=customer_id,
        recipient_email=recipient_email.strip().lower(),
        subject=subject,
        content_html=html_content,
        notification_type=notification_type,
        status="delivered" if is_delivered else "sent",
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
