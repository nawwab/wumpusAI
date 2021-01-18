from logic import *

knowledge = And()
knowledge.add(Symbol("a"))
knowledge.add(Symbol("a"))
print(knowledge.formula())