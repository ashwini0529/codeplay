#Tornado Libraries
from tornado.ioloop import IOLoop
from tornado.escape import json_encode
from tornado.web import RequestHandler, Application, asynchronous, removeslash
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import engine, Task, coroutine

#Other Libraries
from motor import MotorClient
import json
import time
import datetime
import requests
import os
import urllib2
import hashlib
from bson.objectid import ObjectId
import re
import pymongo


db = MotorClient('mongodb://ashwini:HALFpast12@ds011261.mlab.com:11261/scruto')['scruto']

class MainHandler(RequestHandler):
    @removeslash
    @coroutine
    def get(self):
        result_current = result_current_info = None
        userInfo = None
        if bool(self.get_secure_cookie("user")):
            current_id = self.get_secure_cookie("user")
            userInfo = yield db.users.find_one({'_id':ObjectId(current_id)})
            print userInfo
        self.render("home.html",result = dict(name="Scruto",userInfo=userInfo,loggedIn = bool(self.get_secure_cookie("user"))))

class signupHandler(RequestHandler):
    @coroutine
    def get(self):
        self.render('signup.html')

class loginHandler(RequestHandler):
	@removeslash
	def get(self):
	        if bool(self.get_secure_cookie("user")):
	                self.redirect("/")
                self.render("login.html")

	@removeslash
	@coroutine
	def post(self):
		db = self.settings['db']
		username = self.get_argument("username")
		password = self.get_argument("password")
		result = yield db.users.find_one({'username':username,'password':password})
		if bool(result):
			self.set_secure_cookie("user", str(result['_id']))
			self.redirect("/")
		else:
			self.redirect("/login?status=False")

class signupHandler(RequestHandler):
    @removeslash
    @coroutine
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        email = self.get_argument('email','')
        gender = self.get_argument('gender','male')
        location = self.get_argument('city','Vellore')
        likes=[]
        result = yield db.users.find_one({"username":username})
        timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print bool(result)
        if(bool(result)):
            self.redirect('/login?username=taken')
        else:
            result = yield db.users.insert({'username':username,'password':password,'location':location ,'email':email,'gender':gender,'registered_at':timeStamp,'likes':[],'places':[]})
            self.set_secure_cookie('user',str(result))
            self.redirect('/profile')
            print bool(self.get_secure_cookie("user"))
class profileHandler(RequestHandler):
    @coroutine
    @removeslash
    def get(self):
        result_current = result_current_info = None
        userInfo = None
        if bool(self.get_secure_cookie("user")):
            current_id = self.get_secure_cookie("user")
            userInfo = yield db.users.find_one({'_id':ObjectId(current_id)})
            likesCount = len(userInfo['likes'])
            print userInfo
        self.render("profile.html",result = dict(name="Scruto",userInfo=userInfo, likesCount = likesCount,self = self ,loggedIn = bool(self.get_secure_cookie("user"))))
class logoutHandler(RequestHandler):
    @removeslash
    @coroutine
    def get(self):
        self.clear_cookie('user')
        self.redirect('login?loggedOut=true')

class likesHandler(RequestHandler):
    @coroutine
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
        requestedURL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+typeOfAminity+'+in+'+place+'&key= AIzaSyDcw8q78qRZWDymOt3HyAFRJdGlEH46pRY '
        data = requests.get(requestedURL).json()
        self.write(data)

settings = dict(
		db=db,
		template_path = os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static"),
		debug=True,
		cookie_secret="35an18y3-u12u-7n10-4gf1-102g23ce04n6"
	)

#Application initialization
application = Application([
	(r"/", MainHandler),
    (r"/signup", signupHandler),
    (r"/login", loginHandler),
    (r"/logout",logoutHandler),
    (r"/profile", profileHandler),
    (r"/fetch",fetchAmenitiesUI),
    (r"/like",likesHandler)
], **settings)

#main init
if __name__ == "__main__":
	server = HTTPServer(application)
	server.listen(8001)
	IOLoop.current().start()
