from time import time
from finder_app.find_timetable import Query


class Session:
    def __init__(self, sid, uid):
        self.start_time = time()
        self.session_id = sid
        self.user_id = uid
        self.query = Query()
        self.response_stack = []  # stack with keys from phrases_dict
