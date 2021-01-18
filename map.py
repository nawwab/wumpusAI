import random
import numpy as np
from logic import *
from floor import *
import os
import time

class Map:
    def __init__(self, maxWumpus, maxPit):
        self.col = 15
        self.row = 8
        self.arr = []
        self.agentPosition = []

        for i in range(self.row):
            row = []

            for j in range(self.col):
                if i == 0 and j == 0:
                    floor = Floor(["Agent"], [i, j])
                    self.agentPosition = [i, j]
                    floor.explored = True
                    row.append(floor)
                else:
                    row.append( Floor([], [i, j]) )

            self.arr.append(row)

        self.terrains = [] # wumpus
        self.marks = [] # stench
        self.wumpusIndex = self.addTerrain("wumpus", maxWumpus, "stench")
        self.pitIndex = self.addTerrain("pit", maxWumpus, "breeze")
        self.addGold()
    
    def addGold(self):
        self.arr = self.flatArr()

        while True:
            index = random.randint(2, self.col * self.row)

            if not index in self.wumpusIndex:
                self.arr[index].conditions.append("gold")
                print("gold exist")
                break
            else:
                continue
        
        self.arr = np.reshape(self.arr, (-1, self.col))

    def addTerrain(self, terrain, terrainMax, mark=None):
        self.terrains.append(terrain)
        self.marks.append(mark)
        terrainIndex = []

        self.arr = self.flatArr()
        
        for i in range(terrainMax):
            index = random.randint(2, self.col * self.row)

            for otherTerrain in self.terrains:
                if 0 <= index < self.col * self.row:
                    if not otherTerrain in self.arr[index].conditions:
                        terrainIndex.append(index)

        for i in range(self.col * self.row):
            conditions = []
            agentOnIt = False

            if i in terrainIndex:
                self.arr[i].conditions.append(terrain)

        self.arr = np.reshape(self.arr, (-1, self.col))

        if mark:
            for i in range(self.row):
                for j in range(self.col):

                    if terrain in self.arr[i][j].conditions:

                        if 0 <= (j + 1) < self.col: 
                            self.arr[i][j + 1].conditions.append(mark)

                        if 0 <= (j - 1) < self.col:
                            self.arr[i][j - 1].conditions.append(mark)

                        if 0 <= (i + 1) < self.row:
                            self.arr[i + 1][j].conditions.append(mark)

                        if 0 <= (i - 1) < self.row:
                            self.arr[i - 1][j].conditions.append(mark)
        
        return terrainIndex
            
    def flatArr(self):
        newArr = []

        for row in self.arr:
            for floor in row:
                newArr.append(floor)
        
        return newArr
            
    def printMap(self, showAll=False):
        printedArr = self.arr

        for i in range(self.row):
            print("|", end="")

            for floor in printedArr[i]:
                conditionsStr = ""

                if "Agent" in floor.conditions:
                    conditionsStr += "A"

                if "OK" in floor.conditions:
                    conditionsStr += "*"

                if "gold" in floor.conditions:
                    conditionsStr += "g"
                
                for legend in [*self.terrains, *self.marks]:
                    if legend in floor.conditions:
                        conditionsStr += legend[0]
                
                if showAll:
                    print(conditionsStr.ljust(6), end="")
                else:
                    if floor.explored:
                        print(conditionsStr.ljust(6), end="")
                    else:
                        print("██████", end="")

                print("|", end="")

            print()
            print("+", end="")

            for i in range(self.col):
                print("------+", end="")

            print()

    def solve(self):
        floorOnCheck = []
        knowledge = And()
        wumpusFloor = []
        pitFloor = []
        legends = [*self.terrains, *self.marks]   

        while True:
            os.system('clear')
            self.printMap(True)
            time.sleep(0.5)
            print()
            okFlag = True
            currentFloor = self.arr[self.agentPosition[0]][self.agentPosition[1]]

            if "Agent" in currentFloor.conditions and "wumpus" in currentFloor.conditions:
                print("wumpus eat you, you die")
                break
            
            if "Agent" in currentFloor.conditions and "pit" in currentFloor.conditions:
                print("you fall to pit, you die")
                break

            if "Agent" in currentFloor.conditions and "gold" in currentFloor.conditions:
                print("gold discovered, you win!")
                break
        
            row = currentFloor.getRow()
            col = currentFloor.getCol()

            # gathering knowledge
            if currentFloor.explored:
                knowledge.add(Symbol(f"visited{currentFloor.getStringPosition()}"))
            
            for legend in legends:
                if legend in currentFloor.conditions: 
                    okFlag = False
                    knowledge.add(Symbol(f"{legend}{currentFloor.getStringPosition()}"))
                else:
                    knowledge.add(Not(Symbol(f"{legend}{currentFloor.getStringPosition()}")))
            
            # gathering knowledge and upadate the map conditions
            if okFlag:
                knowledge.add(Symbol(f"OK{currentFloor.getStringPosition()}"))
                self.arr[row][col].conditions.append("OK")

                if 0 <= col + 1 < self.col:
                    knowledge.add(Symbol(f"OK({row},{col + 1})"))
                    self.arr[row][col + 1].conditions.append("OK")
                    if not [row, col + 1] in floorOnCheck and not self.arr[row][col + 1].explored:
                        floorOnCheck.append([row, col + 1])

                if 0 <= col - 1 < self.col:
                    knowledge.add(Symbol(f"OK({row},{col - 1})"))
                    self.arr[row][col - 1].conditions.append("OK")
                    if not [row, col - 1] in floorOnCheck and not self.arr[row][col - 1].explored:
                        floorOnCheck.append([row, col - 1])

                if 0 <= row + 1 < self.row:
                    knowledge.add(Symbol(f"OK({row + 1},{col})"))
                    self.arr[row + 1][col].conditions.append("OK")
                    if not [row + 1, col] in floorOnCheck and not self.arr[row + 1][col].explored:
                        floorOnCheck.append([row + 1, col])

                if 0 <= row - 1 < self.row:
                    knowledge.add(Symbol(f"OK({row - 1},{col})"))
                    self.arr[row - 1][col].conditions.append("OK")
                    if not [row - 1, col] in floorOnCheck and not self.arr[row-1][col].explored:
                        floorOnCheck.append([row - 1, col])
                
                self.agentMovingForward(floorOnCheck.pop())
            else:
                def agentsActionTowardTerrain(terrain, mark, terrainArr): 
                    terrainIsNear = []
                    if 0 <= col + 1 < self.col:
                        terrainIsNear.append([[row, col + 1] ,Symbol(f"{terrain}({row},{col + 1})")])

                    if 0 <= col - 1 < self.col:
                        terrainIsNear.append([[row, col - 1] ,Symbol(f"{terrain}({row},{col - 1})")])

                    if 0 <= row + 1 < self.row:
                        terrainIsNear.append([[row + 1, col] ,Symbol(f"{terrain}({row + 1},{col})")])

                    if 0 <= row - 1 < self.row:
                        terrainIsNear.append([[row - 1, col] ,Symbol(f"{terrain}({row - 1},{col})")])

                    allTerrainSymbol = [terrainStatus[1] for terrainStatus in terrainIsNear]
                    
                    knowledge.add(Implication(
                        Symbol(f"{mark}{currentFloor.getStringPosition()}"),
                        Or(*allTerrainSymbol)
                    ))

                    if (len(floorOnCheck) == 0):
                        for terrainStatus in terrainIsNear:
                            terrainRow = terrainStatus[0][0]
                            terrainCol = terrainStatus[0][1]

                            if model_check(knowledge, terrainStatus[1]): #checking if terrain nearby
                                terrainArr.append(terrainStatus[0])
                                knowledge.add(Symbol(f"{terrain}({terrainRow},{terrainCol})"))
                            else:
                                floorOnCheck.append(terrainStatus[0])

                        self.agentMovingForward(floorOnCheck.pop())
                    else:
                        self.agentMovingForward(floorOnCheck.pop())

                if "stench" in currentFloor.conditions and "stench" in self.marks:
                    agentsActionTowardTerrain("wumpus", "stench", wumpusFloor)

                if "breeze" in currentFloor.conditions and "breeze" in self.marks:
                    agentsActionTowardTerrain("pit", "breeze", wumpusFloor)

    def agentMovingForward(self, newPosition):
        row = newPosition[0]
        col = newPosition[1]
        agentRow = self.agentPosition[0]
        agentCol = self.agentPosition[1]
        self.arr[agentRow][agentCol].conditions.remove("Agent")
        self.arr[row][col].conditions.append("Agent")
        self.arr[row][col].explored = True
        self.agentPosition = [row, col]