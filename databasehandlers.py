import base64
import os
import psycopg2
import psycopg2.extras
import urllib.parse


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class UserDB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, firstName TEXT, lastName TEXT,email TEXT,password TEXT)")
        self.connection.commit()

    def createUser(self,firstName,lastName,email,password):
        self.cursor.execute('INSERT INTO users (firstName,lastName,email,password) VALUES (?,?,?,?)',[firstName,lastName,email,password])
        self.connection.commit()

    def getUserByEmail(self,email):
        self.cursor.execute('SELECT * FROM users WHERE email=?',[email])
        if self.cursor.fetchone():
            return self.cursor.fetchone
        return False

    def getUserByID(self,id):
        self.cursor.execute('SELECT * FROM users WHERE email=?',[id])
        if self.cursor.fetchone():
            return self.cursor.fetchone()
        return False

    
    def updateUser(self,id,firstName,lastName,email,password):
        self.cursor.execute('UPDATE users SET firstName=?, lastName=?, email=?, password=? WHERE id=?',[firstName,lastName,email,password,id])
        self.connection.commit()

class EventDB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createEventsTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, name TEXT, date TEXT,subject TEXT,details TEXT)")
        self.connection.commit()

    def createEvent(self,name,date,subject,details):
        self.cursor.execute('INSERT INTO events (name,date,subject,details) VALUES (?,?,?,?)',[name,date,subject,details])
        self.connection.commit()

    def getAllEvents(self):
        self.cursor.execute('SELECT * FROM events ORDER BY id')
        return self.cursor.fetchall()
    
    def deleteEvent(self,id):
        self.cursor.execute('DELETE FROM events WHERE id=?',[id])
        self.connection.commit()

    def updateEvent(self,id,name,date,subject,details):
        self.cursor.execute('UPDATE events SET name=?, date=?, subject=?, details=? WHERE id=?',[name,date,subject,details,id])
        self.connection.commit()


class SessionStore:

    def __init__(self):
        self.sessions = {}
        return

    def generateSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

    def createSession(self):
        sessionId = self.generateSessionId()
        self.sessions[sessionId] = {}
        return sessionId

    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            print("IN (GETSESSIONDATA) DATA: ",self.sessions[sessionId])
            return self.sessions[sessionId]
        else:
            return None

    def addSessionData(self,sessionID,vkey,data):
        self.sessions[sessionID].update({vkey:data})
        print(self.sessions[sessionID])
        return

    def delete(self,sessionID):
        sessionID = sessionID
        self.sessions[sessionID] = None;
        