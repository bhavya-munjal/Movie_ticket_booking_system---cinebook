"""
Email Service - Mock Implementation
To integrate real email: replace _send() with SMTP/SendGrid/SES calls.
All email logic routes through this single file.
"""
from datetime import datetime

def _send(to: str, subject: str, body: str):
    """
    MOCK: Replace this function body with real SMTP/API call.
    Example for SendGrid:
        import sendgrid
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_KEY)
        ...
    """
    print("\n" + "="*50)
    print(f"📧 EMAIL NOTIFICATION [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"TO      : {to}")
    print(f"SUBJECT : {subject}")
    print(f"BODY    :\n{body}")
    print("="*50 + "\n")

def send_booking_confirmation(user_name: str, user_email: str, booking_ref: str,
                               movie_title: str, show_date: str, show_time: str,
                               seat_labels: str, total_amount: float):
    subject = f"Booking Confirmed - {booking_ref} | {movie_title}"
    body = f"""Hi {user_name},

Your booking is confirmed! 🎬

  Movie     : {movie_title}
  Date/Time : {show_date} at {show_time}
  Seats     : {seat_labels}
  Amount    : ₹{total_amount:.2f}
  Ref No    : {booking_ref}

Enjoy the show!
— CineBook Team"""
    _send(user_email, subject, body)

def send_cancellation_email(user_name: str, user_email: str, booking_ref: str, movie_title: str):
    subject = f"Booking Cancelled - {booking_ref}"
    body = f"""Hi {user_name},

Your booking {booking_ref} for {movie_title} has been cancelled.
Refund (if applicable) will be processed in 5–7 business days.

— CineBook Team"""
    _send(user_email, subject, body)

def send_welcome_email(user_name: str, user_email: str):
    subject = "Welcome to CineBook!"
    body = f"""Hi {user_name},

Welcome to CineBook! 🎉
Start exploring movies and book your seats now.

— CineBook Team"""
    _send(user_email, subject, body)
