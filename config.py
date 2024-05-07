class Configuration:
 def __init__(self):
    self.maxY = 25
    self.maxX = 25
    self.windowWidth = 720
    self.windowHeight = 480
    self.widthFactor = self.windowWidth / self.maxX
    self.heightFactor = self.windowHeight / self.maxY

config = Configuration()