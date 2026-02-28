from Engine.Serialize import Writer, Reader, addSerializable
import pygame


def serializeVector2(writer:Writer,vec2:pygame.Vector2):
    writer.writeFloat(vec2.x)
    writer.writeFloat(vec2.y)
    
def deserializeVector2(reader:Reader):
    x = reader.readFloat()
    y = reader.readFloat()
    return pygame.Vector2(x,y)

addSerializable(pygame.Vector2,serializeVector2,deserializeVector2)

def serializeRect(writer:Writer,rect:pygame.Rect):
    writer.writeInt(rect.top)
    writer.writeInt(rect.left)
    writer.writeInt(rect.width)
    writer.writeInt(rect.height)
    
def deserializeRect(reader:Reader):
    top = reader.readInt()
    left = reader.readInt()
    width = reader.readInt()
    height = reader.readInt()
    return pygame.Rect(top,left,width,height)

addSerializable(pygame.Rect,serializeRect,deserializeRect)
    