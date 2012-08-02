
import logging
import models
import webapp2
import os
import datetime

from google.appengine.ext import ndb
from google.appengine.api import users

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required


class MainPage(webapp2.RequestHandler):
    def get(self):        
        ##############################################
        ### Insert StructuredPropertyentry  Example ##
        ##############################################
        # username = 'axa'
        # store_user = models.User(name=username,
				       #  		   profile=[models.Profile(status=True,
					   #      							   account_type='facebook',
					   #      							   account_id='44',
					   #      							   account_name=username,
					   #      							   access_token='####111222333###',
					   #      							   country='TAIWAN',
					   #      							   protray='',
					   #      							   email='axa.cheng@gmail.com',
					   #      							   birthday=datetime.datetime.now().date(),
					   #      							   gender='male'
					   #      							  )])
        # store_user.put()

        ############################################
        ###   StructuredProperty Query  Example  ###
        ############################################

        ### Projection query example.
        ### Return is a single entity.
        #all_query_result = models.User.query().get(projection=["name", "profile.account_id"])
        #logging.info('xxxxxxx %s' % all_query_result.name)

        ### Query.get() method. Only one entity can be found from ndb....
        #all_query_result = models.User.query(models.User.profile.account_id == '44').get()
        #result = all_query_result.profile
        #logging.info('Query result %s' % result)

        ### Query(). It can fetch all entities from ndb... Similarly, old db Query().all()
        ### Note, ndb doesn't have all() method.
        all_query_result = models.User.query(models.User.profile.account_id == '44')
        
        # Compile all the 'key' to template_dict and pass them to index.html
        # This url_link could be logout_link or login_link depends on whether
        # username exist or not. If it's exist then url_link is logout_link,
        # vice versa.
        template_dict = {'all_query_result': all_query_result }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_dict))

### index.html
"""
<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="utf-8">
    <title> dbtest </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">
  </head>


  <body>
    Hello 
    <hr>
    <!-- Query for .get() method -->
    {% for i in all_query_result %}
    <pre>
        User ID: {{ i.name }}
        User ID: {{ i.profile.account_id }}
    </pre>
    {% endfor %}


  </body>
</html>
"""



app = webapp2.WSGIApplication([('/', MainPage),])
