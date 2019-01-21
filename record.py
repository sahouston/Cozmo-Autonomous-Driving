import pygame
import cozmo
import numpy as np
import os, sys, time
import autodrive_constants
from PIL import Image

data_dir = 'data_train'
#data_dir = 'data_test'

class Joystick:
    def __init__(self):
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.throttle = 0.0

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


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = True
    # Lift arms and look down to get good view of road ahead
    robot.set_lift_height(1.0, in_parallel=True)
    robot.set_head_angle(autodrive_constants.HEAD_ANGLE, in_parallel=True)
    robot.set_head_light(True)

    joystick = Joystick()

    screen = pygame.display.set_mode((320,240))

    images = list()
    steer = list()
    imgSize = autodrive_constants.IMG_SIZE

    # -------- Main Program Loop -----------
    run = True
    recording = False
    print("Not recording, press joystick button to start. Cozmo's lights will turn red while recording.")
    while run:
        joystickMoved = False
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                joystick.event(event)
                joystickMoved = True
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    recording = not recording
                    if recording:
                        robot.set_all_backpack_lights(cozmo.lights.red_light)
                    else:
                        robot.set_backpack_lights_off()
            elif event.type == pygame.QUIT:
                run = False

        if joystickMoved:
            if abs(joystick.throttle) < 0.1:
                robot.stop_all_motors()
            else:
                if joystick.throttle > 0.0:
                    direction = 1
                else:
                    direction = -1
                #l_wheel_speed = (joystick.throttle * 150.0) + (joystick.x * 75.0)
                #r_wheel_speed = (joystick.throttle * 150.0) - (joystick.x * 75.0)
                l_wheel_speed = (direction * autodrive_constants.RECORD_DRIVE_SPEED) + (joystick.x * 75.0)
                r_wheel_speed = (direction * autodrive_constants.RECORD_DRIVE_SPEED) - (joystick.x * 75.0)
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
            if recording:
                images.append(scaled_img)
                steer.append(joystick.x)

        pygame.time.wait(100) # sleep

    robot.stop_all_motors()
    robot.set_head_light(False)
    pygame.quit()

    if len(images) > 0:
        print('Saving images')
        img_arr = np.zeros((len(images), imgSize[0], imgSize[1], imgSize[2]), dtype=np.float16)
        steer_arr = np.zeros(len(steer), dtype=np.float32)
        for i in range(0, len(images)):
            img_arr[i] = np.array(images[i], dtype=np.float16) / 255.
            steer_arr[i] = steer[i]

        timestr = time.strftime("%Y%m%d-%H%M%S")

        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        np.savez(f'{data_dir}/{timestr}-images.npz', img_arr=img_arr)
        np.savez(f'{data_dir}/{timestr}-steer.npz', steer_arr=steer_arr)

    print('Done')

if __name__ == "__main__":
    pygame.init()
    cozmo.setup_basic_logging()
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
