# -*- coding: utf-8 -*-

import datetime
import gviz_api
import logging
import os
import models
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


def _DrawHelper(username, disease_name=None):
    """ 讀取使用者在Report 的資料庫，並以疾病名稱為過濾首要條件，然後藉由gviz_api吐出 json。

    這是一個 helper function是為了給 ShowMedicineTakenChartJson使用。
    首先我們先用ndb.Key的方式抓出使用者所有的Report並用 fetch()存成一個list of object.
    之後就使用多種的方式去組成 gviz_api他要的 chart_data_template 與 chart_schema格式。
    範例格式：
    chart_data_template = [{u'Papaverine': 40, u'Ulcol': 20,
                             'time': datetime.datetime(2012, 8, 26, 0, 0)}]

    chart_schema = {'U-clor': ('number', 'U-clor'), 'time': ('datetime', 'Time'),
                    'Papaverine': ('number', 'Papaverine')}

    Args: username, (string): Logged in username
          disease_name, (string): From /showchartjson/USERNAME/disease_name

    Return: gviz_api.ToJSonResponse() object. for json format rendering.
    """

    ancestor_key = ndb.Key("Report", username)
    my_reports = models.Report.query_personal_report(ancestor_key)
    logging.info('All user\'s Report %s' % my_reports.fetch())

    if my_reports.fetch():
      chart_data_template = []
      for data in my_reports.fetch():  #(TODO) 需要在 filter by 'disease_name'
          chart_data = {}
          chart_data['time'] = data.date_created

          # 以下的 zip與map一堆的鬼是把位了組成 [('A藥':'劑量x單位'), ('B藥':'劑量y單位')]
          medicine_and_dosage_data = zip(data.medicine, map(int, data.dosage))

          # 把上面建立的含有 'time'的chart_data這dict和 medicine_and_dosage_data 這dict合併在一起。
          # Merge above two dicts into chart_data, less more readable but faster.
          # http://stackoverflow.com/questions/38987/how-can-i-merge-union-two-python-dictionaries-in-a-single-expression
          chart_data_template.append( dict(chart_data, **(dict(medicine_and_dosage_data))) )   

      logging.info('chart_data_template %s' % chart_data_template)


      # 以下我們把 chart_data_template抓出的所有藥品名藉由兩次的forloop把每一筆 Report entity的
      # 藥品名稱(即: medicine_list.keys()) 抓出並透過 map轉成str 然後在跑一次forloop 抓取藥名並存到
      # columns_order_list 中。 最後在用 set 去把重複的藥物名稱刪除並且刪除 'time' 這個list中的element.
      columns_order_list = []
      for medicine_list in chart_data_template:
        for medicine_name in map(str, medicine_list.keys()):
          columns_order_list.append(medicine_name)

      columns_order = list(set(columns_order_list))
      columns_order.remove('time')

      # 組一個default dict 名為 chart_schema並給他一個預設key為'time'的元素
      # 然後我們需要藉由上面的columns_order 去跑一下的 forloop組成一個 dict.
      # {'time': ("datetime", "Time"), 'A藥': ("number", 'A藥'), 'B藥': ("number", 'B藥')}
      # 最後在把 'time' 這 list element塞到 columns_order這 list的最前面。這麼做的原因是因為 google chart
      # api 在組資料畫圖時，必須要把 time 時間欄位放到第一個。
      # 組好這 chart_shema dict後，就可以給 gviz_api.DataTable使用。
      chart_schema = {'time': ("datetime", "Time")}
      for medicine in columns_order:
          chart_schema[medicine] = ("number", medicine)
      columns_order.insert(0, 'time');


      ## Passing chart_schema and chart_data_template, and do really drawing work!
      logging.info('eeeeeee %s' % chart_schema)
      data_table = gviz_api.DataTable(chart_schema)
      data_table.LoadData(chart_data_template)
      response = data_table.ToJSonResponse(columns_order=columns_order, order_by='time')
      return response
    else:
      pass  #(TODO) Need to work on here when there is no user's Report can be found.


class ShowMedicineTakenChartJson(webapp2.RequestHandler):
    def get(self):
        username = '123456:[[[[[[[[[ TEST ]]]]]]]]:facebook'
        response = _DrawHelper(username)
        self.response.out.write(response)


class ShowChart(webapp2.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), '../templates/showchart.html')
        self.response.out.write(template.render(path, ''))
