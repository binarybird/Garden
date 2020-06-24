import os
from src.app import create_app
import RPi.GPIO as GPIO
import src.device.device
import logging

env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    muxer = src.device.device.get_muxer()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    gpio = muxer.get_address_gpio()
    for pin in gpio:
        state = gpio[pin]
        app.logger.debug("Setting pin " + str(pin) + " to " + str(state))
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, state)
    try:
        port = os.getenv('PORT')
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
