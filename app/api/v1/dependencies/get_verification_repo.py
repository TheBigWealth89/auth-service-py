from ....core.db import AsyncSessionLocal
from ....repositories.email_verify_tokens_repo import EmailVerifyTokensRepo


def get_verification_repo() -> EmailVerifyTokensRepo:
    return EmailVerifyTokensRepo(AsyncSessionLocal)




