#import all fucking Libraries
import tornado
import tornado.ioloop
import tornado.web
from bson import json_util
import os, uuid
import sys
import json
#Tornado Libraries
from tornado.ioloop import IOLoop
from tornado.escape import json_encode
from tornado.web import RequestHandler, Application, asynchronous
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import engine, Task
from tornado.web import RequestHandler
from tornado import gen

from bson.objectid import ObjectId
#Other Libraries
import math
import json
import requests
import os
import urllib2
import re
import time
import datetime
import motor
from motor import MotorClient


db = MotorClient()['orphans']

class MainHandler(RequestHandler):
    def get(self):
        self.write(dict(status=1,message='API WORKING'))


class addOrphan(RequestHandler):
	@gen.coroutine
	def post(self):
		name   = self.get_argument('name','')
		age = self.get_argument('age',0)
		gender = self.get_argument('gender','male')
		address = self.get_argument('address','')
		city = self.get_argument('city','')
		state = self.get_argument('state','')
		latitude = self.get_argument('latitude','')
		longitude = self.get_argument('longitude','')
		timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		isTaken = 0
		writeData = {
		'name':name, 
		'age':age,
		'gender':gender,
		'address':address,
		'city':city,
		'state':state,
		'time':timeStamp,
		'isTaken': isTaken,
		'latitude':latitude,
		'longitude':longitude
		}
		result = yield db.orphans.insert(writeData)
		print writeData
		self.write({'status':1,'message':'Data added successfully'})
		self.flush()


class showOrphans(RequestHandler):
	@gen.coroutine
	def post(self):
		city = self.get_argument('city','')
		state = self.get_argument('state','')
		age = self.get_argument('age','')
		gender = self.get_argument('gender','')
		db = self.settings['db']
		data = []
		if(city!=''):
			cursor = db.orphans.find({'city':city})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(state!=''):
			cursor = db.orphans.find({'state':state})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(age!=''):
			cursor = db.orphans.find({'age':age})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(gender!=''):
			cursor = db.orphans.find({'gender':gender})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/add",addOrphan),
        (r"/show",showOrphans)
],  debug=True, db=db)
##########################################################################################################
#												App Run
##########################################################################################################

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
