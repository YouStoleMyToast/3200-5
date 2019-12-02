from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json,sys
from databasehandlers import UserDB,EventDB,SessionStore
import databasehandlers
from passlib.hash import bcrypt
from http import cookies
# from Planner_db import PlannerDB

UserDB = UserDB()
EventDB = EventDB()
SessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):
    #   THE BASICS  #
    def do_OPTIONS(self):
        self.load_cookie()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()
        return

    def handle201(self):
        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes("Creation Successful", "utf-8"))

    def handle200(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("OK", "utf-8"))

    def handle404(self):
        self.load_cookie()
        self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes("<h1>Not Found</h1>", "utf-8"))

    def handle409(self):
        self.load_cookie()
        self.send_response(409)
        self.end_headers()
        self.wfile.write(bytes("<h1>User Already Exists</h1>", "utf-8"))

    def handle422(self):
        self.load_cookie()
        self.send_response(422)
        self.end_headers()
        self.wfile.write(bytes("<h1>Invalid Credentials</h1>", "utf-8"))

    def handle401(self):
        self.load_cookie()
        self.send_response(401)
        self.end_headers()
        self.wfile.write(bytes("<h1>Unauthorized</h1>", "utf-8"))

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def do_POST(self):
        if self.path.startswith("/users"):
            print("PATH: Users")
            self.handleCreateUser()
        elif self.path.startswith("/events"):
            if self.inSession():
                self.handleCreateEvent()
            else:
                self.handle401()
        elif self.path.startswith("/session"):
            self.createSession()
        
        else:
            self.handle404()

    def handleCreateEvent(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)

        name = body["name"][0]
        date = body["date"][0]
        subject = body["subject"][0]
        details = body["details"][0]

        EventDB.createEvent(name, date, subject, details)
        self.handle201()

    def handleCreateUser(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)

        firstName = body["firstName"][0]
        lastName = body["lastName"][0]
        email = body["email"][0]
        pw = body["password"][0]
        password = bcrypt.encrypt(pw)

        user = UserDB.getUserByEmail(email)
        if user == False:
            UserDB.createUser(firstName, lastName, email, password)
            user = UserDB.getUserByEmail(email)
            self.createSessionNewUser(user)
        else:
            self.handle409()

    def do_GET(self):
        pathParts = self.path.split("/")[1:]
        if len(pathParts) == 1 and pathParts[0] == "events":
            if self.inSession():
                self.handleListEvents()
            else:
                self.handle401()
        elif pathParts[0] == "users" and pathParts[1] == "login":
            self.handleLoginUser()
        elif pathParts[0] == "me" and len(pathParts) == 1:
            if self.inSession():
                data = self.load_session()
                userid = data["userID"]
                user = UserDB.getUserByID(userid)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(json.dumps(user), "utf-8"))
            else:
                self.handle401()
        else:
            self.handle404()

    def handleListEvents(self):
        events = EventDB.getAllEvents()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(events), "utf-8"))

    def handleLoginUser(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)
        email = body['email'][0]

        user = UserDB.getUserByEmail(email)
        if user != False:
            self.createSession()
        else:
            self.handle404()

    def do_DELETE(self):
        pathParts = self.path.split("/")[1:]
        if len(pathParts) < 2 and pathParts[0] != "session":  # or session
            self.handle404()
        elif pathParts[0] == "events":
            if self.inSession():
                self.handleEventDelete(pathParts[1])
            else:
                self.handle401()
        elif pathParts[0] == "session":
            self.logOut()
        return

    def handleEventDelete(self, id):
        EventDB.deleteEvent(id)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes("Item Deleted", "utf-8"))

    def do_PUT(self):
        pathlist = self.path.split("/")[1:]
        if len(pathlist) > 2:
            self.handle404()
        elif self.inSession() == False:
            self.handle401()
        elif pathlist[0] == "events":
            self.handleUpdateEvent(pathlist[1])
        elif pathlist[0] == "users":
            self.handleUpdateUser(pathlist[1])
        else:
            self.handle404()

    def handleUpdateEvent(self, id):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)

        name = body["name"][0]
        date = body["date"][0]
        subject = body["subject"][0]
        details = body["details"][0]

        EventDB.updateEvent(id, name, date, subject, details)
        self.handle200()

    def handleUpdateUser(self, id):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)

        firstName = body["firstName"][0]
        lastName = body["lastName"][0]
        email = body["email"][0]
        pw = body["password"][0]
        password = bcrypt.encrypt(pw)

        UserDB.updateUser(id, firstName, lastName, email, password)
        self.handle200

    def createSessionNewUser(self,user):
        self.load_cookie()
        sessionID = SessionStore.createSession()
        self.cookie["sessionID"] = sessionID
        SessionStore.addSessionData(sessionID,"userID",user['id'])

        data = json.dumps(user)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes(data, "utf-8"))

    def createSession(self):
        self.load_cookie()
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        body = parse_qs(body)
        email = body['email'][0]
        password = body['password'][0]

        user = UserDB.getUserByEmail(email)
        if user == False:
            self.handle422()
        else:
            user = UserDB.getUserByEmail(email)
            match = bcrypt.verify(password, user['password'])
            
            if match:
                sessionID = SessionStore.createSession()
                self.cookie["sessionID"] = sessionID
                SessionStore.addSessionData(sessionID,"userID",user['id'])
                data = json.dumps(user)
                self.send_response(201)
                self.end_headers()
                self.wfile.write(bytes(data, "utf-8"))
            else:
                self.handle422()

    def load_session(self):
        self.load_cookie() 
        if "sessionID" in self.cookie:
            sessionID = self.cookie["sessionID"].value
            data = SessionStore.getSessionData(sessionID)
            return data
        return False

    def inSession(self):
        data = self.load_session()
        if data != False:
            return True
        return False

    def logOut(self):
        self.load_cookie()
        sessionID = self.cookie["sessionID"].value
        SessionStore.delete(sessionID)
        del self.cookie
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def load_cookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def send_cookie(self):
        print("ENTER SEND_COOKIE")
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

#   START RUN SERVER
def run():
    EventDB = databasehandlers.EventDB()
    UserDB = databasehandlers.UserDB()
    EventDB.createEventsTable()
    UserDB.createUsersTable()
    EventDB = None # disconnect
    UserDB = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)
    print("Listening...")
    server.serve_forever()
run()
