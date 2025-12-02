import resend
from .config import RESEND_API_KEY


class ResendMailer:
    def __init__(self):
        self.api_key = RESEND_API_KEY
        resend.api_key = self.api_key

    async def send_verification_email(self, email: str, token: str):
        link = f"http://localhost:8000/auth/v1/verify-email?token={token}"

        resend.Emails.send({
            "from": "Auth-Service <onboarding@resend.dev>",
            "to": email,
            "subject": "Verify Your Email",
            "html": f"<p>Click to verify:</p><a href='{link}'>Verify Email</a>"
        })
