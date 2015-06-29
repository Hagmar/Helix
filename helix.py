import requests as rq
import json
import threading
import hashlib

import udid
udid_test = '0000111122223333444455556666777788889999'

url_register = "https://helixgame.liseberg.se/register"
url_sessionscores = "https://helixgame.liseberg.se/sessionscores"
url_name = "https://helixgame.liseberg.se/name"
url_checkcode = "https://helixgame.liseberg.se/checkgamecode"
url_time = "https://helixgame.liseberg.se/time"
url_token = "https://helixgame.liseberg.se/requesttoken"
url_save = "https://helixgame.liseberg.se/savescore"

name = ""
done = False
code = 0
time = 0
token = ""

def main():
	calculate_hash(udid.udid, 1, "11111111111111111111111111111111")

# Register a new user or update an old one
def register(udid, new_name=""):
	if not new_name:
		new_name = name
	data = {
		'udid' : udid,
		'name' : new_name
	}
	res = rq.post(url_register, data=data)
	js = json.loads(res.text)
	print(res.text)
	try:
		if js['data']['message'] == "New user registered":
			print("Successfully registered user " + js['data']['name'])
			return 1
		elif js['data']['message'] == "User updated":
			print("User successfully updated")
			return 2
	except:
		print("Could not register user!")
	return 0

# Change your username
def rename(new_name):
	return register(udid.udid, new_name)

# Get corresponding username from a udid
def get_name():
	global name
	data = {
		'udid' : udid.udid
	}
	res = rq.post(url_name, data=data)
	js = json.loads(res.text)
	try:
		name = js['data']['name']
	except:
		print("Invalid udid!")
		return 0
	return 1

# Bruteforcing current code for playing the game
def crack_code():
	print("Bruteforcing game code...")
	threads = []
	for i in range(6):
		for j in range(6):
			thread = threading.Thread(target=crack, args=[i*1000+j*100])
			thread.start()
			threads.append(thread)
	
	for thread in threads:
		thread.join()
	print("The current code is: " + str(code))

# Bruteforce current code
def crack(start):
	global done, code
	data = {}
	for i in range(6):
		for j in range(6):
			if done:
				break
			data['code'] = "%04d" % (start+i*10+j)
			res = rq.post(url_checkcode, data=data)
			js = json.loads(res.text)
			if js['data'] != "invalid":
				done = True
				code = data['code']

# Get current server time
def get_time():
	global time
	res = rq.get(url_time)
	js = json.loads(res.text)
	try:
		time = js['data']['time']
	except:
		print("An unexpected error has occurred!")
		return 0
	return 1

# Get a game token
def get_token():
	global token
	data = {
		'udid' : udid.udid
	}
	res = rq.post(url_token, data=data)
	js = json.loads(res.text)
	try:
		token = js['data']['token']
	except:
		print("Invalid udid!")
		return 0
	return 1

# TODO
# Save a score
def save_score(score=1):
	state = calculate_hash(udid.udid, score, token)
	data = {
		'udid' : udid.udid,
		'score' : score,
		'session' : "????????????????",	#TODO
		'state' : "????????????????",	#TODO
		'version' : '2.0'
	}
	res = rq.post(url_save, data=data)
	js = json.loads(res.text)
	try:
		if js['data'] == "Success":
			print("Score saved successfully!")
			return 1
		else:
			print("Warning! The score was not saved successfully!")
			return 0
	except:
		print("An error occurred while saving the score!")
		return 0

# Calculate "state" hash
def calculate_hash(udid, score, token):
	string = udid + str(score) + token + "$1$_laZbmbx"
	hash = hashlib.md5(string.encode("utf-8"))
	state = hash.hexdigest()
	print("State hash: " + state)
	return state
	
if __name__ == '__main__':
	main()
