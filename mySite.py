# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
import utils
import nltk
import csv
import pandas as pd
from twilio.rest import Client
import sqlite3
from datetime import datetime

account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

login_status = 0

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"

@app.route('/', methods=['GET', 'POST'])
def register():
	error = None
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			num = request.form['num']
			
			users = {'Name':request.form['name'],'Email':request.form['email'],'Contact':request.form['num']}
			df = pd.DataFrame(users,index=[0])
			df.to_csv('users.csv',mode='a',header=False)

			sec = {'num':num}
			df = pd.DataFrame(sec,index=[0])
			df.to_csv('secrets.csv')

			name = request.form['name']
			num = request.form['num']
			email = request.form['email']
			password = request.form['password']
			age = request.form['age']
			gender = request.form['gender']

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT Name from Users WHERE Name='{name}' AND password = '{password}';")
		
			if(cursorObj.fetchone()):
				error = "User already Registered...!!!"
			else:
				now = datetime.now()
				dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Contact text,Email text,password text,age text,gender text)")
				cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?)",(dt_string,name,num,email,password,age,gender))
				con.commit()

				return redirect(url_for('login'))

	return render_template('register.html',error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	global login_status
	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Name='{name}' AND password = '{password}';")

		if(cursorObj.fetchone()):
			return redirect(url_for('home'))
			login_status = 1
		else:
			error = "Invalid Credentials Please try again..!!!"
	return render_template('login.html',error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/info', methods=['GET', 'POST'])
def info():
	return render_template('info.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
	return render_template('contact.html')

@app.route('/bulk', methods=['GET', 'POST'])
def bulk():
	global login_status
	'''
	print(login_status)
	if login_status != 1:
		return redirect(url_for('login')) 
	'''
	if request.method == 'POST':
		company = request.form["company"]
		mgs = request.form["mgs"]
		categeory = request.form["categeory"]
		#print(mgs)
		#print(categeory)
		df = pd.read_csv('mgs/'+categeory+'.csv')
		#print(df.to_string())

		nums = df.values.tolist()
		#print(nums)

		for num in nums:
			message = client.messages \
			.create(
					body=company+":\n"+mgs,
					from_='+',
					to='+91' + str(num[0])
				)
			#print(message.sid)
		

	return render_template('bulk.html')

@app.route('/input',methods=['GET', 'POST'])
def input():
	'''
	global login_status
	if login_status != 1:
		return redirect(url_for('login')) 
	'''
	if request.method == 'POST':
		name = request.form["name"]
		contact = request.form["contact"]
		items = request.form["items"]
		print(name)
		print(contact)
		print(items)
   
		
		utils.export("data/"+contact+".txt", items, "w")
				
		data = utils.getTrainData()
		print(data)
		
		def get_words_in_tweets(tweets):	
			all_words = []
			for (words, sentiment) in tweets:
	  			all_words.extend(words)
			return all_words

		def get_word_features(wordlist):		
		
			wordlist = nltk.FreqDist(wordlist)
			word_features = wordlist.keys()
			return word_features

		word_features = get_word_features(get_words_in_tweets(data))		
		


		def extract_features(document):		
			document_words = set(document)
			features = {}
			for word in word_features:
				#features[word.decode("utf8")] = (word in document_words)
				features[word] = (word in document_words)
			#print(features)
			return features

		allsetlength = len(data)
		print(allsetlength)		
		#training_set = nltk.classify.apply_features(extract_features, data[:allsetlength/10*8])		
		training_set = nltk.classify.apply_features(extract_features, data)
		#test_set = data[allsetlength/10*8:]		
		test_set = data[88:]		
		classifier = nltk.NaiveBayesClassifier.train(training_set)			
		
		def classify(purchase):
			return(classifier.classify(extract_features(purchase.split("\n"))))
			
				
			
		f = open("data/"+ contact+".txt", "r")
		f = [line for line in f if line.strip() != ""]	

		clothing=0
		grocery=0
		sports=0
		electronics=0
		vegetables=0

		for item in f:
			result = classify(item)
			if(result == "clothing"):
				clothing = clothing + 1
			elif(result == "grocery"):
				grocery = grocery + 1
			elif(result == "sports"):
				sports = sports + 1
			elif(result == "electronics"):
				electronics = electronics + 1
			elif(result == "vegetables"):
				vegetables = vegetables + 1
		cat = [clothing,electronics,grocery,sports,vegetables]
		print(cat)
		idx = cat.index(max(cat))
		if(idx == 0):
			result = "clothing"
		elif(idx == 1):
			result = "electronics"
		elif(idx == 2):
			result = "grocery"
		elif(idx == 3):
			result = "sports"
		elif(idx == 4):
			result = "vegetables"

		with open('mgs/'+result+'.csv') as f:
			reader = csv.reader(f)
			data = list(reader)
			print(data)
			f.close()

		if([contact] not in data):
			with open('mgs/'+result+'.csv', 'a') as f:
				writerObj = csv.writer(f)
				writerObj.writerow([contact])
				f.close()

		
		print(result)
		return render_template('input.html')
				
	return render_template('input.html')   


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, threaded=True)
