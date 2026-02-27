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
