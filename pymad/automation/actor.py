import json
from .basic import Node
from .. import piano, readWav

class Actor(Node):
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
    def __init__(self, path, env, **kwargs):
        inner = None
        with open(env.findPath(path), 'r') as fp:
            inner = json.load(fp)
        super(JsonNode, self).__init__(inner)

class WavNode(StaticNode):
    def __init__(self, path, env, **kwargs):
        super(WavNode, self).__init__(readWav(env.findPath(path)))

class PianoActor(Actor):
    def __init__(self, instr, args, **kwargs):
        inner = getattr(piano, instr)
        inner = inner(**args)
        super(PianoActor, self).__init__(inner, **kwargs)
    