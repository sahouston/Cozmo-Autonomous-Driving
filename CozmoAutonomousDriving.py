import pygame
import cozmo
import numpy as np
from PIL import Image

class Joystick:
    def __init__(self):
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.throttle = 0.0
        self.button = 0

    def event(self, event):
        # You may need to change the axis mapping.
        # Currently axis 0 turns cozmo left/right (x)
        # axis 2 (inverted) controls fwd/reverse speed (throttle)
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                self.x = event.value
            elif event.axis == 1:
                self.y = event.value
            elif event.axis == 2:
                self.throttle = -event.value
            elif event.axis == 3:
                self.z = event.value
        elif event.type == pygame.JOYBUTTONDOWN:
            self.button = 1 # event.button


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    joystick = Joystick()
    
    screen = pygame.display.set_mode((640,480))

    # -------- Main Program Loop -----------
    run = True
    while run:
        joystickMoved = False
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN:
                joystick.event(event)
                joystickMoved = True
            elif event.type == pygame.QUIT:
                run = False

        latest_image = robot.world.latest_image
        if latest_image is not None:            
            raw = latest_image.raw_image
            py_image = pygame.image.fromstring(raw.tobytes(), raw.size, raw.mode)
            screen.blit(py_image, (0,0))
            pygame.display.flip() # update the display

        if joystickMoved:
            if joystick.button != 0:
                # Button pressed, stop moving and exit
                robot.stop_all_motors()
                break

            if abs(joystick.throttle) < 0.05:
                robot.stop_all_motors()
            else:
                l_wheel_speed = (joystick.throttle * 150.0) + (joystick.x * 75.0)
                r_wheel_speed = (joystick.throttle * 150.0) - (joystick.x * 75.0)
                robot.drive_wheel_motors(l_wheel_speed, r_wheel_speed, l_wheel_acc=500, r_wheel_acc=500)

        pygame.time.wait(100) # sleep
        
    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    cozmo.setup_basic_logging()
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
