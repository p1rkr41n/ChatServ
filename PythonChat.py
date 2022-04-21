import ast
from cmath import e
import re
import sys
import socket
import sqlite3
import datetime
import json
import time
import random
import threading
# from traceback import print_tb
# from unittest import result
from createSqlite import createSqlChat
import hashlib

class chatDB:
    """Database for chat
    Support multiple-thread accesses
    """

    def __init__(self, path, createNew=False):
        """Init chatdb
        Connect to database (at PATH) or create new one if CREATENEW = True
        """
        if createNew == True:
            createSqlChat()
        # You have to implement this method
            # self.start()
        pass

    def start(self):
        """Start background tasks of chat db.

        Background tasks: cookie cleaner
        """
        # You have to implement this method
        clearCookies = threading.Thread(target= self.autoClear)
        clearCookies.start()

        pass

    def stop(self):
        """Stop background tasks of chat db.

        Background tasks: cookie cleaner
        """
        # You have to implement this method
        pass

    def autoClear(self):
        """
        Clear inactive cookie. Timeout = 600
        Should be called in self.start
        """
        # You have to implement this method
        time.sleep(599)
        while True:
            self.excuteSql("DELETE FROM Cookies WHERE Last_acc < " + str(int(time.time())-600))
            countdown = self.excuteSql("SELECT Last_acc FROM Cookies WHERE Cookie = (SELECT min(Cookie) FROM Cookies )")
            # SELECT * FROM Cookies WHERE Cookie = (SELECT min(Cookie) FROM Cookies ) # get element min
            print("Recount")
            try:
                time.sleep(countdown[0][0])
            except:
                time.sleep(600)
            pass
        pass

    def getOnlineUsers(self):
        return( self.convertToList(self.excuteSql("SELECT Users.User as username FROM Users WHERE Status =1")))
        """Get all online users

        Return: list of online users
        """
        # You have to implement this method
        pass

    def getAllUsers(self):
        return (self.convertToList(self.excuteSql("SELECT Users.User as username FROM Users")))
        """Get all online users

        Return: list of all users
        """
        # You have to implement this method
        pass

    def getAllMsgs(self, cookie, usr2):
        """Return all messages between owner of COOKIE and USR2.
        All new messages will be set to be already read.

        Return value:
            + 'invalid_usr': if usr is invalid
            + 'invalid_cook': if cookie is invalid
            + [[sender, receiver, content, time, status],...]
                example: [['manh', 'thanh', 'Hello', '2018-20-06 18:21:26', 'yet']]
        """
        # You have to implement this method
        self.updateTimeStamp(cookie)
        Recv =  self.excuteSql("SELECT User FROM Cookies WHERE Cookie = '"+ cookie +"'")
        Sender =  self.excuteSql("SELECT User FROM Users WHERE User = '"+ usr2 +"'")
        if Recv  != []:    
            if Sender != []:
                try:
                    # GET all messege sql
                    return self.convertToList(self.excuteSql("SELECT * FROM Msgs WHERE (Sender = '"+ Sender[0][0] +"' OR Sender = '"+ Recv[0][0] +"') and ( Receiver = '"+ Recv[0][0] +"' OR Receiver = '"+ Sender[0][0] +"') ORDER BY Timestamp ASC")) 
                except:
                    return 'invalid_usr'
        else :
            return "invalid_cook"

        pass
    def getNewMsgs(self, cookie, frm):
        """Return all new messages from FRM sending to owner of COOKIE.
        All those new messages will be set to be already read.

        Return value:
            + 'invalid_usr': if usr is invalid
            + 'invalid_cook': if cookie is invalid
            + [[content, time],...]
                example: [['Hello', '2018-20-06 18:21:26']]
        """ 
        # You have to implement this method
        self.updateTimeStamp(cookie)
        Sender =  self.excuteSql("SELECT User FROM Cookies WHERE Cookie = '"+ cookie +"'")
        Recv =  self.excuteSql("SELECT User FROM Users WHERE User = '"+ frm +"'")
        if Sender  != []:    
            if Recv != []:
                try:
                    # GET all messege sql
                    return self.convertToList(self.excuteSql("SELECT Content, Timestamp FROM Msgs WHERE Sender = '"+ Sender[0][0] +"' and Receiver = '"+ Recv[0][0] +"'"))
                except:
                    return 'invalid_usr'
        else :
            return "invalid_cook"

        pass

        pass

    def sendMsg(self, cookie, to, content):
        """Send message with content CONTENT from owner of COOKIE to TO.

        The time will be set to the current time on server.

        Return value:
            + 'invalid_usr': if usr is invalid
            + 'invalid_cook': if cookie is invalid
            + 'success'
        """
        # You have to implement this method
        self.updateTimeStamp(cookie)
        Sender =  self.excuteSql("SELECT User FROM Cookies WHERE Cookie = '"+ cookie +"'")
        Recv =  self.excuteSql("SELECT User FROM Users WHERE User = '"+ to +"'")
        if Sender  != []:    
            if Recv != []:
                try:
                    self.excuteSql("INSERT INTO Msgs VALUES ('" + Sender[0][0] + "','" + Recv[0][0] + "','" + content + "','" + str(int(time.time())) + "',0)")
                    return 'success'
                except:
                    return 'invalid_usr'
        else :
            return "invalid_cook"

        pass

    def register(self, usr, wd):
        """Register user USR with word WD

        USR must be a 3-10 byte string.
        Return:
            'success': register successfully
            'invalid_usr': failed. The user name is not valid.
            'invalid_': failed. The word is not valid.
        """
        # You have to implement this method
        if len(usr) < 3 or len(usr) > 10:
            return 'invalid_usr'
        elif len(wd) < 3 or len(wd) > 10:
            return 'invalid_wd'
        else:
            try:
                hashpwd = hashlib.sha1(wd.encode()).hexdigest()
                self.excuteSql("INSERT INTO Users VALUES ('" + usr + "','" + hashpwd + "',0)")
                return 'success'
            except :
                return 'invalid_usr'
        pass

    def login(self, usr, wd):
        """Set user USR as logged in.

        Return:
            ['success', cookie]: login successfully. Cookie is a string specify the session.
            'invalid_usr': login failed because of invalid user name.
            'invalid_wd': login failed because of wrong word.
        """
        # You have to implement this method
        hashpwd = hashlib.sha1(wd.encode()).hexdigest()
        try:
            self.excuteSql("SELECT 1 FROM Users WHERE User = '" + usr + "' AND Passwd='" + hashpwd +"'" )[0]
            self.excuteSql("UPDATE Users SET Status = 1 WHERE User = '" + usr + "'" )
            cookie = ''.join((random.choice('0123456789') for i in range(16)))
            timestamp =str(int(time.time()))
            # print("INSERT INTO Cookies VALUES ('" + cookie + "','" + usr + "', '" + timestamp + "') " )
            while True:
                try:
                    self.excuteSql("INSERT INTO Cookies VALUES ('" + cookie + "','" + usr + "', '" + timestamp + "') ")
                    break
                except:
                    if cookie == "9"*16:
                        cookie= "0"*16
                    cookie = format(str(int(cookie) + 1), '016d')

            return ['success', cookie]
        except e:
            # print(e)
            return 'invalid_usr'
            # return e
        pass

    def logout(self, cookie):
        """Set owner of cookie as logged out
        Remove cookie from database

        Return:
            'success': log-out successfully
            'invalid': log-out failed. The cookie does not exist.
        """
        # You have to implement this method
        try:
            self.excuteSql("DELETE FROM Cookies WHERE Cookie = '" + cookie + "'")
            return 'success'
        except:
            return 'invalid'
        pass
        
    # you can define more method here
    def excuteSql(self, query):
        connection = sqlite3.connect('./chat.sqlite')
        cursor = connection.cursor()
        result = cursor.execute(query).fetchall()
        connection.commit()
        return result
    def convertToList(self, result):
        resultList = []
        for i in result:
            resultList.append([])
            for j in i:
                resultList[-1].append(str(j))
        return resultList
    def updateTimeStamp(self, cookie):
        self.excuteSql("UPDATE Cookies SET Last_acc = '" + str(int(time.time())) + "' WHERE Cookie = '" + cookie + "'")
    # Clear cookies

class ThreadedServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self, maxClient):
        self.sock.listen(maxClient)
        while True:
            client, address = self.sock.accept()

            threading.Thread(target=self.listenToClient,
                             args=(client, address)).start()

    def listenToClient(self, client, address):
        recvBuf = ''
        while True:
            data = self.recvLine(client, recvBuf)
            print (data)
            if type(data) == list:
                ###
                # log down error, may be into db
                ###
                return 
            else:
                # convert string representation of any type to that type
                try:
                    request = ast.literal_eval(data)
                    response = self.processRequest(request)
                except:
                    response = "invalid"
                # convert any type of response to string representation
                data = str(response)
                try:
                    client.send(data+'\n')
                except err:
                    client.close()
                    ###
                    # log down error, may be into db
                    ###
                    return  # data = 'Hello\nHello'

    def recvLine(self, client, recvBuf):  # receive line from client
        while '\n' not in recvBuf:
            try:
                data = client.recv(1024)
                if data:
                    recvBuf += data
                # else:
                #     return [False, 'disconnected']
            except:
                client.close()
                return [False, 'error']
        lineEnd = recvBuf.index('\n')
        data = recvBuf[:lineEnd]
        recvBuf = recvBuf[lineEnd+1:]
        return data

    def processRequest(self, request):
        global chatdb
        if self.regex(request):
            if request[0] == 'ONLINE' :
                return chatdb.getOnlineUsers()
            elif request[0] == 'ALL' :
                return chatdb.getAllUsers()
            elif request[0] == 'GET' :
                return chatdb.getAllMsgs(request[1], request[2])
            elif request[0] == 'NEW' :
                return chatdb.getNewMsgs(request[1], request[2])
            elif request[0] == 'SEND' :
                return chatdb.sendMsg(request[1], request[2], request[3])
            elif request[0] == 'REG' :  
                return chatdb.register( request[1], request[2] )
            elif request[0] == 'LOGIN' : 
                return chatdb.login(request[1], request[2])
            elif request[0] == 'LOGOUT' :
                return chatdb.logout(request[1])
            else:
                return 'invalid'
        else:
            return 'invalid'
        """Process a request of a client
	    A request is in the form:
	        ['ONLINE'] => getOnlineUsers
	        ['ALL'] => getAllUsers
	        ['GET', cookie, usr2] => getAllMsgs
	        ['NEW', cookie, frm] => getNewMsgs
	        ['SEND', cookie, to, content] => sendMsg
	        ['REG', usr, wd] => register
	        ['LOGIN', usr, wd] => login
	        ['LOGOUT', cookie] => logout
	    """
        # You have to implement this method
        pass
    def regex(self, request):
        check = ""
        for i in request:
            check += i
        if check.find('[') != -1 or check.find(']') != -1 or check.find('\n') != -1 or  check.find('\\') != -1 or  check.find('"') != -1 :
            return False
        else:
            return True

chatdb = None
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage: %s <port> <dbFile> <createNew>" % sys.argv[0]
        print "Example: %s 8081 chat.sqlite new" % sys.argv[0]
        exit(1)
    port = int(sys.argv[1])
    dbFile = sys.argv[2]
    createNew = sys.argv[3]
    if createNew == 'new':
        createNew = True
    else:
        createNew = False
    

    chatdb = chatDB(dbFile, createNew)
    chatdb.start()

    ThreadedServer('', port).listen(50)
