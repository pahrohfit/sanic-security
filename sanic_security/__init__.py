from sanic import Sanic
from sanic.log import logger
from sanic_ext.extensions.base import Extension
from sanic_ext import Extend

from sanic_security.configuration import Config as sanic_security_config


class SanicSecurityExtension(Extension):
    logger.info("Setting up SanicSecurityExtension")
    name: str = "security"
    extension_name = app_attribute = 'security'
    app: Sanic = None

    account: object = None
    session: object = None
    role: object = None
    verification_session: object = None
    twostep_session: object = None
    captcha_session: object = None
    authentication_session: object = None
    orm = None
    _started = False

    def __init__(self, app: Sanic = None, orm = None, account: object = None, session: object = None,
                 role: object = None, verification: object = None,
                 twostep: object = None, captcha: object = None,
                 authentication: object = None):

        logger.info(f"provided app: {app}")
        logger.info(f"provided orm: {orm}")

        if app is not None:
            self.init_app(app, orm, account, session, role, verification, twostep, captcha, authentication)

    def init_app(self, app: Sanic, orm = None, account: object = None, session: object = None,
                 role: object = None, verification: object = None,
                 twostep: object = None, captcha: object = None,
                 authentication: object = None):
        """
        init_app factory
        """
        logger.info("[Sanic-Security] init_app")

        if app is None or not isinstance(app, Sanic):
            raise Exception(f"Sanic instance must be provided")

        self.app = app
        self.app.config.update(sanic_security_config())

        self.account = account if account else self.app.config.get('SANIC_SECURITY_ACCOUNT_MODEL', None)
        self.session = session if session else self.app.config.get('SANIC_SECURITY_SESSION_MODEL', None)
        self.role = role if role else self.app.config.get('SANIC_SECURITY_ROLE_MODEL', None)
        self.verification_session = verification if verification else self.app.config.get('SANIC_SECURITY_VERIFICATION_MODEL', None)
        self.twostep_session = twostep if twostep else self.app.config.get('SANIC_SECURITY_TWOSTEP_MODEL', None)
        self.captcha_session = captcha if captcha else self.app.config.get('SANIC_SECURITY_CAPTCHA_MODEL', None)
        self.authentication_session = authentication if authentication else self.app.config.get('SANIC_SECURITY_AUTHENTICATION_MODEL', None)
        self.orm = orm if orm else self.app.config.get('SANIC_SECURITY_ORM', 'tortoise')
        try:
            # TODO: this is ugly as hell, but works for now
            logger.info(f"attmpeting to import sanic_security.ORM.{self.orm}")
            if self.orm == 'tortoise':
                if not self.role:
                    from .orm.tortoise import Role
                    self.role = Role()
                if not self.account:
                    from .orm.tortoise import Account
                    self.account = Account()
                if not self.verification_session:
                    from .orm.tortoise import VerificationSession
                    self.verification_session = VerificationSession()
                if not self.twostep_session:
                    from .orm.tortoise import TwoStepSession
                    self.twostep_session = TwoStepSession()
                if not self.captcha_session:
                    from .orm.tortoise import CaptchaSession
                    self.captcha_session = CaptchaSession()
                if not self.authentication_session:
                    from .orm.tortoise import AuthenticationSession
                    self.authentication_session = AuthenticationSession()
            elif self.orm == 'umongo':
                if not self.role:
                    from .orm.umongo import Role
                    self.role = Role()
                if not self.account:
                    from .orm.umongo import Account
                    self.account = Account()
                if not self.verification_session:
                    from .orm.umongo import VerificationSession
                    self.verification_session = VerificationSession()
                if not self.twostep_session:
                    from .orm.umongo import TwoStepSession
                    self.twostep_session = TwoStepSession()
                if not self.captcha_session:
                    from .orm.umongo import CaptchaSession
                    self.captcha_session = CaptchaSession()
                if not self.authentication_session:
                    from .orm.umongo import AuthenticationSession
                    self.authentication_session = AuthenticationSession()
            else:
                raise ImportError("Invalid ORM specified")
        except ImportError as e:
            logger.critical(f"No such ORM provider: {orm}")
            raise e
        
        self._register_extension(self.app)

    def label(self):
        return "Sanic-Security"

    def _register_extension(self, app):
        logger.info("Trying to register Security Extension")
        if not hasattr(app.ctx, 'extensions'):
            setattr(app.ctx, 'extensions', {})
        app.ctx.extensions[self.extension_name] = self

    def startup(self, bootstrap: Extend) -> None:
        """
        Used by sanic-ext to start up an extension
        NOT YET WORKING -- SANIC-EXT issue, not mine
        """
        logger.debug(f"Bootstrap: {dir(bootstrap)}")
