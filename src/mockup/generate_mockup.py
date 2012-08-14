# -*- coding: utf-8 -*-

import csv
import models
import os
import webapp2

from google.appengine.ext import ndb


class UploadData(webapp2.RequestHandler):
    def get(self):
        ancestor_key = ndb.Key("Medicine", "medicine")
        all_side_effect = models.Medicine.query_medicine(ancestor_key)
        total_count = all_side_effect.count()

        path = os.path.join(os.path.dirname(__file__), 'templates/upload.html')
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