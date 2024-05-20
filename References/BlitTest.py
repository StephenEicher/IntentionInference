import pygame
import thorpy as tp

pygame.init()
screen = pygame.display.set_mode((1200, 700))
tp.init(screen, tp.theme_human)  # bind screen to gui elements and set theme

# Create the button
my_button = tp.Button("Hello, world.\nThis button uses the default theme.")
my_button.center_on(screen)
gui_updater = my_button.get_updater()
# Create a box to contain the button (you can use other containers as needed)



def before_gui():
    screen.fill((250,) * 3)

tp.call_before_gui(before_gui)  # tells Thorpy to call before_gui() before drawing gui.

# Define the function to be called when the button is clicked
def test_func():
    print('this is cool!')

# Assign the function to the button's click event
my_button.at_unclick = test_func

clock = pygame.time.Clock()
playing = True
while playing:
    clock.tick(60)
    events = pygame.event.get()
    mouse_rel = pygame.mouse.get_rel()
    for event in events:
        if event.type == pygame.QUIT:
            playing = False
    # Draw the ThorPy elements
    my_button.draw()
    gui_updater.update(events=events, mouse_rel=mouse_rel)
    pygame.display.flip()

pygame.quit()