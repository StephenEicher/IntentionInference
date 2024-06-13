import numpy as np
from  opensimplex import OpenSimplex
import random
import eventClasses as e
from scipy.ndimage import gaussian_filter, zoom
from scipy.spatial import KDTree
import SpriteClasses as sc
import GameObjects as go
import copy
from immutables import map

class Noise:
    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX

    def genNoise(self, scales, amplis, minZ, maxZ):
        simplex = OpenSimplex(random.randint(0,10000000))
        noiseMap = np.zeros((self.maxY, self.maxX))

        # Generate noise for the left triangular half of the grid (grid split across main diagonal)
        s = scales
        a = amplis
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y - x > 0:
                    noise = simplex.noise2(x * s, y * s) * a
                    noiseMap[y, x] += noise

        # Calculate minimum noise value in the noiseMap
        minNoise = noiseMap.min()
        # Shift the entire noiseMap up by adding the absolute of the minimum value to exclude negative values
        noiseMap += abs(minNoise)

        # Mirror the lower half of the left triangular half across the center of grid
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y > x and y + x >= self.maxY - 1:  # Points within lower half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
        
        # Mirror the upper half of the left triangular half across center of grid
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y > x and y + x <= self.maxY - 1: # Points within upper half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
 
        self.smoothen(noiseMap)
                    
        # Normalize the mirrored map
        noiseMapNormalized = (noiseMap - noiseMap.min()) #Make smallest value 0
        noiseMapNormalized = noiseMapNormalized/ noiseMapNormalized.max() #Scale all values from 0 to 1
        # print(f"minZ = {noiseMap.min()} maxZ = {noiseMap.max()}")
        scaledNoiseMapFloat = noiseMapNormalized * (maxZ - minZ)
        scaledNoiseMapInt = np.round(scaledNoiseMapFloat).astype(int)
        # borderWidth = 3

        # for y in range(self.maxY):
        #     for x in range(self.maxX):
        #         # Calculate the distance from the diagonal and antidiagonal lines
        #         distFromDiag = abs(y - x)
        #         distFromAntidiag = abs((y + x) - (self.maxY - 1))
                
        #         # Check if the point is within the border width of the diagonal or antidiagonal lines
        #         if (
        #             distFromDiag <= borderWidth or
        #             distFromAntidiag <= borderWidth
        #         ):
        #             # Set the value to zero to create a border zone
        #             scaledNoiseMapInt[y, x] = 0

        return [scaledNoiseMapInt, noiseMapNormalized]

    def smoothen(self, map):
        # GENERALIZE FUNCTION SO AS TO MASK -> THRESHOLD -> SMOOTHEN
        # Create a mask that includes the seam and adjacent tiles up to a certain distance (seam_width)
        mask = np.zeros_like(map, dtype=bool)
        length = len(map)
        
        sigma = 1
        seamWidth = 1

        # Define the area around the seam
        for i in range(length):
            # Apply the mask along the main diagonal and its adjacent tiles up to seam_width
            for j in range(max(0, i - seamWidth), min(length, i + seamWidth + 1)):
                mask[i, j] = True
                mask[j, i] = True  # Add adjacent tiles along the diagonal
        
        # Apply Gaussian blur to the entire map
        blurredMap = gaussian_filter(map, sigma=sigma)
        
        # Blend the blurred map back into the original map using the mask
        map[mask] = blurredMap[mask]
        
        return map

class ZMap(Noise):
    def __init__(self, maxY, maxX, board):
        super().__init__(maxY, maxX)
        self.board = board
        comboMap = self.genNoise(0.1, 1, 0, 0)
        self.map = comboMap[0]

    def ZMhandleEvent(self, event):
        if isinstance(event, e.eMove):

            adjZs = {}
            for direction, (adjY, adjX) in self.board.getAdjDirections(event.unit).items():
                adjZ = self.map[adjY, adjX]
                unitZ = self.map[event.unit.position[0], event.unit.position[1]]

                adjZs[(event.unit.position[0], event.unit.position[1])] = unitZ
                adjZs[(direction, (adjY, adjX))] = adjZ

            return adjZs
        
    def applyMasks(self, map, mask):
        yScale = self.maxY/10
        xScale = self.maxX/10
        
        masks = {
        "twirl" :  [[1,0,0,0,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0,0,0,0],
                    [0,1,0,0,0,0,0,0,0,0],
                    [0,0,1,0,1,1,0,0,0,0],
                    [0,0,0,1,0,0,1,0,0,0],
                    [0,0,0,1,0,0,1,0,0,0],
                    [0,0,0,0,1,1,0,1,0,0],
                    [0,0,0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,0,0,0,1],
                    [0,0,0,0,0,0,0,0,0,1]],
        "ravine" : [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]],
        "woods" :  [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]],
        "delta" :  [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]]
        }

        selectedMask = masks.get("twirl")
        scaledMask = zoom(selectedMask, (yScale, xScale), order = 0)

    
    def applyThresholds(self, type):
        thresholds = {
            "erode" : [],
            "makepeaks" : [],
            "flatten" : [],
            "fracture" : []                
        }

    def assignListeners(self, dispatcher):
        dispatcher.addListener(e.eMove, self.ZMhandleEvent)

class OMap(Noise):
    def __init__(self, maxY, maxX, board):
        super().__init__(maxY, maxX)
        self.board = board
        
        comboMap = self.genNoise(0.5, 0.1, 0, 2)
        self.map = comboMap[0]
        self.map[self.map < 2] = 0
        self.map[self.map == 2] = 1 # Convert to bool
        self.createObstacles(self.map)
        

    def createObstacles(self, map): # Should this function exist on the class or should the board pass the instance to the GameObjectTree?
        coordArrays = np.where(map)
        rows, cols = coordArrays
        obstacleCoords = list(zip(rows, cols))
        temp = sc.Sprites()
        for i in range(len(obstacleCoords)):
            row, col = obstacleCoords[i]
            newObstacle = go.Obstacles(None, (row, col), 1, temp.spritesDictScaled["obstacle"])
            self.board.bPygame.obstacleGroup.add(newObstacle.sprite)
            # self.obstacleMap[i] = newObstacle
            # self.GOT.insert(newObstacle)
        # self.tree = KDTree(obstalceCoordsNP)    
        

    def clone(self):
        cloned_OM = OMap.__new__(OMap)
        cloned_OM.map = copy.deepcopy(self.map)
        return cloned_OM