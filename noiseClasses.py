import numpy as np
from  opensimplex import OpenSimplex
import random
from scipy.ndimage import gaussian_filter, zoom
import spriteClasses as sc
import gameObjectClasses as go

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
            self.board.game.pygameUI.obstacleGroup.add(newObstacle.sprite)
