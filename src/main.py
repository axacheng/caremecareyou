# -*- coding: utf-8 -*-


import csv
import datetime
import facebookoauth as foauth
import gviz_api
import json
import logging
import models
import os
import time
import webapp2
import weibo_oauth_v2

from google.appengine.ext import ndb
from google.appengine.api import users

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required


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
    weibo_cookie = weibo_oauth_v2.parse_cookie(self.request.cookies.get("weibo_user"))
    if weibo_cookie:
        weibo_user_id = weibo_cookie
        weibo_user_ancestor = weibo_oauth_v2.WeiboUser.get_by_key_name(weibo_user_id)
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

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_dict))


class ShowNdbKinds(webapp2.RequestHandler):
    def get(self):
        medicine_ancestor_key = ndb.Key("Medicine", "medicine")
        ctx = ndb.get_context()
        ctx_key = ctx.set_cache_policy(medicine_ancestor_key)

        logging.info('Context cache: %s', ctx.get(ctx_key))

        all_medicine = models.Medicine.query_medicine(medicine_ancestor_key)
        total_medicine_count = all_medicine.count()

        sideeffect_ancestor_key = ndb.Key("SideEffect", "sideeffect")
        all_sideeffect = models.SideEffect.query_sideeffect(sideeffect_ancestor_key)
        total_sideeffect_count = all_sideeffect.count()

        template_dict = {'total_medicine_count': total_medicine_count,
                         'total_sideeffect_count': total_sideeffect_count}

        path = os.path.join(os.path.dirname(__file__), 'backend_data.html')
        self.response.out.write(template.render(path, template_dict))


class UploadData(webapp2.RequestHandler):
    def get(self):
        ancestor_key = ndb.Key("Medicine", "medicine")
        all_side_effect = models.Medicine.query_medicine(ancestor_key)
        total_count = all_side_effect.count()

        path = os.path.join(os.path.dirname(__file__), 'upload.html')
        if all_side_effect is None:
            self.response.out.write('No data')
        else:
            self.response.out.write(template.render(
                                    path, {'all_side_effect': all_side_effect,
                                           'total_count': total_count}))

    def post(self):
        uploaded_file = csv.reader(self.request.get('csv'))
        for side_effect_name in uploaded_file:
            if side_effect_name:
                side_effect = models.SideEffect(parent=ndb.Key('SideEffect', 'sideeffect'),
                                                name=''.join(side_effect_name),)
                #side_effect = models.Disease(parent=ndb.Key('Disease', 'disease_name'),
                #                             name=''.join(side_effect_name),)
                #side_effect = models.Medicine(parent=ndb.Key('Medicine', 'medicine'),
                #                              medicine_name=''.join(side_effect_name),)
                side_effect.put()
        self.redirect('/upload')


class DeleteData(webapp2.RequestHandler):
    def get(self):
        ancestor_key = ndb.Key("SideEffect", "sideeffect")
        all_side_effect = models.SideEffect.query_sideeffect(ancestor_key).fetch()
        #ancestor_key = ndb.Key("Medicine", "medicine")
        #all_side_effect = models.Medicine.query_medicine(ancestor_key).fetch()

        for i in all_side_effect:
            entity_key = i.key  # Key, looks like: Key('SideEffect', 'sideeffect', 'SideEffect', 5633)
            entity_key.delete()

        self.response.out.write(entity_key)

class MockData(webapp2.RequestHandler):
    """docstring for MockData"""
    def get(self):
        fb_user_profile = {'id': '123456', 'name': 'Axa', 'email': 'axa.cheng@gmail.com',
                            'gender': 'Male', 'birthday': '06/07/1980',
                            'link': 'https://graph.facebook.com/axa.cheng/picture'}
        fb_user_protray = ''
        access_token = ['this is access_token']
        user_key_name = str(fb_user_profile["id"] + '_facebook')

        models.User.AddFacebookUser(fb_user_profile, fb_user_protray,
                                    access_token, user_key_name)
        self.redirect('/myrecord')



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

        # This user_entity returns format as below:
        """ User(key=Key('User', '692733281_facebook'), name=u'Axa Cheng',
            profile=Profile(access_token=u'AAACAOZBeeoLWxqkE3qkAadezcqWVANRdegZDZD',
            account_id=u'692733281', account_name=u'Axa Cheng', account_type=u'facebook',
            birthday=datetime.date(1980, 6, 7), country=None,
            date_joined=datetime.datetime(2012, 8, 10, 17, 28, 8, 671160),
            date_last_updated=datetime.datetime(2012, 8, 10, 17, 28, 8, 670910),
            email=u'axa.cheng@gmail.com', gender=u'male',
            protray=u'https://graph.facebook.com/axa.cheng/picture', status=None,
            url=u'http://www.facebook.com/axa.cheng'), report=None, social=None)
        """
        #user_protray = user_entity.profile.protray
        user_protray = ''  # Mock up, PLEASE delete this line before deploy.
        ancestor_key = ndb.Key("Report", username)
        my_reports = models.Report.query_personal_report(ancestor_key)
        logging.info('xxxx %s' % my_reports.fetch())


        chart_data_template = []
        for data in my_reports.fetch():
            # Data 
            chart_data = {}
            chart_data['time'] = data.date_created
            medicine_and_dosage_data = zip(data.medicine, map(int, data.dosage))
            # Merge two dicts into chart_data, less more readable but faster.
            # http://stackoverflow.com/questions/38987/how-can-i-merge-union-two-python-dictionaries-in-a-single-expression
            chart_data_template.append( dict(chart_data, **(dict(medicine_and_dosage_data))) )

        logging.info('Oooooooout %s' % chart_data_template)


        # schema = { 'time': ("datetime", "Time"),
        #            '67638': ("number", 'A medicine'),
        #            '774': ("number", 'B medicine')}
        #chart_schema = {'time': ("datetime", "Time")}

        # for j in data.medicine:
        #     chart_schema[j] = ("number", j)

        # logging.info('sssssss %s' % chart_schema)


        #https://developers.google.com/appengine/docs/python/ndb/keyclass?hl=zh-tw
        #my_key = my_reports.get()
        #logging.info('099999999 %s ' % my_key.key.parent())
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        template_dict = {'username': username,
                         'my_reports': my_reports,
                         'today': today, 'user_protray': user_protray}

        path = os.path.join(os.path.dirname(__file__), 'myrecord-beta.html')
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

        populate_data['disease_name'] = terms[0]
        populate_data['medicine'] = terms[1]
        populate_data['side_effect'] = terms[2]
        #logging.info('Adding one report: %s' % populate_data)
        report = models.Report(parent = ndb.Key('Report', username),  # Axa@faceboo_report
                               disease_name = populate_data['disease_name'],
                               report_type = 'TBD',
                               source = 'TBD',
                               date_created = recorded_date,
                               side_effect = map(lambda x: x.strip(), populate_data['side_effect'].split(',')),
                               medicine = map(lambda x: x.strip(), populate_data['medicine'].split(',')),
                               minding = 'TBD',
                               target = 'TBD',
                               dosage = ['5', '5', '10', '8', '3', '1'],
                               tool_strength = 'TBD',
                               data = 'TBD')
        this_key = report.put()
        logging.info('User:[ %s ] added one report - %s' % (username, this_key))
        self.redirect('/myrecord')



########## Testing code ############
class testShowChartJson(webapp2.RequestHandler):
    def get(self):

        data = [ { '67638': 3, '774': 5, 'time': datetime.datetime(2012, 06, 10, 12, 31, 0)}, 
                 { '67638': 30, '774': 5, '8273223': 10, 'time': datetime.datetime(2012, 06, 20, 12, 32, 0)}, 
                 { 'time': datetime.datetime(2012, 07, 15, 12, 33, 0), '774': 10, '8273223': 10 },
                 { 'time': datetime.datetime(2012, 07, 16, 12, 33, 0), '67638': 5, '8273223': 10 },

               ]

        schema = { 'time': ("datetime", "Time"),
                   '67638': ("number", 'A medicine'),
                   '774': ("number", 'B medicine'),
                   '8273223': ("number", 'C medicine') }


        data_table = gviz_api.DataTable(schema)
        data_table.LoadData(data)
        response = data_table.ToJSonResponse(columns_order=("time", "67638", "774", "8273223"),
                                             order_by="time")
        self.response.out.write(response)


class testShowChart(webapp2.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), 'test/showchart.html')
        self.response.out.write(template.render(path, ''))


app = webapp2.WSGIApplication([('/', MainPage),
                                ('/add_report', AddReport),
                                ('/backend_data', ShowNdbKinds),
                                ('/delete', DeleteData),
                                ('/mockdata', MockData),
                                ('/myrecord', MyRecord),
                                ('/oauth/facebook_login', foauth.LoginHandler),
                                ('/oauth/facebook_logout', foauth.LogoutHandler),
                                ('/oauth/weibo_login', weibo_oauth_v2.LoginHandler),
                                ('/oauth/weibo_logout', weibo_oauth_v2.LogoutHandler),
                                ('/search_disease/', SearchDisease),
                                ('/search_medicine/', SearchMedicine),
                                ('/search_side_effect/', SearchSideEffect),
                                ('/upload', UploadData),
                                ########### Test handlers in below ###########
                                ('/showchartjson', testShowChartJson),
                                ('/showchart', testShowChart),
                               ],
                                debug=True)
