import datetime
import json
import logging
import models
import os
import time
import webapp2

from google.appengine.ext.webapp import template


class TagSearch(webapp2.RequestHandler):
    def get(self, term):
        medicine_result = []
        search_word = self.request.get('term')
        logging.info('MY TERM   :::::: %s' % search_word)

        # query.filter("Display", True)
        # query.filter("Word >=", unicode(search_word))
        # query.filter("Word <", unicode(search_word) + u'\ufffd')

        all_medicine = models.Medicine.query(models.Medicine.medicine_name >= unicode(search_word.capitalize()))
        result = all_medicine.fetch(10)

        if result:
            for medicine in result:
                medicine_result.append(medicine.medicine_name)

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(medicine_result))

        # path = os.path.join(os.path.dirname(__file__), 'templates/justTest.html')
        # self.response.out.write(template.render(path, 'template_dict'))

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


class TagPage(webapp2.RequestHandler):
    def get(self):
        t = {'my_disease_name_nav_menu': {'name': ['鼻涕丸', '高血脂', '大頭症'],
                                          'req_id': [0, 1, 2, 3, 4, 5],
                                          'chart_type': ['medicinetakenjson', 'sideeffectjson']},
             'username': '123456:[ TEST ]:facebook'}

        path = os.path.join(os.path.dirname(__file__), 'templates/justTest1.html')
        self.response.out.write(template.render(path, t))

