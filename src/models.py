# -*- coding: utf-8 -*-
import datetime
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class Profile(ndb.Model):
    """docstring for Profile"""

    status = ndb.BooleanProperty()
    account_type = ndb.StringProperty()
    date_joined = ndb.DateTimeProperty(auto_now_add=True)
    date_last_updated = ndb.DateTimeProperty(auto_now=True)

    account_id = ndb.StringProperty()
    account_name = ndb.StringProperty()
    access_token = ndb.StringProperty()
    country = ndb.StringProperty()
    #protray = ndb.BlobProperty()
    protray = ndb.StringProperty()
    email = ndb.StringProperty()
    birthday = ndb.DateProperty()
    gender = ndb.StringProperty()
    url = ndb.StringProperty()


class Report(polymodel.PolyModel):
    """docstring for Profile"""

    report_name = ndb.StringProperty()
    report_type = ndb.StringProperty()
    source = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_last_updated = ndb.DateTimeProperty(auto_now=True)
    side_effect = ndb.StringProperty(repeated=True)  # One pill may cause multiple side-effect
    overall_condition = ndb.StringProperty()
    target = ndb.StringProperty()
    dosage = ndb.StringProperty()
    tool_strength = ndb.StringProperty()
    data = ndb.IntegerProperty()


class SideEffect(ndb.Model):
    name = ndb.StringProperty()

    @classmethod
    def query_sideeffect(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)


class Medicine(ndb.Model):
    """docstring for Profile"""

    medicine_name = ndb.StringProperty()
    medicine_source = ndb.StringProperty()  # A company name
    medicine_packing_image = ndb.BlobProperty()
    medicine_side_effect = ndb.StructuredProperty(SideEffect)

    @classmethod
    def query_medicine(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)


class Tool(ndb.Model):
    """docstring for Profile"""

    tool_name = ndb.StringProperty()
    tool_source = ndb.StringProperty()  # A company name
    tool_packing_image = ndb.BlobProperty()
    tool_side_effect = ndb.StructuredProperty(SideEffect)


class CheckList(ndb.Model):
    """docstring for Profile"""

    check_name = ndb.StringProperty()


class Social(polymodel.PolyModel):
    """docstring for Profile"""

    follower = ndb.StringProperty(repeated=True)
    display = ndb.BooleanProperty(default=False)


class Message(Social):
    """docstring for Profile"""

    mesg_date_created = ndb.DateTimeProperty(auto_now_add=True)
    mesg_from = ndb.StringProperty()
    mesg_to = ndb.StringProperty()
    mesg = ndb.TextProperty()


class User(ndb.Model):
    """使用者資訊。此為最主要的 Kind 由此延伸到使用者其他的Kinds，例如：Profile, Report 和 Social"""

    name = ndb.StringProperty()
    profile = ndb.StructuredProperty(Profile)
    report = ndb.StructuredProperty(Report)
    social = ndb.StructuredProperty(Social)

    @classmethod
    def AddFacebookUser(cls, fb_user_profile, fb_user_protray, access_token, user_key_name):
        logging.info('Adding new facebook user.')
        user_profile = Profile()
        user_profile.account_type = 'facebook'
        user_profile.account_id = str(fb_user_profile["id"])
        user_profile.account_name = fb_user_profile["name"]

        user_profile.access_token = ''.join(access_token)
        user_profile.birthday = datetime.datetime.strptime(fb_user_profile["birthday"], '%m/%d/%Y')
        user_profile.email = fb_user_profile["email"]
        user_profile.gender = fb_user_profile["gender"]
        user_profile.protray = fb_user_protray["picture"]["data"]["url"]
        user_profile.url = fb_user_profile["link"]

        user = User(id=user_key_name)
        user.name = fb_user_profile["name"]
        user.profile = user_profile
        user.put()
