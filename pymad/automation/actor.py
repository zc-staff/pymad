import json
from .basic import Node
from .. import piano, effect, readWav, synthesize

class Actor(Node):
    needReference = True

    def __init__(self, inner, **kwargs):
        super(Actor, self).__init__(**kwargs)
        self.inner = inner
    
    def getReference(self):
        return self.inner

class StaticNode(Actor):
    def __init__(self, inner, **kwargs):
        super(StaticNode, self).__init__(inner, inputs={}, **kwargs)
    
    def execute(self):
        return self.inner

class JsonNode(StaticNode):
    def __init__(self, path, env=None, **kwargs):
        inner = None
        if env != None:
            path = env.findPath(path) 
        with open(path, 'r') as fp:
            inner = json.load(fp)
        super(JsonNode, self).__init__(inner)

class WavNode(StaticNode):
    def __init__(self, path, env=None, **kwargs):
        if env != None:
            path = env.findPath(path)
        super(WavNode, self).__init__(readWav(path))

class PianoActor(Actor):
    def __init__(self, instr, args, lenRatio=1, speedRatio=1, volRatio=1, **kwargs):
        inner = getattr(piano, instr)
        inner = inner(**args)
        super(PianoActor, self).__init__(inner, **kwargs)
        self.lenRatio, self.speedRatio, self.volRatio = lenRatio, speedRatio, volRatio
    
    def doExecute(self):
        self.inner.load(**self.param)
        return synthesize(self.inner, self.param['track'], self.lenRatio, self.speedRatio, self.volRatio)

class EffectActor(Actor):
    def __init__(self, instr, args, **kwargs):
        inner = getattr(effect, instr)
        inner = inner(**args)
        super(EffectActor, self).__init__(inner, **kwargs)
    
    def doExecute(self):
        return self.inner.process(self.param)
