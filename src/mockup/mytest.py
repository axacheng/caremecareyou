# -*- coding: utf-8 -*-

import datetime
import json
import logging
import models
import os
import time
import webapp2

from google.appengine.ext.webapp import template


class TagSearchJson(webapp2.RequestHandler):
    def get(self, term):
        medicine_result = []
        search_word = self.request.get('term')

        all_medicine = models.Medicine.query(models.Medicine.medicine_name >= unicode(search_word.capitalize()))
        result = all_medicine.fetch(5)

        if result:
            for medicine in result:
                medicine_result.append(medicine.medicine_name)

        self.response.headers['Content-Type'] = 'application/json'
        xxxx = [{'value':'1', 'name': 'AAA'},
                    {'value':'2', 'name': 'BBB'},
                    {'value':'3', 'name': 'CCC'}]

        self.response.out.write(json.dumps(xxxx))

    def post(self):
        username = '123456:[ TEST ]:facebook'  # Mocks
        populate_data = {'disease_name': '', 'medicine': '', 'side_effect': ''}
        terms = self.request.get_all('term')
        fetched_report_date = self.request.get_all('report_date')  # [u'2012-08-31']
        recorded_date = datetime.datetime(*time.strptime(''.join(fetched_report_date).encode('utf-8'), "%Y-%m-%d")[0:5])

        logging.info
        populate_data['disease_name'] = 'Tag disease'
        populate_data['medicine'] = terms[1].rstrip(', ')
        populate_data['side_effect'] = terms[2].rstrip(', ')

        models.Report.AddMedicineReport(username, populate_data, recorded_date)
        self.redirect('/myrecord')


class TagShow(webapp2.RequestHandler):
    """TagSearchJson render page"""
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../templates/justTagTest.html')
        self.response.out.write(template.render(path, 'template_dict'))




class TagPage(webapp2.RequestHandler):
    def get(self):
        t = {'my_disease_name_nav_menu': {'name': ['鼻涕丸', '高血脂', '大頭症'],
                                          'req_id': [0, 1, 2, 3, 4, 5],
                                          'chart_type': ['medicinetakenjson', 'sideeffectjson']},
             'username': '123456:[ TEST ]:facebook'}

        path = os.path.join(os.path.dirname(__file__), '../templates/justTest1.html')
        self.response.out.write(template.render(path, t))

