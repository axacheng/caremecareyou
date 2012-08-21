# -*- coding: utf-8 -*-

import csv
import datetime
import models
import os
import time
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


class MockData(webapp2.RequestHandler):
    """docstring for MockData"""
    def get(self):
        ### Mockup User ###
        fb_user_profile = {'id': '123456', 'name': 'Axa', 'email': 'axa.cheng@gmail.com',
                            'gender': 'Male', 'birthday': '06/07/1980',
                            'link': 'https://graph.facebook.com/axa.cheng/picture'}
        fb_user_protray = ''
        access_token = ['this is access_token']
        user_key_name = str(fb_user_profile["id"] + '_facebook')

        models.User.AddFacebookUser(fb_user_profile, fb_user_protray,
                                    access_token, user_key_name)

        ### Mockup Report for medicine ###
        for dn in ['大頭症', '鼻涕丸', '高血脂']:
            if dn == '大頭症':
                date_list = ['5', '10', '15', '20', '25']
                m = 'Fecole, Zafirlukast'
                s = '手指冰冷, 上火, 頭昏, 發冷'
                d = '10, 20'

            elif dn == '鼻涕丸':
                date_list = ['3', '9', '22']
                m = 'Allegra, Anpec'
                s = '五枝無力, 牙齒痛'
                d = '5, 10'
            else:
                date_list = ['1', '4', '7', '13', '22', '27', '28', '29']
                m = 'Zocor'
                s = '睡不著, 疲累'
                d = '10'

            for i in date_list:
                if dn == '大頭症' and (i == '10' or i == '15'):
                    medicine = m
                    side_effect = s
                    dosage = d
                elif dn == '大頭症':
                    medicine = 'Eafunin, Fecole, Gaba-p'
                    side_effect = '上火, 昏沉, 無力感'
                    dosage = '10, 40, 10'
                else:
                    medicine = m
                    side_effect = s
                    dosage = d

                username = '123456:[ TEST ]:facebook'  # Mocks
                populate_data = {'disease_name': dn,
                                 'report_type': 'Medicine',
                                 'medicine': medicine,
                                 'side_effect': side_effect,
                                 'dosage': dosage}
                new_date = '2012-08-%s' % i
                recorded_date = datetime.datetime(*time.strptime(new_date, "%Y-%m-%d")[0:5])
                models.Report.AddMedicineReport(username, populate_data, recorded_date)

        ### Mockup Report for exam ###
        for dn in ['鼻涕丸', '高血脂']:
            if dn == '高血脂':
                date_list = ['10', '20', '30']
                en = 'LDL, HDH, PML/RARA, 盰指數, T細胞'
                ev = '282, 34, 66, 3, 53'
            else:
                date_list = ['1', '15', '30']
                en = '鈉, 尿中鉛, 白蛋白'
                ev = '1.6, 133 , 43'

            for i in date_list:
                username = '123456:[ TEST ]:facebook'  # Mocks
                populate_data = {'disease_name': dn,
                                 'report_type': 'Exam',
                                 'source': '台北榮總',
                                 'exam_name': en,
                                 'exam_value': ev}
                new_date = '2012-08-%s' % i
                recorded_date = datetime.datetime(*time.strptime(new_date, "%Y-%m-%d")[0:5])
                models.Report.AddExamReport(username, populate_data, recorded_date)

        self.redirect('/myrecord')



class UploadData(webapp2.RequestHandler):
    def get(self):
        ancestor_key = ndb.Key("Medicine", "medicine")
        all_side_effect = models.Medicine.query_medicine(ancestor_key)
        total_count = all_side_effect.count()

        path = os.path.join(os.path.dirname(__file__), '../templates/upload.html')
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
                #side_effect = models.SideEffect(parent=ndb.Key('SideEffect', 'sideeffect'),
                #                                name=''.join(side_effect_name),)
                #side_effect = models.Disease(parent=ndb.Key('Disease', 'disease_name'),
                #                             name=''.join(side_effect_name),)
                side_effect = models.Medicine(parent=ndb.Key('Medicine', 'medicine'),
                                              medicine_name=''.join(side_effect_name),)
                #side_effect = models.BioTestList(parent=ndb.Key('BioTestList', 'biotestlist'),
                #                                 biocheck_name=''.join(side_effect_name),)

                side_effect.put()
        self.redirect('/upload')


class DeleteData(webapp2.RequestHandler):
    def get(self):
        ancestor_key = ndb.Key("BioTestList", "biotestlist")
        all_side_effect = models.BioTestList.query_biotestlist(ancestor_key).fetch()
        #ancestor_key = ndb.Key("Medicine", "medicine")
        #all_side_effect = models.Medicine.query_medicine(ancestor_key).fetch()

        for i in all_side_effect:
            entity_key = i.key  # Key, looks like: Key('SideEffect', 'sideeffect', 'SideEffect', 5633)
            entity_key.delete()

        self.response.out.write('Done')

