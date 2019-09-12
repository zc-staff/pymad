from .basic import Node

class External(Node):
    def __init__(self, path, env=None, name=None, inputs=None):
        from .parser import parseNodeList
        if env != None:
            path = env.findPath(path)
        self.obj, self.env = parseNodeList(path)
        if name != None:
            self.obj = self.env.nodes[name]
        if inputs != None:
            self.obj.updateInput(inputs)
    
    def getNode(self):
        return self.obj

class Sequential(Node):
    def __init__(self, nodes, inputs=None, **kwargs):
        super(Sequential, self).__init__(**kwargs)
        self.inputNode = None
        for n in nodes:
            n.updateInput(inputs)
            if self.inputNode == None:
                self.inputNode = n
            inputs = n
        self.node = inputs
    
    def updateInput(self, inputs):
        self.inputNode.updateInput(inputs)
    
    def execute(self):
        return self.node.execute()
