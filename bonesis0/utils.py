
import os

__aspdir__ = os.path.join(os.path.dirname(__file__), "..", "bonesis-asp")

def aspf(name):
    return os.path.join(__aspdir__, name)
