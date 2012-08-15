# -*- coding: utf-8 -*-

import datetime
import gviz_api
import logging
import os
import models
import webapp2

from google.appengine.ext import ndb

from google.appengine.ext.webapp import template


def _DrawHelper():
    username = '123456:[[[[[[[[[ TEST ]]]]]]]]:facebook'  # Mocks
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

# 急性咽喉炎
# Eafunin, Fecole, Gaba-p, Well-well, Gabapentin

    # [{'Fecole': 5, 'Eafunin': 5, 'Well-well': 8, 'Gaba-p': 10, 'Gabapentin': 3,
    #   'time': datetime.datetime(2012, 8, 15, 0, 0)}]
    logging.info('TTTTTTTTT %s' % data.medicine)

    chart_schema = {'time': ("datetime", "Time")}
    for medicine in data.medicine:
        chart_schema[medicine] = ("number", medicine)

    ## Do really work!
    data_table = gviz_api.DataTable(chart_schema)
    data_table.LoadData(chart_data_template)

    columns_order = data.medicine
    columns_order.insert(0, 'time');
    response = data_table.ToJSonResponse(columns_order=columns_order, order_by='time')
    return response


########## Testing code ############
class testShowChartJson(webapp2.RequestHandler):
    def get(self):


        # data_table = gviz_api.DataTable(chart_schema)
        # data_table.LoadData(chart_data)
        # columns_order = ', '.join(str(column) for column in chart_schema.keys())

        # logging.info('aaaaaaaaa %s' % columns_order)
        # response = data_table.ToJSonResponse(columns_order=(chart_schema.keys()),
        #                                      order_by="time")


        # data = [ { '67638': 1, '774': 22, 'time': datetime.datetime(2012, 06, 10, 12, 31, 0)}, 
        #          { '67638': 30, '774': 5, '8273223': 10, 'time': datetime.datetime(2012, 06, 20, 12, 32, 0)}, 
        #          { 'time': datetime.datetime(2012, 07, 15, 12, 33, 0), '774': 10, '8273223': 10 },
        #          { 'time': datetime.datetime(2012, 07, 16, 12, 33, 0), '67638': 5, '8273223': 10 },
        #        ]
        # schema = { 'time': ("datetime", "Time"),
        #            '67638': ("number", 'A medicine'),
        #            '774': ("number", 'B medicine'),
        #            '8273223': ("number", 'C medicine') }


        # data_table = gviz_api.DataTable(schema)
        # data_table.LoadData(data)
        #response = data_table.ToJSonResponse(columns_order=("time", "67638", "774", "8273223"), order_by="time")
        response = _DrawHelper()
        self.response.out.write(response)


class testShowChart(webapp2.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), '../templates/showchart.html')
        self.response.out.write(template.render(path, ''))
