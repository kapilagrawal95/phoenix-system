from . import ROOT_PATH
import os
import random

with open(os.path.join(ROOT_PATH, "words"), "r") as f:
    WORDS = map(lambda s: s.strip(), f.readlines())

def sample(minimum, maximum):
    if maximum == minimum:
        maximum = minimum+1
    return random.sample(list(WORDS), random.randint(minimum, maximum))
