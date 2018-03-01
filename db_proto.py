import pickle
import os


class DB:
    def __init__(self):
        self.file_name = "db_dump"
        if os.path.exists(self.file_name):
            with open(self.file_name, 'rb') as f:
                self.state = pickle.load(f)
        else:
            self.state = {}

    def add_new_id(self, id):
        if id not in self.state:
            self.state[id] = {"notification_state":  0, "schedule_state": 0, "subscribes": set()}
            self.dump()
            return 0
        else:
            return -1

    def dump(self):
        with open(self.file_name, 'wb') as f:
            pickle.dump(self.state, f)

    def set_default_state(self, id):
        if id not in self.state:
            return -1
        else:
            self.state[id] = {"notification_state": 0, "schedule_state": 0, "subscribes": set()}
            self.dump()
            return 0

    def set_notification_state(self, id, state):
        if id not in self.state:
            return -1
        else:
            self.state[id]['notification_state'] = state
            self.dump()
            return state

    def set_schedule_state(self, id, state):
        if id not in self.state:
            return -1
        else:
            self.state[id]['schedule_state'] = state
            self.dump()
            return state

    def get_notification_state(self, id):
        if id not in self.state:
            return -1
        else:
            return self.state[id]['notification_state']

    def get_schedule_state(self, id):
        if id not in self.state:
            return -1
        else:
            return self.state[id]['schedule_state']

    def add_subscribe(self, id, subscribe_name):
        if id not in self.state:
            return -1
        else:
            self.state[id]['subscribes'].add(subscribe_name)
            self.dump()
            return len(self.state[id]['subscribes'])

    def delete_subscribe(self, id, subscribe_name):
        if id not in self.state:
            return -1
        elif subscribe_name not in self.state[id]['subscribes']:
            return -1
        else:
            self.state[id]['subscribes'].remove(subscribe_name)
            self.dump()
            return len(self.state[id]['subscribes'])

    def get_subscribe(self, id):
        if id not in self.state:
            return -1
        else:
            return self.state[id]['subscribes']
