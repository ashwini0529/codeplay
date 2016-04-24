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


db = MotorClient()['scruto']
class MainHandler(RequestHandler):
    def get(self):
        self.write(dict(status=1,message='API WORKING'))

class apiHandler(RequestHandler):
	def get(self):
		lat = float(self.get_argument('lat',0))
		lon = float(self.get_argument('lon',0))
		deg = float(self.get_argument('deg',0))
		R = 6378137
		alpha = 60
		dist = 1000
		radius = 500
		if (lat!=0 and lon !=0 and deg !=0):
			xDist = dist * math.cos(deg/180*math.pi)
			yDist = dist * math.sin(deg/180*math.pi)
			dLat = yDist/R
			dLon = xDist/(R*math.cos(math.pi*lat/180))
			ans = dLat*180/math.pi
			lato = lat+ans
			ans = dLon*180/math.pi
			lono = lon+ans
			latFinal = str((lat+lato)/2)
			lonFinal = str((lon+lono)/2)
			googleAPIKey='AIzaSyAhqgOMep5oBD_PgioNVDLDcCVk9FBahuc'
			#requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=26.2389,73.0243&radius=25000&types=restaurant|atm|bank|bar|cafe|doctor|gym|doctor&key=AIzaSyBeYe4loaSnbCI3W2tNdw-MpORxDWJ4Lt8'
			requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+latFinal+','+ lonFinal+ '&radius=25000&types=restaurant|atm|bank|bar|cafe|doctor|gym|doctor&key=AIzaSyBeYe4loaSnbCI3W2tNdw-MpORxDWJ4Lt8'
			#requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(latFinal)+','+str(lonFinal)+'&radius='+str(radius)+'&types=amusement_park|doctor|food|gym|zoo|shopping_mall|restaurant|night_club|hospital|lodging|bar&key='+googleAPIKey+'&sensor=true'
			data = requests.get(requestedURL).json()
			self.write(json.dumps(dict(status="success", data=data),indent = 4))
		else:
			self.write(dict(status=0,message='Either lat,long, or degree undefined.'))

# class Ammenities(RequestHandler):
# 	def get(self):
# 		nextPageToken = self.get_argument('page_token','')
# 		# if nextPageToken=='':
# 		# 	requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=26.2389,73.0243&radius=1000&types=restaurant|atm|bank|bar|cafe|doctor|gym|doctor&key=AIzaSyBeYe4loaSnbCI3W2tNdw-MpORxDWJ4Lt8"
# 		# else:
# 		requestedURL = "non"
# 		requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=26.2389,73.0243&radius=1000&types=restaurant|atm|bank|bar|cafe|doctor|gym|doctor&key=AIzaSyBeYe4loaSnbCI3W2tNdw-MpORxDWJ4Lt8&pagetoken="+str(nextPageToken)
		
# 		restaurantData = requests.get(requestedURL).json()
# 		print requestedURL
# 		#print restaurantData
# 		#countRestaurants = len(restaurantData['results'])
# 		self.write(restaurantData)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api",apiHandler)

],  debug=True)
##########################################################################################################
#												App Run
##########################################################################################################

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
