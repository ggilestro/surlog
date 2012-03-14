#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  surlogw.py
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

import cgi, os, datetime, random
import sha, Cookie, time

import cgitb; cgitb.enable()  # for troubleshooting

from surgeryLogger import surgery, surgeries, users, surgeries_properties
from string import Template
import cPickle as pickle


url = '/cgi-bin/surlogw.py'

start_list = -30
end_list = None # shows last 30 surgeries


###########################################

class surgeryLoggerApp():
    def __init__(self):
        '''
        '''

        #values that are used in the html template
        self.v = dict(
                users_dropbox='',
                logged_user='',
                logout_link='',
                open_surgeries_table='',
                first_link='',
                second_link='',
                third_link='',
                list_title='',
                edit_surgery_title='',
                surgery_ID='',
                surgery_name='',
                surgery_status='',
                treatments_boxes='',
                surgery_comment='',
                submit_text='',
                )

        self.loadDb()
        self.loggedUser = ''
        self.page = ''

    def loadDb(self):
        '''
        '''
        #Loading the database
        self.ss = surgeries()
        self.ss.loadFromFile()


    def loadCookie(self):
        '''
        '''
        cookie = Cookie.SimpleCookie()
        string_cookie = os.environ.get('HTTP_COOKIE')
        
        if string_cookie:
            cookie.load(string_cookie)
            
        return cookie


    def newCookie(self, user=None):
        '''
        '''
        expire_time = 300
        cookie = Cookie.SimpleCookie()
        string_cookie = os.environ.get('HTTP_COOKIE')

        # If new session
        if not string_cookie or user != None:
           # The sid will be a hash of the server time
           sid = sha.new(repr(time.time())).hexdigest()
           # Set the sid in the cookie
           cookie['sid'] = sid
           # Will expire in a 300 seconds
           cookie['sid']['expires'] = expire_time
           cookie['user'] = user
           cookie['user']['expires'] = expire_time
           cookie['IP'] = cgi.escape(os.environ["REMOTE_ADDR"])
           cookie['IP']['expires'] = cgi.escape(os.environ["REMOTE_ADDR"])

        
        # If already existent session
        else:
           cookie.load(string_cookie)
           #sid = cookie['sid'].value
           #user = cookie['sid']['user']

        return cookie
        
    def deleteCookie(self):
        '''
        '''
        cookie = Cookie.SimpleCookie()
        string_cookie = os.environ.get('HTTP_COOKIE')

        if string_cookie:
            cookie.load(string_cookie)
            cookie['sid']['expires'] = 0
        
        return cookie


    def isLoggedIn(self):
        '''
        '''
        if self.loggedUser:
            user = int(self.loggedUser)
            self.v['logged_user'] = users[user]
            self.v['first_link'] = '<a href="%s?add=%s">Start a new surgery</a>' % (url, 1)
            self.v['second_link'] = '<a href="%s?listuser=%s">List all my surgeries</a>' % (url, user)
            self.v['logout_link'] = '<a href="%s?logout=1">Logout</a>' % url
        
        
    def doLogin(self, user):
        '''
        '''
        
        user = int(user)
        self.cookie = self.newCookie(user)
        self.loggedUser = self.cookie['user'].value
        
        self.page = 'list.tmpl'

    def doLogout(self):
        '''
        '''
        
        self.cookie = self.deleteCookie()
        self.loggedUser = ''

        self.page = 'login.tmpl'
    

    def addSurgery(self):
        '''
        '''
        ui = int(self.loggedUser)
        un = users[ui]

        surgery_ID = self.form.getvalue("surgery_ID", "")
        surgery_name = self.form.getvalue("surgery_name", "")
        surgery_status = self.form.getvalue("surgery_status", "")
        
        IP = cgi.escape(os.environ["REMOTE_ADDR"])
        s = self.ss.addNew(ui, surgery_name, IP)
        
        self.ss.saveToFile()
        
    def editSurgery(self, sid):
        '''
        '''

        ui = int(self.loggedUser)
        un = users[ui]
        s = self.ss.getByID( sid )

        #readonly
        surgery_ID = self.form.getvalue("surgery_ID", "")
        surgery_name = self.form.getvalue("surgery_name", "")
        surgery_status = self.form.getvalue("surgery_status", "")

        #modifiable
        surgery_comment = self.form.getvalue("surgery_comment", "")
        chk_started = self.form.getvalue("chk_started", "")
        chk_finish = self.form.getvalue("chk_finish", "")
        chk_saline = self.form.getvalue("chk_saline", "")
        chk_recovered = self.form.getvalue("chk_recovered", "")
        chk_first_check = self.form.getvalue("chk_first_check", "")
        chk_second_check = self.form.getvalue("chk_second_check", "")
        chk_aborted = self.form.getvalue("chk_aborted", "")

        s.comment = surgery_comment

        if chk_started == 'on': s.stampProperty('started')
        if chk_finish == 'on': s.stampProperty('finish')
        if chk_saline == 'on': s.stampProperty('saline')
        if chk_recovered == 'on': s.stampProperty('recovered')
        if chk_first_check == 'on': s.stampProperty('first_check')
        if chk_second_check == 'on':
            s.stampProperty('second_check')
            s.Close()
        if chk_aborted == 'on': s.stampProperty('aborted')
            
        
        self.ss.saveToFile()

    def export(self):
        '''
        '''
        #Exporting
        #if user and export:
        if int(user) < 0 : u = None
        else: u = int(user)
        csv = self.ss.exportAsCSV( u )
        header = "Content-type: text/csv\nContent-disposition: attachment; filename=surgery_table.csv\n\n"
        print header + csv
        os.sys.exit()


    def loginPage(self):
        '''
        '''
        #if not user and not export:
            
        self.v['submit_text'] = 'Login'

        for i,u in enumerate(users):
            self.v['users_dropbox'] += '<option value="%s">%s</option>\n' % (i,u)

        self.page = 'login.tmpl'

    def listUserPage(self):
        '''
        '''

        ui = int(self.loggedUser)
        un = users[ui]

        self.v['list_title'] = '%s\'s recent surgeries' % un

        table  =  "<table class=\"altrowstable\" id=\"alternatecolor\">"
        table +=  "<tr><td>#%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % ('ID', 'Name', 'Started on', 'Closed on', 'Edit')

        for s in self.ss.surgeriesFromUser(ui)[start_list:end_list]:
            
            isOpen = [ s.getEndTime(), '<strong>Open</strong>' ][s.isOpen()]
                
            table += "<tr><td>#%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href=\"%s?edit=%s\">Edit</a></td></tr>\n" % (s.sid, s.name, s.getStartTime(), isOpen, url, s.sid)

        table += "</table>"

        self.v['open_surgeries_table'] = table

        self.page = 'list.tmpl'


    def listAllPage(self):

        #Listing all users surgeries
        #if listall:
        
        table  =  "<table class=\"altrowstable\" id=\"alternatecolor\">"
        table +=  "<tr><td>#%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % ('ID', 'User', 'Name', 'Started on', 'Closed on')

        allSurgeries = self.ss.surgeriesFromUser()[start_list:end_list]
        if int(listall) == 2 : allSurgeries = [s for s in allSurgeries if s.isOpen()]

        for s in allSurgeries:
            
            isOpen = [ s.getEndTime(), '<strong>Open</strong>' ][s.isOpen()]
                
            table += "<tr><td>#%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (s.sid, users[s.user], s.name, s.getStartTime(), isOpen)
        
        table += "</table>"
        
        self.v['open_surgeries_table'] = table

        self.page = 'list.tmpl'

    def addPage(self):
        '''
        '''

        self.v['edit_surgery_title'] = '<h3>Start a new surgery</h3><div>Create a new surgery log</div>'
        self.v['surgery_ID'] = self.ss.getNewID()
        self.v['surgery_status'] = 'Opening now'
        self.v['submit_text'] = 'Create new surgery'

        self.page = 'new.tmpl'

    def editPage(self, sid=None, new=False):
        '''
        '''

        if new:
            self.v['edit_surgery_title'] = '<h3>Surgery parameters</h3><div></div>'
            s = self.ss.getLastAdded()
            self.v['surgery_ID'] = s.sid

        else:
            self.v['edit_surgery_title'] = '<h3>Edit an existing surgery</h3><div></div>'
            s = self.ss.getByID(sid)
            self.v['surgery_ID'] = sid

        self.v['surgery_name'] = s.name


        if s.isOpen(): self.v['surgery_status'] = 'Open on %s' % s.getStartTime()
        else: self.v['surgery_status'] = 'Closed on %s' % s.getEndTime()
            
        checkboxes = '<table>'

        for k in surgeries_properties:
            va = s.properties[k]
            ce = ['disabled',''] [(s.timeFromStart() >= va[0] )]            #can Edit
            ck = ['','checked'] [ va[1] != False ] #isChecked
            description = va[2]
            prp_time = s.getPropertyTime(k)
            if k == 'aborted' :
                onclick = "onclick=\"$(this).is(':checked') && $('#reason').slideDown('slow') || $('#reason').slideUp('slow');\" "
            else:
                onclick = ''

            checkboxes += '<tr><td width=500px><input %s type="checkbox" name="chk_%s" %s %s /><label class="choice">%s</label></td><td>%s</td></tr>\n' % (ce, k, ck, onclick, description, prp_time)


        abortReason = "<tr><td><div id=\"reason\" class=\"required\" style=\"display: none; margin: 10px; height: 50px; background-color: #f5f5f5; padding: 10px\" ><label>Enter reason for aborting</label><input type=\"text\" name=\"abortReason\" size=40></div></td></tr>\n"


        checkboxes += abortReason

        checkboxes += '</table>'

        
        self.v['surgery_comment'] = s.comment
        self.v['treatments_boxes'] = checkboxes

        self.page = 'edit.tmpl'
        self.v['submit_text'] = 'Modify surgery data'


    def elaborateInput(self):
        '''
        '''
        #Getting URL parameters
        self.form = cgi.FieldStorage()

        #actions
        login = self.form.getvalue("login", "")
        logout = self.form.getvalue("logout", "")
        edit = self.form.getvalue("edit", "")
        add = self.form.getvalue("add", "")
        export = self.form.getvalue("export", "")
        listall = self.form.getvalue("listall", "")
        listuser = self.form.getvalue("listuser", "")

        added_new = self.form.getvalue("added_new", "")
        modified = self.form.getvalue("modified", "")

        ##
        self.cookie = self.loadCookie()
        if self.cookie: self.loggedUser = self.cookie['user'].value
        
        if login: self.doLogin(login)
        if logout: self.doLogout()
        
        if self.loggedUser:
            
            self.isLoggedIn()
        
            if edit and not modified: self.editPage(int(edit))

            elif add: self.addPage()

            elif listall: self.listAllPage()

            elif export: self.export()

            elif listuser: self.listUserPage()

            elif added_new: 
                self.addSurgery()
                self.editPage(new=True)

            elif modified:
                self.editSurgery(int(modified))
                self.editPage(int(modified))

            else: self.listUserPage() # Default page
        
        else:
            self.loginPage()
            
        
    def printOutput(self):
        '''
        '''
        if self.page:
        
            template_header = '/srv/http/surlog/header.tmpl'
            template_body = '/srv/http/surlog/' + self.page
            
            fh1 = open (template_header, 'r')
            fh2 = open (template_body, 'r')
            template = fh1.read() + fh2.read()
            fh1.close()
            fh2.close()

            cookie = self.cookie.output()
            if cookie: cookie += '\n'

            html_header = "Content-type: text/html\n\n"
            html_output = Template( template )

            if cookie:
                print cookie, html_header , html_output.substitute( self.v )
            else:
                print html_header , html_output.substitute( self.v )

if __name__ == '__main__':
    
    app = surgeryLoggerApp()
    app.elaborateInput()
    app.printOutput()
    

