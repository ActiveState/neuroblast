'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

Written by Pete Garcin @rawktron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from pymongo import MongoClient
from pymongo import DESCENDING
from datetime import datetime
import pygame
from utils import *
import sys

# Initialize connect at boot
client = MongoClient('localhost', 27017)
db = client.test
scores = db.scores

def DisplayLeaderBoard(screen, highscores, name):
    y = 100
    displaytext("TOP PLAYERS", 16, 320, 50, WHITE, screen)
    for s in highscores:
        if s['name'] == name:
            color = (255, 255, 0) # YELLOW
        else:
            color = WHITE
        displaytext(s['name'], 16, 160, y, color, screen)
        displaytext(str(s['score']), 16, 480, y, color, screen)
        y+=30

    displaytext("PRESS ANY KEY TO CONTINUE", 16, 320, 640, WHITE, screen)
        
    
# TODO: Check if a player score exists, and instead add another entry instead of
# overwriting. 
def StoreScore(name,score):
    print ("Storing "+name+" score: "+str(score))
    scores.insert({"name":name,"score":score,"time":str(datetime.now())})
    
def GetScores():
    return list(scores.find().sort("score",DESCENDING).limit(10))

def ClearScores():
    scores.remove({})   

def Test():
    # Clear scores first for testing
    scores.remove({})

    scores.insert({"name":"Jilly Bo","score":400,"time":str(datetime.now())})
    scores.insert({"name":"Bob","score":1539,"time":str(datetime.now())})
    scores.insert({"name":"AAA","score":744,"time":str(datetime.now())})

    print (list(scores.find().sort("score",DESCENDING)))

# For clearing db
if (len(sys.argv) > 1) and (sys.argv[1] == '-clear'):
    ClearScores()
