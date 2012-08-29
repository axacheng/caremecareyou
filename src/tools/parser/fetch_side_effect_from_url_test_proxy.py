#!/usr/bin/python

import os
import random
import simplejson
import time
import urllib2
import uuid

proxy = 'proxy.hinet.net'
SIDE_EFFECT_URL = 'side_effect_url_fixed2'
urls = []
OK_LIST = 'all_gentoo_2'
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
for url in open(SIDE_EFFECT_URL):
  print 'Number: %s' % i
  i += 1
  #delay = random.randrange(10, 15)
  delay = 3
  mock_xff = str(uuid.uuid4())
  print 'Sleep for: %d seconds' % (delay)
  time.sleep(delay)
  
  if not (i % 50):
    print 'long sleep'
    time.sleep(10)
  else:
    req = urllib2.Request(url)
    req.add_header('X-Forwarded-For', mock_xff)
    req.add_header('User-agent', random.choice(user_agent))
    #req.set_proxy(proxy, 'http')  ### THIS IS A IMPORTANT APPROCH.
    html = urllib2.urlopen(req) ###html.info()
    try:
      result = simplejson.load(html)
    except simplejson.decoder.JSONDecodeError:
      print 'JSON Error', fail_list.append(str(i))
      print fail_list
      w = open(FAILED_LIST, 'w')
      w.write(str(fail_list))
      w.close()
      continue

    if result:
      print result
      urls.extend(result)
      w = open(OK_LIST, 'w')
      w.write(str(urls))
      w.close()

print 'ALL:%s \n Total:%d' % (urls, len(urls))


