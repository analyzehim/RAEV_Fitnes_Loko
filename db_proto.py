import pickle
import os


class DB:
    def __init__(self):
        self.file_name = "db.dump"
        self.state = self.load()



    def add_default_id(self, id):
        if id not in self.state:
            self.state[id] = {}
        self.state[id]["notification_state"] = 0
        self.state[id]["schedule_state"] = 0
        self.dump()
        return 0




    def load(self):
        # print len(self.file_name )
        # if os.path.exists(self.file_name):
        #     with open(self.file_name, 'rb') as f:
        #         self.state = pickle.load(f)
        # else:
        #     self.state = {}
        return {}

    def dump(self):
        # f = open(self.file_name, 'wb')
        # pickle.dump(self.state, f)
        # f.close()
        return


    def set_notification_state(self, id, state):
        self.state[id]['notification_state'] = state
        self.dump()
        return state

    def set_schedule_state(self, id, state):
        self.state[id]['schedule_state'] = state
        self.dump()
        return state

    def get_notification_state(self, id):
        if id not in self.state:
            self.add_default_id(id)
        else:
            return self.state[id]['notification_state']

    def get_schedule_state(self, id):
        if id not in self.state:
            self.add_default_id(id)
        else:
            return self.state[id]['schedule_state']

    def add_programs(self, id, program):
        if 'programs' not in self.state[id]:
            self.state[id]['programs'] = set()
        self.state[id]['programs'].add(program)
        self.dump()
        return len(self.state[id]['programs'])

    def delete_programs(self, id, program):
        if 'programs' not in self.state[id]:
            self.state[id]['programs'] = set()
        self.state[id]['programs'].remove(program)
        self.dump()
        return len(self.state[id]['programs'])

    def get_programs(self, id):
        if 'programs' not in self.state[id]:
            self.state[id]['programs'] = set()
        return self.state[id]['programs']