import os
import json
from .actor import JsonNode, WavNode, PianoActor, EffectActor
from .combination import External, Sequential, Mixer, MultiTrack

exposes = [ JsonNode, WavNode, PianoActor, External, Sequential, EffectActor, Mixer, MultiTrack ]
exposesMap = { v.__name__: v for v in exposes }

class Environment(object):
    def __init__(self, root):
        self.root = root
        self.nodes = {}
    
    def findPath(self, path):
        return os.path.join(self.root, path)

    def findNode(self, name):
        return self.nodes[name]

    def parseObj(self, obj, ref=False):
        if type(obj) == dict:
            if '__type__' in obj:
                tp = exposesMap[obj['__type__']]
                args = self.parseObj(obj['__args__'], tp.needReference)
                inputs = None
                if '__inputs__' in obj:
                    inputs = self.parseObj(obj['__inputs__'])
                ret = tp(env=self, inputs=inputs, **args).getNode()
                if '__name__' in obj:
                    self.nodes[obj['__name__']] = ret
                if ref:
                    ret = ret.getReference()
                return ret
            else:
                return { k: self.parseObj(v, ref) for k, v in obj.items() }
        elif type(obj) == list:
            return [ self.parseObj(v, ref) for v in obj ]
        else:
            return obj

def parseNodeList(path):
    root = os.path.dirname(path)
    env = Environment(root)
    nodes = None
    with open(path, 'r') as fp:
        nodes = json.load(fp)
    obj = env.parseObj(nodes)
    return obj, env
