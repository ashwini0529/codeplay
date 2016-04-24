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


db = MotorClient()['codeplay']

class MainHandler(RequestHandler):
    def get(self):
        self.write(dict(status=1,message='API WORKING'))


class addEvent(RequestHandler):
	@gen.coroutine
	def post(self):
		name   = self.get_argument('name','')
		description = self.get_argument('desc','')
		address = self.get_argument('address','')
		city = self.get_argument('city','')
		state = self.get_argument('state','')
		typeOfEvent = self.get_argument('type','')
		latitude = self.get_argument('latitude','')
		longitude = self.get_argument('longitude','')
		timeStamp = self.get_argument('time','')	
		link = self.get_argument('link','#')
		degree = self.get_argument('degree','0')
		writeData = {
		'name':name, 
		'description' : description,
		'address':address,
		'city':city,
		'state':state,
		'typeOfEvent':typeOfEvent,
		'time':timeStamp,
		'link':link,
		'latitude':latitude,
		'longitude':longitude,
		'degree' : float(degree)
		}
		result = yield db.events.insert(writeData)
		print writeData
		self.write({'status':1,'message':'Data added successfully'})
		self.flush()


class showEvents(RequestHandler):
	@gen.coroutine
	def post(self):
		city = self.get_argument('city','')
		state = self.get_argument('state','')
		typeOfEvent = self.get_argument('type','')
		degree = self.get_argument('degree','')

		db = self.settings['db']
		data = []
		if(city!=''):
			cursor = db.events.find({'city':city})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(state!=''):
			cursor = db.events.find({'state':state})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(degree!=''):
			lowerDegree = float(degree)-20
			higherDegree = float(degree)+20
			cursor = db.events.find({'degree':{'$gte':lowerDegree,'$lte':higherDegree}})
			print lowerDegree
			print higherDegree
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))
		elif(typeOfEvent!=''):
			cursor = db.events.find({'typeOfEvent':typeOfEvent})
			print typeOfEvent
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
			self.write(json.dumps(dict(data=data)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/add",addEvent),
        (r"/show",showEvents)
],  debug=True, db=db)
##########################################################################################################
#												App Run
##########################################################################################################

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
