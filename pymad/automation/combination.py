import numpy as np
from ..core import sequence
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

class Mixer(Node):
    def __init__(self, volRatio=None, **kwargs):
        super(Mixer, self).__init__(**kwargs)
        self.volRatio = volRatio
    
    def doExecute(self):
        n = 0
        ch = 1
        fs = 0
        for inp in self.param:
            n = max(n, inp.shape[0])
            if inp.ndim > 1:
                ch = max(ch, inp.shape[1])
            fs = inp.fs
        
        ret = None
        if ch > 1:
            ret = np.zeros((n, ch), dtype=np.float32)
        else:
            ret = np.zeros(n, dtype=np.float32)

        for i, inp in enumerate(self.param):
            volRatio = 0 if self.volRatio == None or len(self.volRatio) <= i else self.volRatio[i]
            volRatio = 10 ** (volRatio / 20)

            if ch > 1 and inp.ndim < 2:
                inp = inp[:, np.newaxis]
            ret[:inp.shape[0]] += volRatio * inp
        return sequence(ret, fs)

class MultiTrack(Node):
    def __init__(self, piano, drum, **kwargs):
        super(MultiTrack, self).__init__(**kwargs)
        self.piano, self.drum = piano, drum
    
    def doExecute(self):
        self.piano.param = {}
        def executePiano(track):
            self.piano.param['track'] = track
            return self.piano.doExecute()
        inps = { k: executePiano(v) for k, v in self.param['beats'].items() }
        self.drum.param = { 'beats': inps, 'track': self.param['track'] }
        return self.drum.doExecute()
