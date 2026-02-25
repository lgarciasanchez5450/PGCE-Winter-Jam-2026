from System import BaseSystem
import Serialize


class Serializer(BaseSystem):

    def writer(self):
        return Serialize.Writer()

    def reader(self):
        return Serialize.Reader()

    def update(self):
        pass

    def draw(self): pass