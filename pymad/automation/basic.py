class Node(object):
    def __init__(self, inputs, **kwargs):
        self.type = self.__class__.__name__
        self.inputs = inputs
        self.param = None
    
    def doGetInput(self, obj):
        if isinstance(obj, Node):
            return obj.execute()
        elif type(obj) == dict:
            return { k: self.doGetInput(v) for k, v in obj.items() }
        elif type(obj) == list:
            return [ self.doGetInput(v) for v in obj ]
        else:
            return obj
    
    def getInput(self):
        self.param = self.doGetInput(self.inputs)
    
    def getReference(self):
        return self
    
    def getNode(self):
        return self
    
    def doExecute(self):
        raise NotImplementedError()

    def execute(self):
        self.getInput()
        return self.doExecute()

class CacheNode(Node):
    def __init__(self, **kwargs):
        super(CacheNode, self).__init__(**kwargs)
        self.result = None
    
    def reset(self):
        self.result = None
    
    def execute(self):
        if self.result == None:
            self.getInput()
            self.result = self.doExecute()
        return self.result
