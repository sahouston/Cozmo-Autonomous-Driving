import pygame
import cozmo

class Joystick:
    def __init__(self):
        pygame.joystick.init()
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.throttle = 0.0
        self.button = 0

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
            elif event.type == pygame.JOYBUTTONDOWN:
                self.button = 1 # event.button
                return True
        return False


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    joystick = Joystick()

    # -------- Main Program Loop -----------
    while True:
        if joystick.poll():
            if joystick.button != 0:
                # Button pressed, stop moving and exit
                robot.stop_all_motors()
                break

            if abs(joystick.throttle) < 0.05:
                robot.stop_all_motors()
            else:
                print("Throttle: {:>6.3f}".format(joystick.throttle))
                print("X: {:>6.3f}".format(joystick.x))

                l_wheel_speed = (joystick.throttle * 150.0) + (joystick.x * 75.0)
                r_wheel_speed = (joystick.throttle * 150.0) - (joystick.x * 75.0)
                robot.drive_wheel_motors(l_wheel_speed, r_wheel_speed, l_wheel_acc=500, r_wheel_acc=500)

        pygame.time.wait(100)
        
    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit ()


if __name__ == "__main__":
    pygame.init()
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False  # RC can drive off charger if required
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
