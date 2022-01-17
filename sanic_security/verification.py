import functools
from contextlib import suppress

from sanic.request import Request

from sanic_security.exceptions import AccountError, JWTDecodeError, NotFoundError
from sanic_security.models import (
    Account,
    TwoStepSession,
    SessionFactory,
)

session_factory = SessionFactory()


async def request_two_step_verification(
    request: Request, account: Account = None
) -> TwoStepSession:
    """
    Creates a two-step session.

    Args:
        request (Request): Sanic request parameter. All request bodies are sent as form-data with the following arguments: email.
        account (Account): The account being associated with the verification session. If None, an account is retrieved via email in the request form-data.
        refresh (bool): Deactivates the client's existing two-step session and A refreshed two-step session is returned.

    Raises:
        NotFoundError

    Returns:
         two_step_session
    """
    with suppress(NotFoundError, JWTDecodeError):
        two_step_session = await TwoStepSession.decode(request)
        two_step_session.active = False
        await two_step_session.save(
            update_fields=["active"]
        )  # Deactivates client's existing session.
    if not account:
        account = await Account.get_via_email(request.form.get("email"))
    two_step_session = await session_factory.get("two-step", request, account)
    return two_step_session


async def two_step_verification(request: Request) -> TwoStepSession:
    """
    Validates a two-step verification attempt.

    Args:
        request (Request): Sanic request parameter. All request bodies are sent as form-data with the following arguments: code.

    Raises:
        NotFoundError
        JWTDecodeError
        DeletedError
        ExpiredError
        DeactivatedError
        UnverifiedError
        DisabledError
        UnrecognisedLocationError
        ChallengeError
        MaxedOutChallengeError

    Returns:
         two_step_session
    """
    two_step_session = await TwoStepSession.decode(request)
    two_step_session.validate()
    two_step_session.bearer.validate()
    await two_step_session.check_code(request, request.form.get("code"))
    return two_step_session


async def verify_account(
    request: Request, two_step_session: TwoStepSession = None
) -> TwoStepSession:
    """
    Verifies account with two-step session code.

    Args:
        request (Request): Sanic request parameter. All request bodies are sent as form-data with the following arguments: code.
        two_step_session (TwoStepSession): Two-step session associated with the account being verified. If None, a two-step session is retrieved via client by decoding.

    Raises:
        NotFoundError
        JWTDecodeError
        DeletedError
        ExpiredError
        DeactivatedError
        UnrecognisedLocationError
        ChallengeError
        MaxedOutChallengeError
        AccountError

    Returns:
         two_step_session
    """
    if not two_step_session:
        two_step_session = await TwoStepSession.decode(request)
    if two_step_session.bearer.verified:
        raise AccountError("Account already verified.", 403)
    two_step_session.validate()
    await two_step_session.check_code(request, request.form.get("code"))
    two_step_session.bearer.verified = True
    await two_step_session.bearer.save(update_fields=["verified"])
    return two_step_session


def requires_two_step_verification():
    """
    Validates a two-step verification attempt.

    Example:
        This method is not called directly and instead used as a decorator:

            @app.post("api/verification/attempt")
            @requires_two_step_verification()
            async def on_verified(request, two_step_session):
                response = json("Two-step verification attempt successful!", two_step_session.json())
                return response

    Raises:
        NotFoundError
        JWTDecodeError
        DeletedError
        ExpiredError
        DeactivatedError
        UnrecognisedLocationError
        ChallengeError
        MaxedOutChallengeError
    """

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(request, *args, **kwargs):
            two_step_session = await two_step_verification(request)
            return await func(request, two_step_session, *args, **kwargs)

        return wrapped

    return wrapper
