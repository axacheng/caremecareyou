#!/usr/bin/python

import os
import random
import simplejson
import time
import urllib2
import uuid

SIDE_EFFECT_URL = 'side_effect_url_fixed'
urls = []
OK_LIST = 'all_gentoo'
FAILED_LIST = 'fail_list_from_gentoo'

user_agent = [
    'PaiSai/Godzilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'PaiSai/A-la/9.25 (Windows NT 5.1; U; en)',
    'PaiSai/Godzilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'PaiSai/A-la/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'PaiSai/Godzilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'PaiSai/SexyBaby/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
    ]

fail_list = []
i = 1
all_result = """"""

for url in open(SIDE_EFFECT_URL):
  delay = random.randrange(1, 8)
  print 'Number: %s' % i
  i += 1
  mock_xff = str(uuid.uuid4())
  delay = 1
  print 'Sleep for: %d seconds' % (delay)
  time.sleep(delay)
  
  if not (i % 23):
    print 'renew IP sleep by calling ppp'
    network_restart = os.system('/etc/init.d/net.ppp0 restart')
    if network_restart:
      time.sleep(10)
      OK_LIST = OK_LIST+'_'+str(i)
    
  req = urllib2.Request(url)
  req.add_header('X-Forwarded-For', mock_xff)
  req.add_header('User-agent', random.choice(user_agent))
  html = urllib2.urlopen(req) ###html.info()
  result = html.read()
  all_result += result

  print result
  w = open(OK_LIST, 'w')
  w.write(all_result)
  w.close()
