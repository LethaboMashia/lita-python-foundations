print("Lita Day 1 - Lethabo Mashia" )
print("How Python actually works")

import dis

def greet():
    message = "Hello"
    return message 

dis.dis(greet)