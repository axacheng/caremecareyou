# -*- coding: utf-8 -*-

import os
import webapp2
import models
import csv
import logging

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


class MainPage(webapp2.RequestHandler):
  def get(self):
	template_dict = {'username':'axa'}
	path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, template_dict))


class UploadData(webapp2.RequestHandler):
	def get(self):
	  ancestor_key = ndb.Key("SideEffect", "sideeffect")
	  all_side_effect = models.SideEffect.query_sideeffect(ancestor_key)
	  path = os.path.join(os.path.dirname(__file__), 'upload.html')

	  if all_side_effect is None:
	  	self.response.out.write('No data')
	  else:
		self.response.out.write(template.render(path, {'all_side_effect':all_side_effect}))

	def post(self):
	  uploaded_file = csv.reader(self.request.get('csv'))
	  for side_effect_name in uploaded_file:
	  	if side_effect_name:
		  side_effect = models.SideEffect(parent=ndb.Key('SideEffect', 'sideeffect'),
		  								  name=''.join(side_effect_name),)
		  side_effect.put()
	  self.redirect('/upload')


class DeleteData(webapp2.RequestHandler):
	def get(self):
	  ancestor_key = ndb.Key("SideEffect", "sideeffect")
	  all_side_effect = models.SideEffect.query_sideeffect(ancestor_key).fetch()

	  for i in all_side_effect:
	  	entity_key = i.key #Key, looks like: Key('SideEffect', 'sideeffect', 'SideEffect', 5633)
	  	entity_key.delete()
	  	#self.response.out.write(entity_key)   	  


app = webapp2.WSGIApplication([('/', MainPage),
							   ('/upload', UploadData),
							   ('/delete', DeleteData)])