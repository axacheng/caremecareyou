# -*- coding: utf-8 -*-

import datetime
import gviz_api
import logging
import os
import models
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


def _DrawHelper(username, disease_name, chart_type, req_id):
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
    logging.info('username %s' % username)
    logging.info('disease_name %s' % disease_name)
    logging.info('chart_type %s' % chart_type)

    ancestor_key = ndb.Key("Report", username)
    my_reports = models.Report.query_personal_report(ancestor_key)
    logging.info('All user\'s Report %s' % my_reports.fetch(1))


    ###### 用藥記錄追蹤圖 ######
    if chart_type == 'medicinetakenjson':
      if my_reports.fetch(1):
        chart_data_template = []

        for data in my_reports.filter(models.Report.disease_name == disease_name).fetch():  #(TODO) 需要在 filter by 'disease_name'
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
        import random
        logging.info('req_id %s' % req_id)
        response = data_table.ToJSonResponse(columns_order=columns_order, order_by='time', req_id=req_id)
        return response
      else:
        pass  #(TODO) Need to work on here when there is no user's Report can be found.

    ###### 副作用記錄追蹤圖 ######
    if chart_type == 'sideeffectjson':
        chart_data_template = []

        for data in my_reports.filter(models.Report.disease_name == disease_name).fetch():
            chart_data = {}
            chart_data['time'] = data.date_created

            side_effect_index = 5
            side_effect_position = []
            for i in sorted(data.side_effect):
                side_effect_position.append(side_effect_index)
                side_effect_index += 5

                sideeffect_y_axis_data = zip(data.side_effect, map(int, side_effect_position))
                chart_data_template.append(dict(chart_data, **(dict(sideeffect_y_axis_data))))


        columns_order_list = []
        for medicine_list in chart_data_template:
          for medicine_name in medicine_list.keys():
            columns_order_list.append(medicine_name)

        columns_order = list(set(columns_order_list))
        columns_order.remove('time')
        chart_schema = {'time': ("datetime", "Time")}
        for medicine in columns_order:
            chart_schema[medicine] = ("number", medicine)
        columns_order.insert(0, 'time');


        ## Passing chart_schema and chart_data_template, and do really drawing work!
        data_table = gviz_api.DataTable(chart_schema)
        data_table.LoadData(chart_data_template)
        response = data_table.ToJSonResponse(columns_order=columns_order, order_by='time',
                                             req_id=req_id)
        return response
    else:
        pass 


    ###### 心情指數追蹤圖 ######
    if chart_type == 'mindingjson':
      if my_reports.fetch(1):
        minding_data_template = []

        for data in my_reports.filter(models.Report.disease_name == disease_name).fetch():  #(TODO) 需要在 filter by 'disease_name'
            chart_data = {}
            chart_data['time'] = data.date_created
            chart_data['minding'] = int(data.minding)
            minding_data_template.append(chart_data)

        chart_schema = {'time': ("datetime", "Time"),  #(TODO) Move it to constants
                        'minding': ("number", "Minding")}

        ## Passing chart_schema and minding_data_template, and do really drawing work!
        data_table = gviz_api.DataTable(chart_schema)
        data_table.LoadData(minding_data_template)
        response = data_table.ToJSonResponse(columns_order=('time', 'minding'),
                                             order_by='time', req_id=2)
        return response
    else:
        pass 


    ###### 檢查記錄追蹤圖 ######
    if chart_type == 'examjson':
      if my_reports.fetch(1):
        chart_data_template = []

        for data in my_reports.filter(models.Report.disease_name == disease_name).fetch():  #(TODO) 需要在 filter by 'disease_name'
            chart_data = {}
            chart_data['time'] = data.date_created
            chart_data['title'] = 'fuck'

            exam_name_and_value = zip(data.exam_name, map(int, data.exam_value))
            chart_data_template.append( dict(chart_data, **(dict(exam_name_and_value))) )   

        logging.info('chart_data_template %s' % chart_data_template)

        columns_order_list = []
        for exam_list in chart_data_template:
          for medicine_name in map(str, exam_list.keys()):
            columns_order_list.append(medicine_name)

        columns_order = list(set(columns_order_list))
        columns_order.remove('time')
        chart_schema = {'time': ("datetime", "Time")}

        for exam in columns_order:
            chart_schema[exam] = ("number", exam)

        chart_schema['title'] = ('string', 'title')
        columns_order.insert(0, 'time');




        ## Passing chart_schema and chart_data_template, and do really drawing work!
        logging.info('eeeeeee %s' % chart_schema)



        # chart_schema = {"time": ("datetime", "Time"),
        #                "salary": ("number", "Salary"),
        #                "title": ("string", "Title")
        #                }
        # chart_data_template = [
        #         {"salary": 10000, "title": 'aaaaa', "time": datetime.datetime(2012, 8, 10, 0, 0), },
        #         {"salary": 800, "title": 'bbb', "time": datetime.datetime(2012, 8, 15, 0, 0), },
        #         {"salary": 12500, "title": 'cccc', "time": datetime.datetime(2012, 8, 20, 0, 0), },
        #         {"salary": 7000, "title": 'ddd', "time": datetime.datetime(2012, 8, 25, 0, 0)}]



        chart_data_template =[
           {u'A': 8, 'title': 'YYYYY', u'C': 12, u'B': 5, 'time': datetime.datetime(2012, 10, 1, 0, 0)},
           {u'A': 2, u'C': 33, u'B': 19, 'title': 'B', 'time': datetime.datetime(2012, 9, 18, 0, 0)},
           {u'A': 8, u'C': 29, 'title': 'XXXX', u'B': 11, 'time': datetime.datetime(2012, 8, 28, 0, 0)},
           {u'A': 4, u'C': 11, u'B': 10, 'title': 'zzzzzz', 'time': datetime.datetime(2012, 8, 18, 0, 0)}]



        data_table = gviz_api.DataTable(chart_schema)
        data_table.LoadData(chart_data_template)
        response = data_table.ToJSonResponse(columns_order=columns_order, order_by='time',
                                            req_id=3)
        # response = data_table.ToJSonResponse(req_id=3, columns_order=['time', 'salary', 'title'], order_by='time')
        # logging.info('hahahahaha %s' % response)
        return response
      else:
        pass  #(TODO) Need to work on here when there is no user's Report can be found.





class MedicineTakenJson(webapp2.RequestHandler):
    def get(self, username, disease_name, chart_type ,req_id):
        #username = '123456:[[[[[[[[[ TEST ]]]]]]]]:facebook'
        response = _DrawHelper(username, disease_name, chart_type, req_id)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(response)


class ShowChart(webapp2.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), '../templates/showchart.html')
        self.response.out.write(template.render(path, ''))
