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

        # content_ret = ""

        # for msg in self.msgs:
        #     content_ret += f"{msg['role']}: {msg['content']}\n"

        # return content_ret

        return self.msgs
    
    def get_history_str(self):
        content_ret = ""

        for msg in self.msgs:
            content_ret += f"{msg['role']}: {msg['content']}\n"

        return content_ret
    
    def clean(self, text_to_mantain: str):
        self.msgs = []
        self.add('user', text_to_mantain)

