from PIL import Image
import glob
crop_box = (0, 0, 220, 220)
frames = [Image.open(image).crop(crop_box) for image in sorted(glob.glob("./reinforcement_learning/Videos/Frames/*.png"))]
frames[0].save('./reinforcement_learning/Videos/FC.gif', save_all=True, append_images=frames[1:], duration=3, loop=0)

