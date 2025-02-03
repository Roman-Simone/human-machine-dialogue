class History():

    def __init__(self):
        self.msgs = []
        self.limit = 5

    def clear(self):
        self.msgs = []

    def add(self, role, content):

        if len(self.msgs) >= self.limit:
            self.msgs.pop(0)
        
        self.msgs.append({
            'role': role,
            'content': content
        })
    
    def get_history(self):
        # return self.msgs

        content_ret = ""

        for msg in self.msgs:
            content_ret += msg['content'] + " "

        return content_ret

