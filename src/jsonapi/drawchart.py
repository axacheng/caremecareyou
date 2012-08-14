# -*- coding: utf-8 -*-

import datetime
import gviz_api
import os
import webapp2

from google.appengine.ext.webapp import template


########## Testing code ############
class testShowChartJson(webapp2.RequestHandler):
    def get(self):

        data = [ { '67638': 1, '774': 22, 'time': datetime.datetime(2012, 06, 10, 12, 31, 0)}, 
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

        path = os.path.join(os.path.dirname(__file__), '../templates/showchart.html')
        self.response.out.write(template.render(path, ''))
