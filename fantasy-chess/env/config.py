class Configuration:
 def __init__(self):
    self.maxY = 25
    self.maxX = 25
    self.windowWidth = 1008
    self.windowHeight = 672
    self.widthFactor = 720 / self.maxX
    self.heightFactor = 480 / self.maxY

config = Configuration()