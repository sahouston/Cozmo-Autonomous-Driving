import os

os.environ['KERAS_BACKEND'] = 'theano'
os.environ['THEANO_FLAGS']='mode=FAST_RUN,device=cuda0,floatX=float32,optimizer=None'

import keras.models as models
from keras.models import Sequential

import numpy as np
import pygame
import cozmo
import autodrive_constants
from PIL import Image

def run(sdk_conn):
    imgSize = autodrive_constants.IMG_SIZE

    # load the model:
    model = Sequential()
    with open('autopilot_basic_model.json') as model_file:
        model = models.model_from_json(model_file.read())

    # load weights
    model.load_weights("weights/model_basic_weight.hdf5")

    # Prime Keras by making a first prediction
    steer = model.predict(np.zeros((1,imgSize[0],imgSize[1],imgSize[2]), dtype=np.float16))

    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = True
    # Lift arms and look down to get good view of road ahead
    robot.set_lift_height(1.0, in_parallel=True)
    robot.set_head_angle(autodrive_constants.HEAD_ANGLE, in_parallel=True)
    robot.set_head_light(True)

    screen = pygame.display.set_mode((320,240))

    # -------- Main Program Loop -----------
    run = True
    while run:
        steer = 0.0
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.QUIT:
                robot.stop_all_motors()
                run = False

        latest_image = robot.world.latest_image
        if latest_image is not None:            
            raw = latest_image.raw_image
            # Convert to pygame image and display in window
            py_image = pygame.image.fromstring(raw.tobytes(), raw.size, raw.mode)
            screen.blit(py_image, (0,0))
            pygame.display.flip() # update the display
            # Scale image
            scaled_img = raw.resize((imgSize[1], imgSize[0]), Image.BICUBIC)
            steer = model.predict(np.array(scaled_img, dtype=np.float16, ndmin=4)/255.)

        l_wheel_speed = autodrive_constants.AUTO_DRIVE_SPEED + (steer * 75.0) 
        r_wheel_speed = autodrive_constants.AUTO_DRIVE_SPEED - (steer * 75.0)
        robot.drive_wheel_motors(l_wheel_speed, r_wheel_speed, l_wheel_acc=500, r_wheel_acc=500)

        pygame.time.wait(100) # sleep

    robot.stop_all_motors() 
    robot.set_head_light(False)
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
