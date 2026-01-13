import resend
from .config import RESEND_API_KEY


class ResendMailer:
    def __init__(self):
        self.api_key = RESEND_API_KEY
        resend.api_key = self.api_key

    async def send_verification_email(self, email: str, token: str):

        link = f"http://localhost:8000/auth/verify-email?token={token}"

        resend.Emails.send({
            "from": "Auth-Service <onboarding@resend.dev>",
            "to": email,
            "subject": "Verify Your Email",
            "html": f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Welcome to Auth-Service 🎉</h2>
        <p>Thanks for creating an account! Before you can start using it, we just need to confirm your email address.</p>
        
        <p>
            <a href="{link}" 
               style="
                   background-color: #4CAF50;
                   color: white;
                   padding: 10px 16px;
                   text-decoration: none;
                   border-radius: 6px;
                   display: inline-block;
                   font-weight: bold;
               ">
                Verify Email
            </a>
        </p>

        <p>If the button above doesn't work, copy and paste this link into your browser:</p>
        <p style="word-break: break-all;">
            {link}
        </p>

        <hr>

        <p style="font-size: 12px; color: #555;">
            This link will expire in 10 minutes for security reasons.
            If you didn’t request this, you can safely ignore the email.
        </p>
    </div>
"""
        })

    async def send_reset_password_email(self, email: str, token: str):

        link = f"http://localhost:8000/auth/reset-password/confirm?token={token}"

        resend.Emails.send({
            "from": "Auth-Service <onboarding@resend.dev>",
            "to": email,
            "subject": "Reset password Email",
            "html": f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Reset your password</h2>
        
        <p>
            <a href="{link}" 
               style="
                   background-color: #4CAF50;
                   color: white;
                   padding: 10px 16px;
                   text-decoration: none;
                   border-radius: 6px;
                   display: inline-block;
                   font-weight: bold;
               ">
                Reset Password
            </a>
        </p>

        <p>If the button above doesn't work, copy and paste this link into your browser:</p>
        <p style="word-break: break-all;">
            {link}
        </p>

        <hr>

        <p style="font-size: 12px; color: #555;">
            This link will expire in 10 minutes for security reasons.
            If you didn’t request this, you can safely ignore the email.
        </p>
    </div>
"""
        })
