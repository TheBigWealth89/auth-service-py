import resend
from .config import RESEND_API_KEY
resend.api_key = RESEND_API_KEY

def send_verification_email(email: str, token: str):
    link = f"https://your-frontend.com/verify?token={token}"

    resend.Emails.send({
        "from": "YourApp <noreply@yourapp.com>",
        "to": email,
        "subject": "Verify Your Email",
        "html": f"<p>Click to verify:</p><a href='{link}'>Verify Email</a>"
    })
