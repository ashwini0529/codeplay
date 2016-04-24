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
import requests
import os
import urllib2
import re
import time
import datetime
import motor
from motor import MotorClient


db = MotorClient('mongodb://ashwini:HALFpast12@ds011261.mlab.com:11261/scruto')['scruto']

class MainHandler(RequestHandler):
    def get(self):
        self.write(dict(status=1,message='API WORKING'))

class apiHandler(RequestHandler):
	@tornado.web.removeslash
	def get(self):
		counts=[]
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
			lat = str((lat+lato)/2)
			lon = str((lon+lono)/2)
			googleAPIKey='AIzaSyAhqgOMep5oBD_PgioNVDLDcCVk9FBahuc'
			#requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=26.2389,73.0243&radius=25000&types=restaurant|atm|bank|bar|cafe|doctor|gym|doctor&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
			requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=bus_station&key= AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk &deg='+str(deg)
			data = requests.get(requestedURL).json()
			data = dict(data=data,ammenity="bus_stands")
			counts.append(data)
			requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=hospital&key= AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk &deg='+str(deg)
			data = requests.get(requestedURL).json()
			data = dict(data=data,ammenity="hospital")
			counts.append(data)
			requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=restaurant&key= AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk &deg='+str(deg)
			data = requests.get(requestedURL).json()
			data = dict(data=data,ammenity="restaurant")
			counts.append(data)
			requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=police&key= AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk &deg='+str(deg)
			data = requests.get(requestedURL).json()
			data = dict(data=data,ammenity="police")
			counts.append(data)
			self.write(json.dumps(counts))
		else:
			self.write(dict(status=0,message='Either lat,long, or degree undefined.'))

class countHandler(RequestHandler):
	def post(self):

		lat = self.get_argument('lat','')
		lon = self.get_argument('lon','')
		counts = []
		def getData(lat,lon,place):
			requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lon)+"&radius=500&types=police&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   "
			data = requests.get(requestedURL).json()
			data = dict(data=data)
			countHotels = str(len(data['data']['results']))
			requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lon)+"&radius=500&types=restaurant&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   "
			data = requests.get(requestedURL).json()
			data = dict(data=data)
			countRestaurants = str(len(data['data']['results']))
			requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lon)+"&radius=500&types=bus_station&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   "
			data = requests.get(requestedURL).json()
			data = dict(data=data)
			countAtms = str(len(data['data']['results']))
			requestedURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lat)+","+str(lon)+"&radius=500&types=hospital&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   "
			data = requests.get(requestedURL).json()
			data = dict(data=data)
			countBars = str(len(data['data']['results']))
			ammenities = [{'name':'hospital','value':countBars},{'name':'police','value':countHotels},{'name':'restaurant','value':countRestaurants},{'name':'bus_stands','value':countAtms}]
			listOfCounts = dict(city=place,placeList=ammenities,latitude=lat,longitude=lon)
			print listOfCounts
			counts.append(listOfCounts)
		getData(lat,lon,'Vellore')
		getData('13.0827','80.2707','Chennai')
		getData('12.9716','77.5946','Bangalore')
		getData('17.3850','78.4867','Hyderabad')
		getData('19.0760','72.8777','Mumbai')
		self.write(json.dumps(dict(data=counts)))

class fetchAmenities(RequestHandler):
	def get(self):
		counts = []
		lat = str(self.get_argument('lat',''))
		lon = str(self.get_argument('lon',''))
		requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=bus_station&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
		data = requests.get(requestedURL).json()
		data = dict(data=data,ammenity="bus_stands")
		counts.append(data)
		requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=hospital&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
		data = requests.get(requestedURL).json()
		data = dict(data=data,ammenity="hospital")
		counts.append(data)
		requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=restaurant&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
		data = requests.get(requestedURL).json()
		data = dict(data=data,ammenity="restaurant")
		counts.append(data)
		requestedURL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat+','+lon+'&radius=1000&types=police&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
		data = requests.get(requestedURL).json()
		data = dict(data=data,ammenity="police")
		counts.append(data)
		self.write(json.dumps(counts))
	        print json.dumps(counts)
class registerHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        userName = self.get_argument('username','')
        password = self.get_argument('password','')
        email = self.get_argument('email','')
        location = self.get_argument('location','Vellore')
        gender = self.get_argument('gender', 'male')
        timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        likes = []
        writeData = {'username' : userName, 'password': password,'email':email, 'location' : location , 'gender' : gender,'likes':likes,'registered_at':timeStamp,'places':[]}
        result = yield db.users.insert(writeData)
        print result
        result = yield db.users.find_one({'username':userName})
        userId = {'$oid' : str(result['_id']) }
        self.write(json.dumps(dict(status=1, message='User registered successfully',_id = userId),indent = 4))
        self.flush()

class loginHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        userName = self.get_argument('username', '')
        password = self.get_argument('password','')
        result = yield db.users.find_one({'username':userName,'password':password})
        if(bool(result)):
            data=[]
            cursor = db.users.find({'username': userName,'password':password})
            while (yield cursor.fetch_next):
                document = cursor.next_object()
                data.append(json.loads(json_util.dumps(document)))
                #self.write(str(document))
                self.write(json.dumps(dict(data=data,status=1,message="User logged in successfully"),indent=4))
        else:
            self.write(dict(status=0,message="Invalid credentials"))

class profileHandler(RequestHandler):
	@gen.coroutine
	def post(self):
		userId = self.get_argument('userId', '')
		if userId!='':
			data=[]
			cursor = db.users.find({'_id': ObjectId(userId)})
			while (yield cursor.fetch_next):
		         document = cursor.next_object()
		         data.append(json.loads(json_util.dumps(document)))
		         #self.write(str(document))
			self.write(json.dumps(dict(data=data)))
		else:
			self.write(json.dumps(dict(data={'message' : 'Please enter user ID'})))

class likesHandler(RequestHandler):
	@gen.coroutine
	def post(self):
		userId = self.get_argument('userId','')
		likedItemName = self.get_argument('name','')
		likedItemDescription = self.get_argument('description','No description given')
		timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		data = {'item_name':likedItemName,'item_description':likedItemDescription,'time':timeStamp}
		result = yield db.users.update({'_id': ObjectId(userId)}, {'$push':{'likes':data}})
		print result
		self.write(json.dumps(dict(status=1, message='Liked successfully'),indent = 4))
		self.flush()

class fetchAmenitiesUI(RequestHandler):
	def get(self):
		place = self.get_argument('place','')
		typeOfAminity = self.get_argument('ammenity','')
		requestedURL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+typeOfAminity+'+in+'+place+'&key=   AIzaSyBaMXRTKp1C0SOKO7Y28vR-VHod3MNA5Zk   '
		data = requests.get(requestedURL).json()
		self.write(data)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api",apiHandler),
        (r"/count",countHandler),
        (r"/register",registerHandler),
        (r"/login",loginHandler),
        (r"/profile",profileHandler),
        (r"/like",likesHandler),
        (r"/ammenity",fetchAmenities),
        (r"/fetch",fetchAmenitiesUI)
],  debug=True)
##########################################################################################################
#												App Run
##########################################################################################################

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
