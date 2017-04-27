from pymongo import MongoClient
from pymongo import DESCENDING
from datetime import datetime
import pygame
from utils import *

# Initialize connect at boot
client = MongoClient('localhost', 27017)
db = client.test
scores = db.scores

def DisplayLeaderBoard(screen, highscores):
    y = 100
    for s in highscores:
        displaytext(s['name'], 16, 100, y, WHITE, screen)
        displaytext(str(s['score']), 16, 400, y, WHITE, screen)
        y+=30
        
    

def StoreScore(name,score):
    scores.insert({"name":name,"score":score,"time":str(datetime.now())})
    
def GetScores():
    return scores.find().sort("score",DESCENDING).limit(10)

def Test():
    # Clear scores first for testing
    scores.remove({})

    scores.insert({"name":"Jilly Bo","score":400,"time":str(datetime.now())})
    scores.insert({"name":"Bob","score":1539,"time":str(datetime.now())})
    scores.insert({"name":"AAA","score":744,"time":str(datetime.now())})

    print list(scores.find().sort("score",DESCENDING))