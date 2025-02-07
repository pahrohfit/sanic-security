from os import environ

from sanic.utils import str_to_bool
from sanic import Sanic
from sanic.log import logger


"""
An effective, simple, and async security library for the Sanic framework.
Copyright (C) 2020-present Aidan Stewart

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


DEFAULT_CONFIG = {
    "SANIC_SECURITY_SECRET": "This is a big secret. Shhhhh",
    "SANIC_SECURITY_PUBLIC_SECRET": None,
    "SANIC_SECURITY_SESSION_SAMESITE": "strict",
    "SANIC_SECURITY_SESSION_SECURE": True,
    "SANIC_SECURITY_SESSION_HTTPONLY": True,
    "SANIC_SECURITY_SESSION_DOMAIN": None,
    "SANIC_SECURITY_SESSION_EXPIRES_ON_CLIENT": False,
    "SANIC_SECURITY_SESSION_PREFIX": "token",
    "SANIC_SECURITY_SESSION_ENCODING_ALGORITHM": "HS256",
    "SANIC_SECURITY_MAX_CHALLENGE_ATTEMPTS": 5,
    "SANIC_SECURITY_CAPTCHA_SESSION_EXPIRATION": 60,
    "SANIC_SECURITY_CAPTCHA_FONT": "captcha.ttf",
    "SANIC_SECURITY_TWO_STEP_SESSION_EXPIRATION": 200,
    "SANIC_SECURITY_AUTHENTICATION_SESSION_EXPIRATION": 2592000,
    "SANIC_SECURITY_AUTHENTICATION_SESSION_REFRESH": True,
    "SANIC_SECURITY_ALLOW_LOGIN_WITH_USERNAME": False,
    "SANIC_SECURITY_INITIAL_ADMIN_EMAIL": "admin@example.com",
    "SANIC_SECURITY_INITIAL_ADMIN_PASSWORD": "admin123",
    "SANIC_SECURITY_INITIAL_ADMIN_PHONE": "1111111111",
    "SANIC_SECURITY_TEST_DATABASE_URL": "sqlite://:memory:",
    "SANIC_SECURITY_ORM": 'tortoise', # Currently supports ['tortoise', 'umongo']
    "SANIC_SECURITY_ACCOUNT": None,
    "SANIC_SECURITY_SESSION": None,
    "SANIC_SECURITY_ROLE": None,
    "SANIC_SECURITY_VERIFICATION_MODEL": None,
    "SANIC_SECURITY_TWOSTEP_MODEL": None,
    "SANIC_SECURITY_CAPTCHA_MODEL": None,
    "SANIC_SECURITY_AUTHENTICATION_MODEL": None,
}


class Config(dict):
    """
    Sanic Security configuration.

    Attributes:
        SANIC_SECURITY_SECRET (str): The secret used by the hashing algorithm for generating and signing JWTs. This should be a string unique to your application. Keep it safe.
        SANIC_SECURITY_PUBLIC_SECRET (str): The secret used for verifying and decoding JWTs and can be publicly shared. This should be a string unique to your application.
        SANIC_SECURITY_SESSION_SAMESITE (str): The SameSite attribute of session cookies.
        SANIC_SECURITY_SESSION_SECURE (bool): The Secure attribute of session cookies.
        SANIC_SECURITY_SESSION_HTTPONLY (bool): The HttpOnly attribute of session cookies. HIGHLY recommended that you do not turn this off, unless you know what you are doing.
        SANIC_SECURITY_SESSION_DOMAIN (bool): The Domain attribute of session cookies.
        SANIC_SECURITY_SESSION_EXPIRES_ON_CLIENT: When true, session cookies are removed from the clients browser when the session expires.
        SANIC_SECURITY_SESSION_ENCODING_ALGORITHM (str): The algorithm used to encode sessions to a JWT.
        SANIC_SECURITY_SESSION_PREFIX (str): Prefix attached to the beginning of session cookies.
        SANIC_SECURITY_MAX_CHALLENGE_ATTEMPTS (str): The maximum amount of session challenge attempts allowed.
        SANIC_SECURITY_CAPTCHA_SESSION_EXPIRATION (int): The amount of seconds till captcha session expiration on creation. Setting to 0 will disable expiration.
        SANIC_SECURITY_CAPTCHA_FONT (str): The file path to the font being used for captcha generation.
        SANIC_SECURITY_TWO_STEP_SESSION_EXPIRATION (int):  The amount of seconds till two step session expiration on creation. Setting to 0 will disable expiration.
        SANIC_SECURITY_AUTHENTICATION_SESSION_EXPIRATION (bool): The amount of seconds till authentication session expiration on creation. Setting to 0 will disable expiration.
        SANIC_SECURITY_AUTHENTICATION_SESSION_REFRESH (bool): A refresh token can be used to generate a new session instead of reauthenticating.
        SANIC_SECURITY_ALLOW_LOGIN_WITH_USERNAME (bool): Allows login via username and email.
        SANIC_SECURITY_INITIAL_ADMIN_EMAIL (str): Email used when creating the initial admin account.
        SANIC_SECURITY_INITIAL_ADMIN_PASSWORD (str) Password used when creating the initial admin account.
        SANIC_SECURITY_TEST_DATABASE_URL (str): Database URL for connecting to the database Sanic Security will use for testing
        SANIC_SECURITY_ORM (str): ORM to use (right now, 'tortoise', 'umongo', or 'manual')
    """

    SANIC_SECURITY_SECRET: str
    SANIC_SECURITY_PUBLIC_SECRET: str
    SANIC_SECURITY_SESSION_SAMESITE: str
    SANIC_SECURITY_SESSION_SECURE: bool
    SANIC_SECURITY_SESSION_HTTPONLY: bool
    SANIC_SECURITY_SESSION_DOMAIN: str
    SANIC_SECURITY_SESSION_EXPIRES_ON_CLIENT: bool
    SANIC_SECURITY_SESSION_ENCODING_ALGORITHM: str
    SANIC_SECURITY_SESSION_PREFIX: str
    SANIC_SECURITY_MAX_CHALLENGE_ATTEMPTS: int
    SANIC_SECURITY_CAPTCHA_SESSION_EXPIRATION: int
    SANIC_SECURITY_CAPTCHA_FONT: str
    SANIC_SECURITY_TWO_STEP_SESSION_EXPIRATION: int
    SANIC_SECURITY_AUTHENTICATION_SESSION_EXPIRATION: int
    SANIC_SECURITY_AUTHENTICATION_SESSION_REFRESH: bool
    SANIC_SECURITY_ALLOW_LOGIN_WITH_USERNAME: bool
    SANIC_SECURITY_INITIAL_ADMIN_EMAIL: str
    SANIC_SECURITY_INITIAL_ADMIN_PASSWORD: str
    SANIC_SECURITY_TEST_DATABASE_URL: str
    SANIC_SECURITY_ORM: str
    SANIC_SECURITY_ACCOUNT: str
    SANIC_SECURITY_SESSION: str
    SANIC_SECURITY_ROLE: str
    SANIC_SECURITY_VERIFICATION_MODEL: str
    SANIC_SECURITY_TWOSTEP_MODEL: str
    SANIC_SECURITY_CAPTCHA_MODEL: str
    SANIC_SECURITY_AUTHENTICATION_MODEL: str

    def load_app_variables(self, app: Sanic = None, load_env="SANIC_SECURITY_") -> None:
        """
        If we have a loaded Sanic app, read in any local config variables
        """
        try:
            if not app:
                app = Sanic.get_app()
        except:
            logger.debug('SANIC-SECURITY No Sanic App provided -- skipping load of Sanic variables')
            return
        logger.debug('SANIC-SECURITY Sanic App provided -- loading Sanic variables')
        
        for key, value in app.config.items():
            if not key.startswith(load_env):
                continue

            logger.debug(f'SANIC-SECURITY Found App Config Variable: {key}')

            # Support unsetting values
            if not value:
                self[key] = value
                continue

            for converter in (int, float, str_to_bool, str):
                try:
                    if [key]:
                        self[key] = converter(value)
                        break
                except ValueError:
                    pass
    

    def load_environment_variables(self, load_env="SANIC_SECURITY_") -> None:
        """
        Any environment variables defined with the prefix argument will be applied to the config.

        Args:
            load_env (str): Prefix being used to apply environment variables into the config.
        """
        for key, value in environ.items():
            if not key.startswith(load_env):
                continue

            # Support unsetting values
            if not value:
                self[key] = value
                continue

            for converter in (int, float, str_to_bool, str):
                try:
                    self[key] = converter(value)
                    break
                except ValueError:
                    pass

    def __init__(self):
        super().__init__(DEFAULT_CONFIG)
        self.__dict__ = self
        self.load_app_variables()
        self.load_environment_variables()


config = Config()
