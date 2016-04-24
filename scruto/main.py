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
import requests
import os
import urllib2
import hashlib
from bson.objectid import ObjectId
import re
import pymongo

db = MotorClient()['beforethecourt']

class MainHandler(RequestHandler):
	@coroutine
	def get(self):
		result_current = result_current_info = None
		statusMessage = self.get_argument("alert","")
		db = self.settings['db']
		categories = db.category_list.find()
		categories = yield categories.to_list(None)
		if bool(self.get_secure_cookie("user")):
			current_id = self.get_secure_cookie("user")
		questionList = yield db.Questions.find({'answers':{'$not':{'$size':0}}}).to_list(None)
		answerList = yield db.Answers.find().to_list(None)
		userList = yield db.users.find().to_list(None)
		userinfoList = yield db.user_info.find().to_list(None)
		notifications = yield db.notifications.find({'to':self.get_secure_cookie('user'),'read':0}).to_list(None)
		self.render("home.html",result = dict(title = "BeforetheCourt", loggedIn = bool(self.get_secure_cookie("user")), result_current = result_current, questionList = questionList, answerList = answerList, userinfoList = userinfoList, userList= userList, result_current_info = result_current_info, categories = categories, statusMessage = statusMessage, notifications = notifications))

class SignupHandler(RequestHandler):
	@removeslash
	@coroutine
	def post(self):
		db = self.settings['db']
		name = self.get_argument("name").split()
		last_name = ' '.join(name[1:])
		first_name = name[0]
		email = self.get_argument("email")
		pwd = self.get_argument("pwd")
		result = yield db.users.find_one({"email":email})
		if bool(result):
			self.redirect("/?alert=Signup")
		else:
			result = db.users.find({"$and":[{"first_name":name[0]},{"last_name":' '.join(name[1:])}]})
			url = name
			count = yield result.count()
			url.append(str(count+1))
			result = yield db.users.insert({"first_name":first_name,"last_name":last_name,"email":email,"password":pwd,"url":'-'.join(url)})
			import uuid
			random_email = str(uuid.uuid4())+str(result)
			result_info = yield db.user_info.insert({"display_picture":"default.png","email_token":random_email,"email_verified":0,"description" : "", "bio" : "", "uid" : str(result)})
			self.set_secure_cookie("user",str(result))
			self.redirect("/")

class SigninHandler(RequestHandler):
	@removeslash
	def get(self):
		self.redirect("/")

	@removeslash
	@coroutine
	def post(self):
		db = self.settings['db']
		email = self.get_argument("login_email")
		pwd = self.get_argument("login_pwd")
		result = yield db.users.find_one({'email':email,'password':pwd})
		if bool(result):
			self.set_secure_cookie("user", str(result['_id']))
			self.redirect("/")
		else:
			self.redirect("/?alert=Login")

class LogoutHandler(RequestHandler):
	@removeslash
	def get(self):
		self.clear_cookie('user')
		self.redirect("/login")

class ProfileHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self, url=None):
		db = self.settings['db']
		result_current_info = result_current = None
		categories = db.category_list.find()
		categories = yield categories.to_list(None)
		result_user = yield db.users.find_one({'url':url})
		result_user_info = yield db.user_info.find_one({'uid':str(result_user['_id'])})
		if bool(self.get_secure_cookie("user")):
			current_id = self.get_secure_cookie("user")
			result_current = yield db.users.find_one({'_id':ObjectId(current_id)})
			result_current_info = yield db.user_info.find_one({'uid':str(result_current['_id'])})
			if url == None:
				result_user = result_current
				result_user_info = result_current_info
		notifications = yield db.notifications.find({'to':self.get_secure_cookie('user'),'read':0}).to_list(None)
		questions = yield db.Questions.find({"user": str(result_user['_id'])}).to_list(None)
		answers =  yield db.Answers.find({"uid": str(result_user['_id'])}).to_list(None)
		Ans = yield db.Answers.find().to_list(None)
		upvotes = filter(lambda item: str(result_user['_id']) in item['Upvotes'], Ans)
		downvotes = filter(lambda item: str(result_user['_id']) in item['Downvotes'], Ans)
		self.render("profile.html", result=dict(result_user=result_user, result_current = result_current, result_current_info = result_current_info, title=result_user['first_name']+' '+result_user['last_name'], loggedIn = bool(self.get_secure_cookie("user")), categories = categories, result_user_info= result_user_info, questions= questions, notifications = notifications, answers = answers, upvotes = upvotes, downvotes = downvotes))

class CategoryListHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		q = str(self.get_argument("q",''))
		db = self.settings['db']
		List = []
		if not len(q):
			List = yield db.category_list.find().to_list(None)
		else:
			List = yield db.category_list.find({"name": {'$regex':re.compile(q,re.IGNORECASE)}}).to_list(None)
		self.render("categories.html", List = List)

class AskQuestion(RequestHandler):
	@removeslash
	@coroutine
	def post(self):
		if bool(self.get_secure_cookie("user")):
			try:
				categories = self.request.arguments['val']
			except:
				categories = []
			question = self.get_argument('question')
			anonymous = self.get_argument('anonymous',"off")
			db = self.settings['db']
			insert = yield db.Questions.insert({"question":question,"categories":len(categories),"anonymous":anonymous,"answers":[],"answer_wanted":1,"user":self.get_secure_cookie("user")})
			for category in categories:
				ins_cat = yield db.category_list.update({"_id": ObjectId(category)},{'$push':{"questions":str(insert)}})
			self.redirect("/?alert=Question")

class UploadHandler(RequestHandler):
	@removeslash
	@coroutine
	def post(self):
		import os
		from PIL import Image
		import cStringIO
		canvas_data = self.get_argument('canvas_data','')
		remove = self.get_argument('remove',0)
		print canvas_data
		if not canvas_data=='':
			imgstr = re.search(r'base64,(.*)', canvas_data).group(1)
			db = self.settings['db']
			fname = self.get_secure_cookie("user")+'.png'
			filepath = os.path.join("static/img/profile",fname)
			tempimg = cStringIO.StringIO(imgstr.decode('base64'))
			im = Image.open(tempimg)
			im = im.resize((160,160),Image.ANTIALIAS)
			im.save(filepath,optimize=True, quality=95)
			update = yield db.user_info.update({"uid":self.get_secure_cookie("user")},{"$set":{"display_picture":fname}})

		if remove=="yes":
			db = self.settings['db']
			fname = self.get_secure_cookie("user")+'.png'
			filepath = os.path.join("static/img/profile",fname)
			os.remove(filepath)
			update = yield db.user_info.update({"uid":self.get_secure_cookie("user")},{"$set":{"display_picture":"default.png"}})

class EditProfileHandler(RequestHandler):
	@removeslash
	@coroutine
	def post(self, field):
		field_info = self.get_argument('field','')
		print field_info
		if field=="bio" or field=="description":
			update = yield db.user_info.update({"uid":self.get_secure_cookie("user")},{"$set":{field:field_info}})

class IndexSearchHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		q = str(self.get_argument("q",''))
		db = self.settings['db']
		peopleList = questionList = people_infoquery = people_infoList = []
		q = q.split()
		questionQueryList = []
		for e in q:
			questionQueryList.append({"question":{'$regex':re.compile(e,re.IGNORECASE)}})
		peopleList = yield db.users.find({"$or":[{"first_name": {'$regex':re.compile(q[0],re.IGNORECASE)}},{"last_name": {'$regex':re.compile(q[0],re.IGNORECASE)}}]}).to_list(None)

		for people in peopleList:
			people_infoquery.append({"uid":str(people['_id'])})

		questionList = yield db.Questions.find({"$or":questionQueryList}).sort('_id', pymongo.DESCENDING).to_list(length=4)
		if len(people_infoquery):
			people_infoList = yield db.user_info.find({"$or":people_infoquery}).to_list(None)
		self.render('indexsearch.html', questionList = questionList, peopleList = peopleList, people_infoList = people_infoList)

class AnswerHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		if bool(self.get_secure_cookie("user")):
			current_id = self.get_secure_cookie("user")
			db = self.settings['db']
			result_current = yield db.users.find_one({'_id':ObjectId(current_id)})
			result_current_info = yield db.user_info.find_one({'uid':current_id})
			categories = yield db.category_list.find().to_list(None)
			questions = yield db.Questions.find({"answer_wanted":1}).sort('_id', pymongo.DESCENDING).to_list(None)
			ranlis = []
			for question in questions:
				if not current_id in question['answers']:
					ranlis.append(question)

			questions = ranlis
			notifications = yield db.notifications.find({'to':self.get_secure_cookie('user'),'read':0}).to_list(None)
			self.render('answer.html', result = dict(title = "Write Answer", loggedIn = bool(self.get_secure_cookie("user")), result_current = result_current, result_current_info = result_current_info, categories = categories, questions = questions, notifications = notifications))
		else:
			self.redirect('/?alert=NeedLogin')

class ViewAnswerHandler(RequestHandler):
	@removeslash
	@coroutine
	def get(self):
		result_current = result_current_info = None
		db = self.settings['db']
		categories = db.category_list.find()
		categories = yield categories.to_list(None)
		if bool(self.get_secure_cookie("user")):
			current_id = self.get_secure_cookie("user")
			result_current = yield db.users.find_one({'_id':ObjectId(current_id)})
			result_current_info = yield db.user_info.find_one({'uid':current_id})
		qid = self.get_argument('id','')
		question = yield db.Questions.find_one({'_id':ObjectId(qid)})
		answers = yield db.Answers.find({'qid':qid}).to_list(None)
		try:
			topanswer = sorted(answers, key=lambda k: len(k['Upvotes']), reverse=True)[0]

		except:
			topanswer =  False
		userList = yield db.users.find().to_list(None)
		userinfoList = yield db.user_info.find().to_list(None)
		answers = sorted(answers, key=lambda k: len(k['Upvotes']), reverse=True)[1:]
		notifications = yield db.notifications.find({'to':self.get_secure_cookie('user'),
			'read':0}).to_list(None)
		self.render('viewanswer.html',result = dict(title = "View Answer", loggedIn = bool(self.get_secure_cookie("user")), result_current = result_current, result_current_info = result_current_info, categories = categories, question =question, answers = answers, topanswer=topanswer, userList = userList, userinfoList = userinfoList, notifications = notifications))

	@removeslash
	@coroutine
	def post(self):
		q_id = self.get_argument("qid")
		answer = self.get_argument("answer")
		if len(answer)==0:
			self.redirect('/?alert=NoAns')
		else:
			db = self.settings['db']
			insertAnswer = yield db.Answers.insert({"qid":str(q_id),"uid":self.get_secure_cookie("user"),"Upvotes":[],"Downvotes":[],"Answer":answer})
			question = yield db.Questions.find_one({'_id':ObjectId(q_id)})
			insertNotification = yield db.notifications.insert({"type":"Q","who":self.get_secure_cookie("user"),"to":question['user'],"action":"Answer","link":str(q_id),"read":0})
			updateQuestions = yield db.Questions.update({"_id":ObjectId(q_id)},{"$push":{"answers":self.get_secure_cookie("user")}})
			self.redirect('/?alert=Ans')

class VoteHandler(RequestHandler):
	@removeslash
	@coroutine
	def post(self, vote):
		a_id = self.get_argument('a_id','')
		db = self.settings['db']
		uid = self.get_secure_cookie("user")
		answer = yield db.Answers.find_one({'_id':ObjectId(a_id)})
		if not uid in answer[vote]:
			updateAnswer = yield db.Answers.update({'_id':ObjectId(a_id)},{'$push':{vote:uid}})
			insertNotification = yield db.notifications.insert({'type':'A','who':uid,'to':answer['uid'],'action':vote,"link":answer['qid'],"read":0})
		else:
			updateAnswer = yield db.Answers.update({'_id':ObjectId(a_id)},{'$pull':{vote:uid}})
		updatedAnswer = yield db.Answers.find_one({'_id':ObjectId(a_id)})

		self.write(str(len(updatedAnswer[vote])))

class NotificationHandler(RequestHandler):
	@removeslash
	@coroutine
	def post(self):
		db = self.settings['db']
		notifications = yield db.notifications.find({'to':self.get_secure_cookie('user')}).sort('_id', pymongo.DESCENDING).to_list(None)
		users = yield db.users.find().to_list(None)
		userinfo = yield db.user_info.find().to_list(None)
		question = yield db.Questions.find().to_list(None)
		updateNotifications = yield db.notifications.update({'read':0,'to':self.get_secure_cookie('user')},{'$set':{'read':1}},multi=True)
		self.render('notifications.html', notifications = notifications, users=users, userinfo = userinfo, question = question)

settings = dict(
		db=db,
		template_path = os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static"),
		debug=True,
		cookie_secret="49fd21b3-b96b-4f18-9ff8-260c64fe10e9"
	)

#Application initialization
application = Application([
	(r"/", MainHandler),
	(r"/signup/*", SignupHandler),
	(r"/login/*", SigninHandler),
	(r"/logout/*", LogoutHandler),
	(r"/profile/?([a-zA-Z\-0-9\.:,_]+)?/*", ProfileHandler),
	(r"/categorylist/*", CategoryListHandler),
	(r"/ask/*", AskQuestion),
	(r"/upload/*", UploadHandler),
	(r"/editprofile/?([a-zA-Z\-0-9\.:,_]+)?/*", EditProfileHandler),
	(r"/indexsearch/*", IndexSearchHandler),
	(r"/answer/*", AnswerHandler),
	(r"/viewanswer/*", ViewAnswerHandler),
	(r"/vote/?([a-zA-Z\-0-9\.:,_]+)?/*", VoteHandler),
	(r"/notifications/*", NotificationHandler)
], **settings)

#main init
if __name__ == "__main__":
	server = HTTPServer(application)
	server.listen(8001)
	IOLoop.current().start()
