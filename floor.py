class Floor:
    def __init__(self, conditions, position):
        self.conditions = [*conditions]
        self.explored = False
        self.position = [position[0], position[1]]

    def getStringPosition(self):
        return f"({self.position[0]},{self.position[1]})"

    def getRow(self):
        return self.position[0]
    
    def getCol(self):
        return self.position[1]

