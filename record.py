import pygame
import cozmo
import time
import numpy as np
import sys
from PIL import Image

imgSize = (66, 200, 3) # h, w, channels

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
    robot.camera.color_image_enabled = True
    # Lift arms and look down to get good view of road ahead
    robot.set_lift_height(1.0, in_parallel=True)
    robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE, in_parallel=True)

    joystick = Joystick()

    screen = pygame.display.set_mode((640,480))

    images = list()
    steer = list()

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

        if joystickMoved:
            if joystick.button != 0:
                # Button pressed, stop moving and exit
                robot.stop_all_motors()
                break

            if abs(joystick.throttle) < 0.1:
                robot.stop_all_motors()
            else:
                if joystick.throttle > 0.0:
                    direction = 1
                else:
                    direction = -1
                #l_wheel_speed = (joystick.throttle * 150.0) + (joystick.x * 75.0)
                #r_wheel_speed = (joystick.throttle * 150.0) - (joystick.x * 75.0)
                l_wheel_speed = (direction * 75.0) + (joystick.x * 75.0)
                r_wheel_speed = (direction * 75.0) - (joystick.x * 75.0)
                robot.drive_wheel_motors(l_wheel_speed, r_wheel_speed, l_wheel_acc=500, r_wheel_acc=500)

        latest_image = robot.world.latest_image
        if latest_image is not None:            
            raw = latest_image.raw_image
            # Convert to pygame image and display in window
            py_image = pygame.image.fromstring(raw.tobytes(), raw.size, raw.mode)
            screen.blit(py_image, (0,0))
            pygame.display.flip() # update the display
            # Scale image
            scaled_img = raw.resize((imgSize[1], imgSize[0]), Image.BICUBIC)
            images.append(scaled_img)
            steer.append(joystick.x)

        pygame.time.wait(100) # sleep
        
    pygame.quit()

    img_arr = np.zeros((len(images), imgSize[0], imgSize[1], imgSize[2]), dtype=np.float16)
    steer_arr = np.zeros(len(steer), dtype=np.float32)
    for i in range(0, len(images)):
        img_arr[i] = np.array(images[i], dtype=np.float16) / 255.
        steer_arr[i] = steer[i]

    timestr = time.strftime("%Y%m%d-%H%M%S")
    np.savez(f'data/{timestr}-images.npz', img_arr=img_arr)
    np.savez(f'data/{timestr}-steer.npz', steer_arr=steer_arr)

if __name__ == "__main__":
    pygame.init()
    cozmo.setup_basic_logging()
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
