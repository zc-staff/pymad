from .basic import Node
from .. import piano

class Actor(Node):
    def __init__(self, inner, **kwargs):
        super(Actor, self).__init__(**kwargs)
        self.inner = inner
    
    def getReference(self):
        return self.inner

class PianoActor(Actor):
    def __init__(self, instr, args, **kwargs):
        inner = getattr(piano, instr)
        inner = inner(**args)
        super(PianoActor, self).__init__(inner, **kwargs)
    