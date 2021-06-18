<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Downloads](https://pepy.tech/badge/sanic-security)](https://pepy.tech/project/sanic-security)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h3 align="center">Sanic Security</h3>

  <p align="center">
   A powerful, simple, and async security library for Sanic.
    <br />
    <a href="http://security.sunsetdeveloper.com/">Documentation</a>
    ·
    <a href="https://github.com/sunset-developer/sanic-security/issues">Report Bug</a>
    ·
    <a href="https://github.com/sunset-developer/asyncauth/pulls">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
    * [Initial Setup](#initial-setup)
    * [Authentication](#authentication)
    * [Recovery](#account-recovery)
    * [Captcha](#captcha)
    * [Two Step Verification](#two-step-verification)
    * [Authorization](#authorization)
    * [Error Handling](#error-handling)
    * [Middleware](#Middleware)
    * [Blueprints](#Blueprints)
    * [Testing](#Testing)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgements](#acknowledgements)



<!-- ABOUT THE PROJECT -->
## About The Project

Sanic Security is an authentication and authorization library made easy, designed for use with [Sanic](https://github.com/huge-success/sanic).
This library is intended to be easy, convenient, and contains a variety of features:


* Easy login and registering
* Captcha
* SMS and email verification
* JWT
* Password recovery
* Wildcard permissions
* Role permissions
* Easy database integration
* Blueprints
* Completely async

This repository has been starred by Sanic's core maintainer:

![alt text](https://github.com/sunset-developer/asyncauth/blob/master/images/ahopkins.png)

<!-- GETTING STARTED -->
## Getting Started

In order to get started, please install pip.

### Prerequisites

* pip
```sh
sudo apt-get install python3-pip
```


### Installation

* Install pip packages
```sh
pip3 install sanic-security
```


## Usage

Once Sanic Security is configured and good to go, implementing is easy as pie.

### Initial Setup

Familiarity with [Sanic](https://github.com/huge-success/sanic) and [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/index.html)
is recommended.

First you have to create a configuration file called security.ini in the project directory. Make sure Python's 
working directory is the project directory. Below is an example of its contents: 

WARNING: You must set a custom secret or you will compromise your encoded sessions.

```ini
[SECURITY]
name=ExampleProject
secret=05jF8cSMAdjlXcXeS2ZJUHg7Tbyu
captcha_font=source-sans-pro.light.ttf

[TORTOISE]
username=admin
password=8UVbijLUGYfUtItAi
endpoint=example.cweAenuBY6b.us-north-1.rds.amazonaws.com
schema=exampleschema
models=sanic_security.core.models, example.core.models
engine=mysql
generate=true

[TWILIO]
from=12058469963
token=1bcioi878ygO8fi766Fb34750e82a5ab
sid=AC6156Jg67OOYe75c26dgtoTICifIe51cbf

[SMTP]
host=smtp.gmail.com
port=465
from=test@gmail.com
username=test@gmail.com
password=wfrfouwiurhwlnj
tls=true
start_tls=false
```

You may remove each section in the configuration you aren't using. For example, if you're not utilizing Twillio you can
delete the TWILLIO section.

Once you've configured Sanic Security, you can initialize Sanic with the example below:

```python
initialize_security(app)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```


All request bodies must be sent as `form-data`. For my below examples, I use my own custom json method:

```python
from sanic.response import json as sanic_json
def json(message, content, status_code=200):
    payload = {
        'message': message,
        'code': status_code,
        'data': content
    }
    return sanic_json(payload, status=status_code)
```

## Authentication

* Registration (With all verification requirements)

Phone can be null or empty. A captcha request must be made.

Key | Value |
--- | --- |
**username** | test 
**email** | test@test.com 
**phone** | 19811354186
**password** | testpass
**captcha** | Aj8HgD

```python
@app.post('api/register')
@requires_captcha()
async def on_register(request, captcha_session):
    two_step_session = await register(request)
    await two_step_session.text_code() # Text verification code.
    await two_step_session.email_code() # Or email verification code.
    response = json('Registration successful', two_step_session.account.json())
    two_step_session.encode(response)
    return response
```

* Registration (Without verification requirements)

Phone can be null or empty.

Key | Value |
--- | --- |
**username** | test 
**email** | test@test.com 
**phone** | 19811354186
**password** | testpass

```python
@app.post('api/register')
async def on_register(request):
    account = await register(request, verified=True)
    return json('Registration Successful!', account.json())
```

* Login

Key | Value |
--- | --- |
**email** | test@test.com
**password** | testpass

```python
@app.post('api/login')
async def on_login(request):
    authentication_session = await login(request)
    response = json('Login successful!', authentication_session.account.json())
    authentication_session.encode(response)
    return response
```

* Logout

```python
@app.post('api/logout')
async def on_logout(request):
    authentication_session = await logout(request)
    response = json('Logout successful', authentication_session.account.json())
    return response
```

* Requires Authentication

```python
@app.get('api/client/authenticate')
@requires_authentication()
async def on_authenticated(request, authentication_session):
    return json('Hello ' + authentication_session.account.username + '! You are now authenticated.', 
                authentication_session.account.json())
```

## Account Recovery

* Recovery Attempt

Key | Value |
--- | --- |
**email** | test@test.com
**captcha** | Aj8HgD

```python
@app.post('api/recovery/attempt')
@requires_captcha()
async def on_recovery_attempt(request, captcha_session):
    two_step_session = await attempt_account_recovery(request)
    await two_step_session.text_code() # Text verification code.
    await two_step_session.email_code() # Or email verification code.
    response = json('A recovery attempt has been made, please verify account ownership.', two_step_session.json())
    two_step_session.encode(response)
    return response
```

* Recovery Fulfill

Key | Value |
--- | --- |
**code** | G8ha9nVa
**password** | newpass

```python
@app.post('api/recovery/fulfill')
@requires_two_step_verification()
async def on_recovery_fulfill(request, two_step_session):
    await fulfill_account_recovery_attempt(request, two_step_session)
    return json('Account recovered successfully.', two_step_session.account.json())
```


## Captcha

You must download a .ttf font for captcha challenges and define the file's path in security.ini.

[1001 Free Fonts](https://www.1001fonts.com/)

[Recommended Font](https://www.1001fonts.com/source-sans-pro-font.html)

Captcha challenge example:

![alt text](https://github.com/sunset-developer/asyncauth/blob/master/images/captcha.png)

* Request Captcha

```python
@app.get('api/captcha')
async def on_request_captcha(request):
    captcha_session = await request_captcha(request)
    response = json('Captcha request successful!', captcha_session.json())
    captcha_session.encode(response)
    return response
```

* Captcha Image

```python
@app.get('api/captcha/img')
async def on_captcha_img(request):
    captcha_session = await CaptchaSession().decode(request)
    return await file(captcha_session.get_image())
```

* Requires Captcha

Key | Value |
--- | --- |
**captcha** | Aj8HgD

```python
@app.post('api/captcha/attempt')
@requires_captcha()
async def on_captcha_attempt(request, captcha_session):
    response = json('Your captcha attempt was correct!', captcha_session.json())
    return response
```

## Two-Step Verification

* Request 2SV (Creates and encodes a code, useful for when a two-step session may be 
  invalid or expired.)

```python
@app.get('api/verification/request')
@requires_captcha()
async def on_request_verification(request, captcha_session):
    two_step_session =  await request_two_step_verification(request)
    await two_step_session.text_code() # Text verification code.
    await two_step_session.email_code() # Or email verification code.
    response = json('Verification request successful', two_step_session.json())
    two_step_session.encode(response)
    return response
```

* Resend 2SV Code (Does not create new code, only resends encoded session code.)

```python
@app.post('api/verification/resend')
async def on_resend_verification(request):
    two_step_session = await TwoStepSession().decode(request)
    await two_step_session.text_code() # Text verification code.
    await two_step_session.email_code() # Or email verification code.
    return json('Verification code resend successful', two_step_session.json())
```

* Requires Two-Step Verification

Key | Value |
--- | --- |
**code** | G8ha9nVa

```python
@app.get('api/client/verify')
@requires_two_step_verification()
async def on_verified(request, two_step_session):
    return json('Hello ' + two_step_session.account.username + '! You have verified yourself and may continue. ', 
                two_step_session.account.json())
```

* Verify Account

Key | Value |
--- | --- |
**code** | G8ha9nVae

```python
@app.post('api/verification/account')
@requires_two_step_verification()
async def on_verify(request, two_step_session):
    await verify_account(two_step_session)
    return json('You have verified your account and may login!', two_step_session.json())
```

## Authorization

Sanic Security comes with two protocols for authorization: role based and wildcard based permissions.

Role-based access control (RBAC) is a policy-neutral access-control mechanism defined around roles and privileges. The components of RBAC such as role-permissions, user-role and role-role relationships make it simple to perform user assignments. 

Wildcard permissions support the concept of multiple levels or parts. For example, you could grant a user the permission
`printer:query`. The colon in this example is a special character used to delimit the next part in the permission string. In this example, the first part is the domain that is being operated on (printer), and the second part is the action (query) being performed. 
This concept was inspired by [Apache Shiro's](https://shiro.apache.org/static/1.7.1/apidocs/org/apache/shiro/authz/permission/WildcardPermission.html) implementation of wildcard based permissions.

Examples of wildcard permissions are:

  ```
  admin:add,update,delete
  admin:add
  admin:*
  employee:add,delete
  employee:delete
  employee:*
  ```

* Require Permissions

```python
@app.post('api/account/update')
@require_permissions('admin:update', 'employee:add')
async def on_require_perms(request, authentication_session):
    return text('Admin successfully updated account!')
```

* Require Roles

```python
@app.get('api/dashboard/admin')
@require_roles('Admin', 'Moderator')
async def on_require_roles(request, authentication_session):
    return text('Admin gained access!')
```

## Error Handling

```python
@app.exception(SecurityError)
async def on_error(request, exception):
    return exception.response
```

## Middleware

```python
@app.middleware('response')
async def xxs_middleware(request, response):
    xss_prevention_middleware(request, response)


@app.middleware('request')
async def https_middleware(request):
    return https_redirect_middleware(request)
```

## Blueprints

Sanic Security blueprints contain endpoints that allow you to employ fundamental authentication and verification into your application with a
single line of code. 

Blueprints are available for production and testing purposes.

* Implementation

```python
# Blueprint containing all security endpoints.
app.blueprint(security)

"""
Below are blueprints containing endpoints only related to authentication and captcha verification.
You may need to create your own endpoints in some instances if you choose to only use specific blueprints.
For example, when the account is registered via the register endpoint in the authenticaton blueprint, you need to
create an endpoint for verifying the account as one is not available in either of the implemented blueprints below.
"""
app.blueprint(authentication)
app.blueprint(captcha)
```

* Live Endpoints

Method | Endpoint | Info |
--- | --- | --- |
POST | api/auth/register | A captcha is required. Register an account with an email, username, and password. Once the account is created successfully, a two-step session is requested and the code is emailed.
POST | api/auth/login | Login with an email and password.
POST | api/auth/verify | Verify account with a two-step session code found in email.
POST | api/auth/logout | Logout of logged in account.
POST | api/verif/request | A captcha is required. Request new two-step session and send email with code. Used if existing session is invalid or expired.
POST | api/verif/resend | Resend existing two-step session code if lost.
POST | api/recov/request | A captcha is required. Requests new two-step session to ensure current recovery attempt is being made by account owner.
POST | api/recov/fulfill | Changes an account's password once recovery attempt was determined to have been made by account owner with two-step code found in email.
POST | api/capt/request | Requests new captcha session.
GET | api/capt/img | Retrieves captcha image from existing captcha session.

* Testing Endpoints

Method | Endpoint | Info |
--- | --- | --- |
POST | api/test/auth/register | Register an account with an email, username, and password. Once the account is created successfully, a two-step session is requested and the code is emailed.
POST | api/test/auth/login | Login with an email and password.
POST | api/test/auth/verify | Verify account with a two-step session code found in email.
POST | api/test/auth/logout | Logout of logged in account.
POST | api/test/verif/request | Request new two-step session and send email with code. Used if existing session is invalid or expired.
POST | api/test/verif/resend | Resend existing two-step session code if lost.
POST | api/test/recov/request | Requests new two-step session to ensure current recovery attempt is being made by account owner.
POST | api/test/recov/fulfill | Changes an account's password once recovery attempt was determined to have been made by account owner with two-step code found in email.
POST | api/test/capt/request | Requests new captcha session.
POST | api/test/capt/img | Retrieves captcha image from existing captcha session.
POST | api/test/capt/fulfill | Data retrieval example with captcha verification.
GET | api/test/capt/img | Retrieves captcha image from existing captcha session.
POST | api/test/auth/roles |  Creates 'Admin' and 'Mod' roles to be used for testing role based authorization.
GET | api/test/auth/roles |  Data retrieval example with role authorization access.
POST | api/test/auth/perms |  Creates 'Admin' and 'Mod' roles to be used for testing role based authorization.
GET | api/test/auth/perms |  Data retrieval example with wildcard authorization access.


<!-- ROADMAP -->
## Roadmap

Keep up with Sanic Security's [Trello](https://trello.com/b/aRKzFlRL/amy-rose) board for a list of proposed features, known issues, and in progress development.


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements 

* [thewchan](https://github.com/thewchan) added a MANIFEST.in to make packaging to conda-forge possible.


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/sunset-developer/sanic-security.svg?style=flat-square
[contributors-url]: https://github.com/sunset-developer/sanic-security/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/sunset-developer/sanic-security.svg?style=flat-square
[forks-url]: https://github.com/sunset-developer/sanic-security/network/members
[stars-shield]: https://img.shields.io/github/stars/sunset-developer/sanic-security.svg?style=flat-square
[stars-url]: https://github.com/sunset-developer/sanic-security/stargazers
[issues-shield]: https://img.shields.io/github/issues/sunset-developer/sanic-security.svg?style=flat-square
[issues-url]: https://github.com/sunset-developer/sanic-security/issues
[license-shield]: https://img.shields.io/github/license/sunset-developer/sanic-security.svg?style=flat-square
[license-url]: https://github.com/sunset-developer/sanic-security/blob/master/LICENSE
