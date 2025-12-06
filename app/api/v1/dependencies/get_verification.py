from ....core.db import AsyncSessionLocal
from ....repositories.email_verify_tokens_repo import EmailVerifyTokensRepo
from ....core.mailer import ResendMailer

def get_verification_repo() -> EmailVerifyTokensRepo:
    return EmailVerifyTokensRepo(AsyncSessionLocal)


# Get mailer

def get_mailer() -> ResendMailer:
    return ResendMailer()
