from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_ics(sender, **kwargs):
    ics_content = f"""BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//Your Company//Your Product//EN
    BEGIN:VEVENT
DTSTAMP:{(datetime.now() + timedelta(days=1)).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{(datetime.now() + timedelta(days=1)).strftime('%Y%m%dT%H%M%SZ')}
    SUMMARY:Order 10
    DESCRIPTION:Order details
    END:VEVENT
    END:VCALENDAR"""

    # Create the email
    email = EmailMessage(
        subject=f"Order  Confirmation",
        body="Please find the attached ICS file for your order.",
        to=["nhanhoa21012002@gmail.com"],
    )
    email.attach(f"order.ics", ics_content, "text/calendar")
    email.send()
    return "Email sent"
