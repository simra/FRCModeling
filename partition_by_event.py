from __future__ import print_function
#import time
import swagger_client as v3client
from swagger_client.rest import ApiException
from pprint import pprint
import pickle
import os

filename = 'matches.pkl'
matches = []
with open(filename, 'rb') as f:
    matches = pickle.load(f)

#print(len(matches))

events = {}

for m in matches:
    if m.event_key not in events:
        events[m.event_key]=[]
    events[m.event_key].append(m)

for e in events:
    #with open('event_features_{}.txt'.format(e),'w',encoding='utf-8') as outFile: 
    outFile = open('event_features_{}.txt'.format(e),'w',encoding='utf-8')
    for m in events[e]:
        red = ' '.join(m.alliances.red.team_keys)
        blue = ' '.join(m.alliances.blue.team_keys)
        label = str(int(m.winning_alliance == 'red'))
        outFile.write('\t'.join([label,red,blue])+'\n')
    outFile.close()
    
#2019pncmp
#2019waahs
#2019wasno