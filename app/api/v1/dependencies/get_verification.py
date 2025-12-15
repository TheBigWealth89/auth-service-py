from ....core.db import AsyncSessionLocal
from ....domain.abstracts.email_verify_abstract import IEmailRepository
from ....repositories.email_verify_tokens_repo import EmailVerifyTokensRepo
from ....core.mailer import ResendMailer

def get_verification_repo() -> IEmailRepository:
    return EmailVerifyTokensRepo(AsyncSessionLocal)


# Get mailer

def get_mailer() -> ResendMailer:
    return ResendMailer()
