class Node(object):
    def __init__(self, inputs, **kwargs):
        self.type = self.__class__.__name__
        self.inputs = inputs
    
    def getInput(self):
        self.param = { k: v.execute() for k, v in self.inputs }
    
    def getReference(self):
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

class StaticNode(Node):
    def __init__(self, inner, **kwargs):
        super(StaticNode, self).__init__(inputs={})
        self.inner = inner
    
    def execute(self):
        return self.inner

class JsonNode(object):
    def __init__(self, path):
        pass
