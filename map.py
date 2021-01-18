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

        self.terrains = [] # wumpus, pit
        self.marks = [] # breeze, stench
        self.addTerrain("wumpus", maxWumpus, "stench")
        # self.addTerrain("pit", maxPit, "breeze")

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

        while not self.mapSolved():
            os.system('clear')
            self.printMap()
            time.sleep(0.5)
            print()
            okFlag = True
            currentFloor = self.arr[self.agentPosition[0]][self.agentPosition[1]]
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
                if "stench" in currentFloor.conditions:
                    wumpusIsNear = []
                    if 0 <= col + 1 < self.col:
                        wumpusIsNear.append([[row, col + 1] ,Symbol(f"wumpus({row},{col + 1})")])

                    if 0 <= col - 1 < self.col:
                        wumpusIsNear.append([[row, col - 1] ,Symbol(f"wumpus({row},{col - 1})")])

                    if 0 <= row + 1 < self.row:
                        wumpusIsNear.append([[row + 1, col] ,Symbol(f"wumpus({row + 1},{col})")])

                    if 0 <= row - 1 < self.row:
                        wumpusIsNear.append([[row - 1, col] ,Symbol(f"wumpus({row - 1},{col})")])

                    allWumpusSymbol = [wumpusStatus[1] for wumpusStatus in wumpusIsNear]
                    
                    knowledge.add(Implication(
                        Symbol(f"stench{currentFloor.getStringPosition()}"),
                        Or(*allWumpusSymbol)
                    ))

                    if (len(floorOnCheck) == 0):
                        for wumpusStatus in wumpusIsNear:
                            if model_check(knowledge, wumpusStatus[1]): #checking if wumpus nearby
                                wumpusFloor.append(wumpusStatus[0])
                            else:
                                floorOnCheck.append(wumpusStatus[0])
                        self.agentMovingForward(floorOnCheck.pop())
                    else:
                        self.agentMovingForward(floorOnCheck.pop())

         
    def mapSolved(self):
        arrOnCheck = self.flatArr()

        for floor in arrOnCheck:
            for terrain in self.terrains: #checking if terrain exist
                if "Agent" in floor.conditions and terrain in floor.conditions:
                    print(f"Agent Die because of {terrain}")
                    return True

                if terrain in floor.conditions and "OK" in floor.conditions:
                    print("unexpected behaviour: " + terrain + " marked OK")
                    return True
                elif terrain in floor.conditions: 
                    continue
            
            return False

    def agentMovingForward(self, newPosition):
        row = newPosition[0]
        col = newPosition[1]
        agentRow = self.agentPosition[0]
        agentCol = self.agentPosition[1]
        self.arr[agentRow][agentCol].conditions.remove("Agent")
        self.arr[row][col].conditions.append("Agent")
        self.arr[row][col].explored = True
        self.agentPosition = [row, col]