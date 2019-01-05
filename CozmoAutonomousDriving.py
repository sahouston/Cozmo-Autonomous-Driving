import pygame
import cozmo

class Joystick:
    def __init__(self):
        pygame.joystick.init()
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.throttle = 0.0

    def poll(self):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        # EVENT PROCESSING STEP
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    self.x = event.value
                elif event.axis == 1:
                    self.y = event.value
                elif event.axis == 2:
                    self.throttle = -event.value
                elif event.axis == 3:
                    self.z = event.value
                return True
        return False


def main():
    pygame.init()
    done = False

    joystick = Joystick()

    # -------- Main Program Loop -----------
    while done==False:

        if joystick.poll():
            print("Throttle: {:>6.3f}".format(joystick.throttle))
        pygame.time.wait(10)
        
    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit ()

if __name__ == "__main__":
    main()