class Backgrounder():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.nextid = 1
            self.processes = {}
    
    def register_job(self, pid) -> int:
        self.processes[self.nextid] = pid
        self.nextid += 1
        return self.nextid - 1
