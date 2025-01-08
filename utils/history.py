class History():

    def __init__(self):
        self.msgs = []

    def clear(self):
        self.msgs = []

    def add(self, role, content):
        self.msgs.append({
            'role': role,
            'content': content
        })
    
    def get_history(self):
        return self.msgs
    
    