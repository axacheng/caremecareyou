#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A barebones AppEngine application that uses Facebook OAuth2.0 for login.

This application uses OAuth 2.0 directly rather than relying on Facebook's
JavaScript SDK for login. It also accesses the Facebook Graph API directly
rather than using the Python SDK. It is designed to illustrate how easy
it is to use the Facebook Platform without any third party code.

See the "appengine" directory for an example using the JavaScript SDK.
Using JavaScript is recommended if it is feasible for your application,
as it handles some complex authentication states that can only be detected
in client-side code.

This code is original wrote by martey.
I changed it a bit for customization.
http://github.com/pythonforfacebook/facebook-sdk
http://pypi.python.org/pypi/facebook-sdk/0.3.0

"""

FACEBOOK_APP_ID = "141265999345490"
FACEBOOK_APP_SECRET = "cef1e5c4107f3d2a1f7c08757a0a5fe6"

import base64
import cgi
import Cookie
import datetime
import email.utils
import hashlib
import hmac
import logging
import os.path
import time
import urllib
import wsgiref.handlers
import json
import webapp2
import models

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


class BaseHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                #self._current_user = models.Profile.get_by_key_name(user_id)
                self._current_user = models.User.query(models.User.profile.account_id == user_id).get()

        return self._current_user


class LoginHandler(BaseHandler):
    def get(self):
        verification_code = self.request.get("code")
        # We can refer below link to get additional permission from user.
        # https://developers.facebook.com/docs/authentication/permissions/
        args = dict(client_id=FACEBOOK_APP_ID,
                    redirect_uri=self.request.path_url,
                    scope='email, user_location, user_birthday')

        if self.request.get("code"):
            args["client_secret"] = FACEBOOK_APP_SECRET
            args["code"] = self.request.get("code")
            response = cgi.parse_qs(urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]

            # Download the user profile and cache a local instance of the
            # basic profile info
            #
            # (Added by Axa)
            # We can get profile information from
            # https://developers.facebook.com/tools/explorer?method=GET&path=me
            fb_user_profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))

            fb_user_protray = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?fields=picture&" +
                urllib.urlencode(dict(access_token=access_token))))

            logging.info('FB profile resful result: %s' % fb_user_profile)
            user_key_name = str(fb_user_profile["id"] + '_facebook')
            verify_user = models.User.get_by_id(user_key_name)
            logging.info('Verify user %s' % verify_user)

            if verify_user:
                logging.info('User facebook account is existing. No adding.')
                set_cookie(self.response, "fb_user", str(fb_user_profile["id"]),
                           expires=time.time() + 30 * 86400)
                self.redirect("/")
            else:
                models.User.AddFacebookUser(fb_user_profile, fb_user_protray,
                                            access_token, user_key_name)
                set_cookie(self.response, "fb_user", str(fb_user_profile["id"]),
                           expires=time.time() + 30 * 86400)
                self.redirect("/")
        else:
            self.redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "fb_user", "", expires=time.time() - 86400)
        self.redirect("/")


def set_cookie(response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain:
        cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers.add("Set-Cookie", cookie.output()[12:])


def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value:
        return None
    parts = value.split("|")
    if len(parts) != 3:
        return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()
