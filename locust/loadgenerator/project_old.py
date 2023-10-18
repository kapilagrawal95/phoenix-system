from .socketio import *
import gevent
import random
import os
import re
import string
import uuid
import json
from . import ROOT_PATH, csrf, randomwords
# from gevent.hub import ConcurrentObjectUseError
from locust import TaskSet, task
import time
# from locust.event import request

current_milli_time = lambda: int(round(time.time() * 1000))
# pos_triggered = pos_registered = 0 #delete this in the end

# PAGE_TASKS  = os.environ.get("PAGE_TASKS", '')


# class Websocket():
#     def __init__(self, page):
#         self.c = Client(page)
#         self.l = page
#         self.sent_doc_version = 0
#         self.pending_text = None
#         # self.c.on("clientTracking.clientUpdated", self.noop)
#         self.c.on("clientTracking.clientUpdated", self.on_update_position)
#         self.c.on("clientTracking.clientDisconnected", self.noop)
#         self.c.on("new-chat-message", self.on_chat)
#         self.c.on("reciveNewFile", self.noop)
#         self.c.on("connectionAccepted", self.noop)
#         self.c.on("otUpdateApplied", self.update_version)

#         self.emit("joinProject", [{"project_id": page.project_id}], id=1)
#         with gevent.Timeout(5000, False):
#             m = self.c.recv()
#             self.root_folder =  m["args"][1]["rootFolder"][0] if len(m["args"]) > 1 else None
#             self.main_tex = m["args"][1]["rootDoc_id"] if len(m["args"]) > 1 else None
#             if self.root_folder:
#                 page.imgs = [file['_id'] for file in self.root_folder['fileRefs']]
#             self.emit("joinDoc", [self.main_tex], id=2)
#             old_doc = self.c.recv()
#             self.doc_text = "\n".join(old_doc["args"][1])
#             self.doc_version = old_doc["args"][2]
#             self.emit("clientTracking.getConnectedUsers", [], id=3)
#             self.c.recv()
#         assert self.doc_version is not None


#     def recv(self): self.c.recv()

#     def update_version(self, args):
#         rec_ts = current_milli_time()

#         if 'client_ts' in args[0] and self.sent_doc_version != args[0]["v"]:
#             # print (rec_ts - args[0]['client_ts'])
#             request.fire(request_type='WebSocket',
#                                 name="update_text",
#                                 response_time=rec_ts - args[0]['client_ts'],
#                                 response_length=0)
#             # print("update in %s ms" % str(rec_ts - args[0]['client_ts']))

#         # if self.sent_doc_version != args[0]["v"]:
#         #     print('user %s saw an update it didn\'t emit' % (self.l.parent.email))

#         self.doc_version = args[0]["v"]+1
#         if self.pending_text is not None:
#             self.doc_text = self.pending_text
#             self.pending_text = None


#     def noop(self, args):
#         pass


#     pos_triggered = pos_registered = 0
#     def on_update_position(self, args):

#         rec_ts = current_milli_time()
#         if 'client_ts' in args[0] and self.l.parent.email != args[0]['email']:
#             request.fire(request_type='WebSocket',
#                                 name="update_cursor_position",
#                                 response_time=rec_ts - args[0]['client_ts'],
#                                 response_length=0)
#             # print('user %s saw user %s moving at [%s:%s]' % (self.l.parent.email, args[0]['email'], args[0]['row'], args[0]['column']))

#             global pos_registered
#             pos_registered += 1

#         pass

#     def on_chat(self, args):

#         rec_ts = current_milli_time()
#         if 'client_ts' in args[0] and self.l.parent.email != args[0]['user']['email']:
#             request.fire(request_type='WebSocket',
#                                 name="receive_chat_message",
#                                 response_time=rec_ts - int(args[0]['client_ts']),
#                                 response_length=0)
#             # print('user %s received chat from %s' % (self.l.parent.email, args[0]['user']['email']))
#         pass

    # def update_document(self, new_text):
    #     update = [ self.main_tex,
    #               {"doc": self.main_tex,
    #                "op": [{"d": self.doc_text, "p":0},
    #                       {"i": new_text, "p":0}],
    #                "v": self.doc_version}]
    #     self.c.emit("applyOtUpdate", update)
    #     self.pending_text = new_text

    # def move_and_write(self, text):
    #     doc_split = self.doc_text.split('\n')
    #     nr_lines = len(doc_split)
    #     start_i, end_i= 0, nr_lines-1
    #     for i in range(0, nr_lines):
    #         if '\section{Introduction}' in doc_split[i]:
    #             start_i = i+1
    #         if '\end{document}' in doc_split[i]:
    #             end_i = i-1
    #             break

    #     if random.randint(1, 50) == 25:
    #         text += '\n' #add a new line occasionally

    #     row = random.randint(start_i, end_i)
    #     col = len(doc_split[row])
    #     pos = 0
    #     for j in range(0, row+1):
    #         pos += len(doc_split[j])+1
    #     pos -= 1

    #     # print('user %s moving at [%s:%s]' % (self.l.parent.email, row, col))

    #     global pos_triggered
    #     pos_triggered += 1


    #     dv = self.doc_version
    #     pos_args = {"row":row,"column":col,"doc_id":self.main_tex}
    #     doc_args = {"doc":self.main_tex,"op":[{"p":pos,"i":text}],"v":dv}
    #     self.sent_doc_version = dv
    #     client_ts = current_milli_time()
    #     #     client_rid = str(uuid.uuid4().hex)
    #     pos_args['client_ts'] = client_ts
    #     doc_args['client_ts'] = client_ts
    #     #     args[args_i[0]]['client_rid'] = client_rid

    #     # print('move and write')
    #     self.emit("clientTracking.updatePosition", [pos_args])
    #     self.emit("applyOtUpdate", [self.main_tex, doc_args])
    #     self.pending_text = self.doc_text[:pos]+text+self.doc_text[pos:]

    # def close(self):
    #     self.c.close()

    # def emit(self, name, args, id=None, add_version=False):
    #     try:
    #         self.c.emit(name, args, id, add_version)
    #     except:
    #         print("SHLG: emit exeption")
    #         self.l.interrupt()

class Websocket():
    def __init__(self, page):
        self.c = Client(page)
        # print(page)
        # print(self.c)
        # print("=============")
        # print(self.c)
        self.l = page
        # self.pending_text = None
        self.c.on("clientTracking.clientUpdated", self.on_update_position)
        self.c.on("clientTracking.clientUpdated", self.noop)
        self.c.on("clientTracking.clientDisconnected", self.noop)
        self.c.on("new-chat-message", self.noop)
        self.c.on("new-chat-message", self.on_chat)
        print("done on-chat")
        self.c.on("reciveNewFile", self.noop)
        self.c.on("otUpdateApplied", self.update_version)
        # print("before emit")
        # print([{"project_id": page.project_id}])
        self.emit("joinProject", [{"project_id": page.project_id}], id=1)
        
        with gevent.Timeout(5000, False):
            m = self.c.recv()
            # print(m)
            m = self.c.recv()
            # print(m)
            self.root_folder =  m["args"][1]["rootFolder"][0] if len(m["args"]) > 1 else None
            self.main_tex = m["args"][1]["rootDoc_id"] if len(m["args"]) > 1 else None
            # print("self.main_tex: "+ self.main_tex)
            if self.root_folder:
                page.imgs = [file['_id'] for file in self.root_folder['fileRefs']]
            self.emit("joinDoc", [self.main_tex], id=2)
            old_doc = self.c.recv()
            # print(old_doc)
            # print("=======================")
            self.doc_text = "\n".join(old_doc["args"][1])
            self.doc_version = old_doc["args"][2]
            self.emit("clientTracking.getConnectedUsers", [], id=3)
            self.c.recv()
        assert self.doc_version is not None
    
    pos_triggered = pos_registered = 0
    def on_update_position(self, args):

        rec_ts = current_milli_time()
        if 'client_ts' in args[0] and self.l.parent.email != args[0]['email']:
            self.l.events.request_success.fire(request_type='WebSocket',
                                name="update_cursor_position",
                                response_time=rec_ts - args[0]['client_ts'],
                                response_length=0)
            # print('user %s saw user %s moving at [%s:%s]' % (self.l.parent.email, args[0]['email'], args[0]['row'], args[0]['column']))

            global pos_registered
            pos_registered += 1

        pass

    def on_chat(self, args):

        rec_ts = current_milli_time()
        if 'client_ts' in args[0] and self.l.parent.email != args[0]['user']['email']:
            self.l.events.request_success.fire(request_type='WebSocket',
                                name="receive_chat_message",
                                response_time=rec_ts - int(args[0]['client_ts']),
                                response_length=0)
            # print('user %s received chat from %s' % (self.l.parent.email, args[0]['user']['email']))
        pass
    
    def recv(self): self.c.recv()

    def update_version(self, args):
        self.doc_version = args[0]["v"] + 1
        if self.pending_text is not None:
            self.doc_text = self.pending_text
            self.pending_text = None

    def noop(self, args):
        pass

    def update_document(self, new_text):
        update = [ self.main_tex,
                  {"doc": self.main_tex,
                   "op": [{"d": self.doc_text, "p":0},
                          {"i": new_text, "p":0}],
                   "v": self.doc_version}]
        self.c.emit("applyOtUpdate", update)
        self.pending_text = new_text

    def close(self):
        self.c.close()
        

        
    def emit(self, name, args, id=None, add_version=False):
        # print("in project emit")
        # print(name, args, id)
        try:
            self.c.emit(name, args, id, add_version)
        except:
            print("SHLG: emit exeption")
            self.l.interrupt()

def template(path):
    with open(os.path.join(ROOT_PATH, path), "r") as f:
        return string.Template(f.read())

def chat(l):
    
    # msg = "".join( [random.choice(string.ascii_letters) for i in range(30)] )
    # p = dict(_csrf=l.csrf_token, content=msg)
    res = l.client.get("/project/%s" % l.project_id)
    print(res.content)
    print(l.project_id)
    print("==================")
    # print("++++++here in chat")
    csrf_token = csrf.find_in_page(res.content)
    # print(csrf_token, l.csrf_token)
    msg = "1234"
    # client_ts = current_milli_time()
    p = {
        "_csrf": csrf_token,
        "content": msg
        }
    # print(p)
    # print("=================")
    # print(p)
    # print("/project/%s/messages" % l.project_id)
    # print("=================")
    # print("http://localhost:8080/project/{}/messages?_csrf={}&content=hi".format(l.project_id, l.csrf_token))
    # r = l.client.post("/project/{}/messages?_csrf={}&content=hi".format(l.project_id, l.csrf_token))
    r = l.client.post("http://localhost:8080/project/%s/messages" % l.project_id, data=p, name="/project/[id]/messages")
    # print("Response Headers:")
    # for key, value in r.headers.items():
    #     print(f"{key}: {value}")
    con = r.content
    decoded_data = con.decode('utf-8')
    print(r)
    print("=================")

DOCUMENT_TEMPLATE = template("document.tex")
def edit_document(l):
    params = dict(paragraph=random.randint(0, 1000))
    doc = DOCUMENT_TEMPLATE.safe_substitute(params)
    l.websocket.update_document(doc)

def stop(l):
    l.interrupt()

def get_random_email_except(self_email):
    i = random.randint(10,21)
    return "user{}@netsail.uci.edu".format(i)
    
def share_project(l):
    l.client.get("/user/contacts")
    p = dict(_csrf=l.csrf_token, email=get_random_email_except("admin@example.com"), privileges="readAndWrite")
    res = l.client.post("/project/%s/users" % l.project_id, data=p, name="/project/[id]/users")
    # print(str(res.content))

def spell_check(l):
    data = dict(language="en", _csrf=l.csrf_token, words=randomwords.sample(1, 1), token=l.user_id)
    r = l.client.post("/spelling/check", json=data)

def file_upload(l):
    path = os.path.join(ROOT_PATH, "tech-support.jpg")
    p = dict(folder_id=l.websocket.root_folder['_id'],
             _csrf=l.csrf_token,
             qquuid=str(uuid.uuid1()),
             qqtotalfilesize=os.stat(path).st_size)
    files = { "qqfile": ('tech-support.jpg', open(path, "rb"), 'image/jpeg')}
    resp = l.client.post("/project/%s/upload" % l.project_id, params=p, files=files, name="/project/[id]/upload")

def show_history(l):
    l.client.get("/project/%s/updates?min_count=10" % l.project_id)
    l.client.get("/project/{}/doc/{}/diff?from=1&to=2".format(l.project_id, l.websocket.root_folder['_id']))

    # l.client.get("/project/%s/updates" % l.project_id, params={"min_count": 10}, name="/project/[id]/updates")
    # u =  "/project/%s/doc/%s/diff" % (l.project_id, l.websocket.root_folder['_id'])
    # l.client.get(u, params={'from':1, 'to':2}, name="/project/[id]/doc/[id]/diff")

def compile(l):
    d = {"rootDoc_id": l.websocket.root_folder['_id'] ,"draft": False,"_csrf": l.csrf_token}
    r1 = l.client.post("/project/%s/compile" % l.project_id,
                       json=d,
                       name="/project/[id]/compile")
    resp = r1.json()
    if resp["status"] == "too-recently-compiled":
        return
    files = resp["outputFiles"]
    l.client.get("/project/%s/output/output.log" % l.project_id,
            params={"build": files[0]["build"]},
            name="/project/[id]/output/output.log?build=[id]")
    l.client.get("/project/%s/output/output.pdf" % l.project_id,
            params={"build": files[0]["build"], "compileGroup": "standard", "pdfng": True},
            name="/project/[id]/output/output.pdf")

def find_user_id(doc):
    # window.csrfToken = "DwSsXuVc-uECsSv6dW5ifI4025HacsODuhb8"
    decoded_data = doc.decode('utf-8')    
    user = re.search('window\.user_id\s*=\s*\'(.*?)\';', decoded_data, re.IGNORECASE).group(1)
    assert user, "No user found in response"
    return user

def join_projects(l):
    r = l.client.get("/project", name='get_project_list')
    notifications = re.search("\"notifications\":\\[.*\\]", r.content.decode('utf-8'), re.MULTILINE)
    notifications = json.loads('{'+notifications.group(0)+'}')['notifications'] if notifications is not None else []
    try:
        csrf_token = csrf.find_in_page(r.content)
    except AssertionError:
        print('User %s, project %s reached rate limit' % (l.parent.name, l.project['name']))
        time.sleep(60)
        stop(l)
        return
    d = {"_csrf": csrf_token}
    projects = re.search("{\"projects\":\\[.*\\]}", r.content.decode('utf-8'), re.MULTILINE)
    projects = json.loads(projects.group(0))['projects'] if projects is not None else []
    pids = [p['id'] for p in projects if not p['archived']]

    for n in notifications:
        p_id = n['messageOpts']['projectId']
        if p_id in pids:
            continue
        token = n['messageOpts']['token']
        resp = l.client.post("/project/%s/invite/token/%s/accept" % (p_id,token), params=d, name="join_project")
        if resp.status_code != 200:
            print('user %s shared %s with %s' % ( n['messageOpts']['userName'], n['messageOpts']['projectName'],l.parent.parent.email))

def get_projects(l):
    r = l.client.get("/project", name='get_project_list')
    projects = re.search("{\"projects\":\\[.*\\]}", r.content.decode('utf-8'), re.MULTILINE)
    projects = json.loads(projects.group(0))['projects'] if projects is not None else []
    return [p for p in projects if not p['archived']]


def set_project(l):
    old_pid = l.project_id if hasattr(l, 'project_id') else None
    join_projects(l)
    projects = get_projects(l)
    l.user_id = l.parent.user_id

    predef = [p for p in projects if p['name'] in l.parent.predef_projects]

    if len(predef)>0:
        projects = predef
    else:
        if len(l.parent.predef_projects) and len(l.parent.predef_projects[0]):
            projects = []
            for pname in l.parent.predef_projects:
                #create these projects and share them with everybody
                new_p = create_project(l, pname).json()
                new_p['id'] = new_p['project_id']
                new_p['name'] = pname
                new_p['owner'] = {'_id':l.user_id}
                # share_project_all(l, new_p['id'])
                projects.append(new_p)

    

    if len(projects):
        l.project = random.choice(projects)
        l.project_id = l.project['id']
        # l.project_id = '5a69b3d3ba0c6d042e460407'
    else:
        pname = randomwords.sample(2, 2)
        pname = "%s %s" % (pname[0], pname[1])
        r = create_project(l, pname)
        l.project = r.json()
        l.project_id = l.project["project_id"]

    l.locust.ws_fwd_path = ''
    # if len(redirect_projs)>0 and l.parent.predef_projects[l.project_id] == 'remote':
    if l.parent.koala_enabled:
            l.locust.ws_fwd_path = 'object/%s/' % l.project_id

    print('User %s opened project %s' % (l.parent.name , l.project['name']))

    if l.project_id != old_pid:
        page = l.client.get("/project/%s" % l.project_id, name="open_project")
        try:
            l.csrf_token = csrf.find_in_page(page.content)
        except AssertionError:
            print('User %s, project %s reached rate limit' % (l.parent.name, l.project['name']))
            time.sleep(60)
            stop(l)
            return
        # l.user_id = find_user_id(page.content)

        d = {"shouldBroadcast": False, "_csrf": l.csrf_token}
        # res = l.client.post("/project/%s/references/indexAll" % l.project_id, params=d, name="get_references")
        # res = l.client.get("/project/%s/metadata" % l.project_id, name="get_project_metadata")


        # if not len(projects):
        # share_project(l)
        # if l.project['owner']['_id'] == l.user_id:
        #     share_project_all(l)

        l.websocket = Websocket(l)
        def _receive():
            try:
                while True:
                    l.websocket.recv()
            except (ConcurrentObjectUseError, WebSocketConnectionClosedException):
                if not l.interrupted:
                    print("SHLG: websocket closed. User %s, project %s " % (l.parent.name , l.project['name']))
                    l.websocket.close()
                    l.interrupt()

        gevent.spawn(_receive)


class Page(TaskSet):
    tasks = { stop: 0, chat: 20, edit_document: 0, file_upload: 0, show_history: 0, file_upload: 0, compile: 0, share_project: 0, spell_check: 0}
    def on_start(self):
        pass
        projects = self.parent.projects
        # assert len(projects) > 0
        # rand_id = random.randint(0,len(projects["projects"]))
        print(projects)
        
        self.project_id = projects[0]["id"]
        print(self.project_id)
        print("=====")
        page = self.client.get("/project/%s" % self.project_id, name="/project/[id]")
        # # print(page.content)
        # # print("==============")
        self.csrf_token = csrf.find_in_page(page.content)
        # self.user_id = find_user_id(page.content)
        # # print(self.project_id, self.csrf_token, self.user_id)
        # self.websocket = Websocket(self)
        # # print("here")
        # def _receive():
        #     try:
        #         while True:
        #             # print("inside websocket")
        #             self.websocket.recv()
        #     except:
        #         print("websocket closed")
        # gevent.spawn(_receive)

    def interrupt(self,reschedule=True):
        self.websocket.close()
        super(Page, self).interrupt(reschedule=reschedule)

if __name__ == "__main__":
    ws = Websocket()