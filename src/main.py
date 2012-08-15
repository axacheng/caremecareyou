# -*- coding: utf-8 -*-

import datetime
import auth.facebookoauth as foauth
import auth.weibo_oauth_v2
import json
import jsonapi.drawchart
import logging
import mockup.generate_mockup
import models
import os
import time
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template


def UserLoginHandler(self):
    """ This method offers username and logout_link to MainPage().

    MainPage() would see if current uesr is logged in, or needed to log in.
    If current user shows 'no logged in', then we would provide login links to
    them which handled by AuthHandler().
    If current user is logged in, then here we provide logout link, and it'd
    being a result to template_dict['url_link']

    Two kind of account authorizations support: OpenID and Oauth2.0.
    * OpenID
      1. GAE has built-in federated support. Yahoo and Google use it.

    * Oauth2.0
      1. Facebook user: We use unofficial facebook python API - facebookoauth.py
         and changed it a bit for customization.
         http://github.com/pythonforfacebook/facebook-sdk (version 0.3.0)

         This API sets cookie(fb_user) to browser, and we use
         foauth.parse_cookie function to get it back from user's browser
         resource to identify your profile info (e.g. access_token or login
         status)

      2. Sina weibo user: Similar as Facebook python API.
         When your click Weibo login icon on our page, we will deliver your to
         weibo authentication page to get access_token by OAuth2.0.
         Once authentication flow successful then we set "weibo_user" cookie on
         user's browser. When main page loaded, we would check weibo_user cookie
         by parse_cookie method which would decode cookie format and pull Weibo
         User's ID out. More detail check:
             weibo_oauth_v2.py line 112: 'weistr(weibo_user_profile.id)'
             weibo_oauth_v2.py line 142:  set_cookie(self.response,
                                                     "weibo_user",
                                                     str(weibo_id),
        About the decode, you can check weibo_oauth_v2.py line 173
              base64.b64decode(parts[0]).strip()

        Once we got Weibo user's ID, then we use it as datastore key_name to
        fetch its value(aka: Weibo username) from screen_name column.
        Finally, we use screen_name to determine user login or not.

    Arg: xxxxx: string - fdsafdsafdsfdsafd
    Raise: 
    Return: dict: {logged in username:logout URL link}
    """
    # Check OpenID/Federated user logged in or not.
    openid_username = users.get_current_user()

    # Check Facebook user logged in or not.
    if not hasattr(self, "_current_user"):
        self._current_user = None
        user_id = foauth.parse_cookie(self.request.cookies.get("fb_user"))

        if user_id:
            self._current_user = models.User.query(models.User.profile.account_id == user_id).get()
    facebook_user = self._current_user  # Returns FacebookUser db entity

    # Check WeiBo user logged in or not.
    weibo_cookie = auth.weibo_oauth_v2.parse_cookie(self.request.cookies.get("weibo_user"))
    if weibo_cookie:
        weibo_user_id = weibo_cookie
        weibo_user_ancestor = auth.weibo_oauth_v2.WeiboUser.get_by_key_name(weibo_user_id)
        query = ndb.Query(weibo_user_ancestor)
        for name in query.fetch(1):
            weibo_screen_name = name.screen_name

        weibo_username = weibo_user_id + ':' + weibo_screen_name + ':weibo'
    else:
        weibo_username = None

    if openid_username:
        #openid_user_id = ':' + openid_username.user_id()  #1111
        openid_username = openid_username.user_id() + ':' + openid_username.email()
        #openid_username = openid_username.email().replace('@', openid_user_id)
        logging.info('%s logged in.' % openid_username)
        logout_link = users.create_logout_url(self.request.path)
        return {openid_username: logout_link}

    elif facebook_user:
        facebook_user = facebook_user.profile.account_id + ':' + facebook_user.profile.account_name + ':facebook'
        logging.info("%s logged in." % facebook_user)
        logout_link = '/oauth/facebook_logout'
        return {facebook_user: logout_link}

    elif weibo_username:
        logging.info("%s logged in." % weibo_username)
        url_link = '/oauth/weibo_logout'
        return {weibo_username: url_link}

    else:
        logging.info('We cant find username, redirect to login page.')
        return {}


class MainPage(webapp2.RequestHandler):
    def get(self):
        username = "".join(UserLoginHandler(self).keys())
        logout_link = "".join(UserLoginHandler(self).values())

        if username:
            username = username
            url_link = logout_link
            url_text = '登出'
            login_status = True
        else:
            url_link = users.create_login_url(self.request.path)
            url_text = '請先登入'
            login_status = None

        # Compile all the 'key' to template_dict and pass them to index.html
        # This url_link could be logout_link or login_link depends on whether
        # username exist or not. If it's exist then url_link is logout_link,
        # vice versa.
        template_dict = {'username': username, 'url_link': url_link, 'url_text': url_text,
                         'login_status': login_status}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_dict))



class MyRecord(webapp2.RequestHandler):
    """docstring for MyRecord"""
    # def to_dict(self):
    #   """Covert datastore entities from python object to python dictionary"""
    #    return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def get(self):
        #username = ''.join(UserLoginHandler(self).keys())
        username = '123456:[[[[[[[[[ TEST ]]]]]]]]:facebook'  # Mocks/please remove after testing
        user_id = username.split(':')[0] + '_' + username.split(':')[2]

        #user_entity = models.User.get_by_id(user_id).to_dict()
        user_entity = models.User.get_by_id(user_id)

        #user_protray = ''  # Mock up, PLEASE delete this line before deploy.
        user_protray = user_entity.profile.protray
        ancestor_key = ndb.Key("Report", username)
        my_reports = models.Report.query_personal_report(ancestor_key)
        logging.info('All user\'s Report %s' % my_reports.fetch())

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        template_dict = {'username': username,
                         'my_reports': my_reports,
                         'today': today, 'user_protray': user_protray}

        path = os.path.join(os.path.dirname(__file__), 'templates/myrecord-beta.html')
        self.response.out.write(template.render(path, template_dict))



class SearchDisease(webapp2.RequestHandler):
    def get(self):
        disease_result = []
        search_word = self.request.get('term')
        all_disease = models.Disease.query(models.Disease.name >= unicode(search_word.capitalize()))
        result = all_disease.fetch(50)
        # query.filter("Display", True)
        # query.filter("Word >=", unicode(search_word))
        # query.filter("Word <", unicode(search_word) + u'\ufffd')

        if result:
            for disease in result:
                disease_result.append(disease.name)

            self.response.out.write(json.dumps(disease_result))


class SearchMedicine(webapp2.RequestHandler):
    def get(self):
        medicine_result = []
        search_word = self.request.get('term')
        all_medicine = models.Medicine.query(models.Medicine.medicine_name >= unicode(search_word.capitalize()))
        result = all_medicine.fetch(10)

        if result:
            for medicine in result:
                medicine_result.append(medicine.medicine_name)

            self.response.out.write(json.dumps(medicine_result))


class SearchSideEffect(webapp2.RequestHandler):
    def get(self):
        side_effect_result = []
        search_word = self.request.get('term')
        all_side_effect = models.SideEffect.query(models.SideEffect.name >= unicode(search_word))
        result = all_side_effect.fetch(10)

        if result:
            for side_effect in result:
                side_effect_result.append(side_effect.name)

            self.response.out.write(json.dumps(side_effect_result))


class AddReport(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Oops ~ you can not do it.')

    def post(self):
        username = ''.join(UserLoginHandler(self).keys())
        username = '123456:[[[[[[[[[ TEST ]]]]]]]]:facebook'  # Mocks
        populate_data = {'disease_name': '', 'medicine': '', 'side_effect': ''}
        terms = self.request.get_all('term')
        fetched_report_date = self.request.get_all('report_date')  # [u'2012-08-31']
        recorded_date = datetime.datetime(*time.strptime(''.join(fetched_report_date).encode('utf-8'), "%Y-%m-%d")[0:5])

        logging.info
        populate_data['disease_name'] = terms[0]
        populate_data['medicine'] = terms[1].rstrip(', ')
        populate_data['side_effect'] = terms[2].rstrip(', ')

        models.Report.AddMedicineReport(username, populate_data, recorded_date)
        self.redirect('/myrecord')


app = webapp2.WSGIApplication([('/', MainPage),
                                ('/add_report', AddReport),
                                ('/myrecord', MyRecord),
                                ('/oauth/facebook_login', foauth.LoginHandler),
                                ('/oauth/facebook_logout', foauth.LogoutHandler),
                                ('/oauth/weibo_login', auth.weibo_oauth_v2.LoginHandler),
                                ('/oauth/weibo_logout', auth.weibo_oauth_v2.LogoutHandler),
                                ('/search_disease/', SearchDisease),
                                ('/search_medicine/', SearchMedicine),
                                ('/search_side_effect/', SearchSideEffect),
                                ('/upload', mockup.generate_mockup.UploadData),
                                ('/delete', mockup.generate_mockup.DeleteData),

                                ########### Draw Chart Handlers ###########
                                ('/showchartjson', jsonapi.drawchart.ShowMedicineTakenChartJson),
                                ('/showchart', jsonapi.drawchart.ShowChart),
                               ],
                                debug=True)
