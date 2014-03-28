#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  surgery_logger.py
#  
#  Copyright 2012 Giorgio Gilestro <giorgio@gilest.ro>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

__author__ = "Giorgio Gilestro <giorgio@gilest.ro>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2012/03/01 21:57:19 $"
__copyright__ = "Copyright (c) 2011 Giorgio Gilestro"
__license__ = "Python"

import cPickle as pickle
import datetime as dt
from time import time

FILENAME = 'surgeries.cp'

users = [   'Reviewer',
            'Eleonora Steinberg',
            'David R Carr',
            'Rowan Baker',
            'Valentina Ferretti',
            'Anna Y Zecharia',
            'Qianzi Yang',
            'Zhe Zhang',
            'Zhiwen Ye',
            'Xiao Yu',
            'Cigdem Gelegen Van Eijl',
            'Edward Harding',
            'David Uygun',
            'Catriona M Houston'
        ] 

surgeries_properties = ['started', 'finish', 'saline', 'recovered', 'health_check', 'aborted']

#############################

class user():
    def __init__(self):
        '''
        '''
        self.availableUsers = []
        self.filename = 'users.cp'
        self.defaultUsersList = [ {'Name' : 'Reviewer', 'email' : ''} ]
        
    def loadUsers(self):
        '''
        '''
        try:
            self.availableUsers = pickle.load( open( self.filename, "rb" ) )
        except:
            self.availableUsers = dict()
        
    def importUsers(self, filename):
        '''
        Import list of users from text file
        format should be:
        
        Fullname   email@address
        '''
        users = []
        f = open(filename, 'r')
        fc = f.read()
        for row in fc:
            r = row.split('\t')
            users.append( { 'Name' : r[0], 'email' : r[1] } )
            
        
    def saveUsers(self):
        '''
        '''
        pickle.dump( self.availableUsers, open( self.filename, "wb" ) )
        
    
    def setCurrentUser(self, uid):
        '''
        '''
        self.currentUser = self.availableUsers[uid]

class surgery():
    def __init__(self, sid, name, user, opened, IP=None):
        '''
        id is the unique number identifier
        user is the number related to the user who performed surgery
        started, ended are dates
        properties is a dictionary of mainly timestamps
        '''
        self.sid = int(sid)
        self.name = name
        self.user = user
        self.opened = opened
        self.ip = IP
        self.ended = False
        self.aborted = ''
        #name: [min_time, value, description, order]
        self.properties =  { 'started' : [0, False, 'Start surgery', 0],
                             'finish' : [0, False, 'Finish surgery & animal in recovery area', 1],
                             'saline' : [0, False, 'Saline & post-operative drugs given', 2],
                             'recovered' : [10, False, 'Animal behaving normally & back in home cage', 3],
                             'health_check' : [0, False, 'Follow up check - ideally next day', 5 ],
                             'aborted' : [0, False, 'Abort this surgery (must specify reason)', 0]
                             }
                             
        self.comment = ''
                                 
    def listProperties(self):
        '''
        '''
        return surgeries_properties
        
    def getPropertyTime(self, p):
        '''
        '''
        if self.properties.has_key(p) and self.properties[p][1]:
            t = self.properties[p][1]
            return self.formatTime(t).strftime('%d-%m-%y %H:%M')
        else:
            return 0
    
    def timeFromStart(self):
        '''
        return how many minutes have elapsed since the surgery started
        '''
        delta = dt.datetime.now() - self.formatTime( self.opened )
        return int ( delta.seconds / 60 )
    
    
    def Close(self):
        '''
        Surgery ended
        '''
        if not self.ended:
            self.ended = time() # Time as unix timestamp
            return True
        else:
            return False        #Surgery is already closed!


    def stampProperty(self, prp):
        '''
        '''
        if not self.properties[prp][1]:
            self.properties[prp][1] = time()


    def addEvent(self, eventname):
        '''
        '''

        if eventname in self.properties and ( self.properties[eventname][0] <= self.timeFromStart() ):
       
            self.properties[eventname][1] = time()
            return True
        else:
            return False
        
    def addComment(self, comment):
        '''
        '''
        self.comment = comment
    
    
    def formatTime(self, ts):
        '''
        '''
        if ts:
            return dt.datetime.fromtimestamp(ts)
        else:
            return 0
            
    def isOpen(self):
        '''
        '''
        return (self.ended == False)
        
    
    def isAborted(self):
        '''
        '''
        return self.aborted
    
    def getStartTime(self):
        '''
        '''
        return self.formatTime(self.opened).strftime('%d-%m-%y %H:%M')

        
    def getEndTime(self):
        '''
        '''
        if self.ended:
            return self.formatTime(self.ended).strftime('%d-%m-%y %H:%M')

        else:
            return ''
    
    def getUserName(self):
        '''
        '''
        return users[self.user]
    
    def canModifyProperty(self, prp):
        '''
        '''
        priorChecked = True
        
        all_prps = self.listProperties()
        prp_min_time = self.properties[prp][0]
        
        time_has_elapsed = ( self.timeFromStart() >= prp_min_time )
        
        pos = all_prps.index(prp)
        for k in all_prps[:pos]:
            priorChecked &= ( self.properties[k][1] != False )
        
        if self.properties[prp][3] == 0: priorChecked = True

        return time_has_elapsed & priorChecked & self.isOpen()
    
    def isPropertyChecked(self, prp):
        '''
        '''
        return ( self.properties[prp][1] != False )
    
class surgeries():
    def __init__(self):
        self.l = []
        self.filename = FILENAME
    
    
    def saveToFile(self):
        '''
        '''
        pickle.dump( self.l, open( self.filename, "wb" ) )
        
    def loadFromFile(self):
        '''
        '''
        try:
            self.l = pickle.load( open( self.filename, "rb" ) )
        except:
            self.l = []
        
    
    def getNewID(self):
        '''
        '''
        return len(self.l)
        
        
    def hasSurgery(self, sid):
        '''
        '''
        for s in self.l:
            if sid == s.sid: return True
            
        return False
        
    def getByID(self, sid):
        '''
        '''
        for s in self.l:
            if sid == s.sid: return s
        
        return False
        
    def getLastAdded(self):
        '''
        '''
        return self.l[-1]
        
    def addNew(self, username, name, IP=None):
        '''
        '''
        newSurgery = surgery( sid = self.getNewID(),
                              name = name,
                              user = username,
                              opened = time()
                            )
                            
        self.l.append(newSurgery)
        return self.l[-1]
        

    def getInfo(self, sid):
        '''
        '''
        if self.hasSurgery(sid):
            s = self.l[sid]
            
            d = { 'username' : s.user,
                  'started' : s.getStartTime(),
                  'ended' : s.getEndTime(),
                  'isOpen' : s.isOpen(),
                  'properties' : s.properties,
                  'comment' : s.comment
                }
            
            return d
            
        else:
            return 0
       

    def surgeriesFromUser(self, uid=None):
        '''
        '''
        if uid != None:
            return [s for s in self.l if s.user == uid]
        else:
            return self.l
            

    def userOpenSurgeries(self, uid):
        '''
        '''
        lu = self.surgeriesFromUser(uid)
        return [s for s in lu if s.isOpen()]

    def exportAsCSV(self, uid=None):
        '''
        '''
        csv = ''
        
        if uid:
            lu = self.surgeriesFromUser(uid)
        else:
            lu = self.l
        
        #header
        csv += ','.join( ['ID', 'Name', 'User', 'Opened', 'Ended', 'IP'] + [ k for (k,v) in lu[0].properties.items() ]) + '\n'
        
        for s in lu:
            lp = [s.sid, s.name, s.user, s.getStartTime(), s.getEndTime(), s.ip] + [ s.getPropertyTime(k) for (k,v) in s.properties.items() ]
            csv += ','.join( [str(i) for i in lp] ) + '\n'
            
        return csv


def test():
    
    ss = surgeries()
    ss.addNew(0, 'Rat #23'); ss.addNew(0, 'Rat #24'); ss.saveToFile()
    #ss.loadFromFile()
    print ss.getInfo(0)
    print ss.userOpenSurgeries(0)
    

if __name__ == '__main__':
    test()

