import os
from src.app import create_app
import RPi.GPIO as GPIO
import src.i2c.device

env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)

if __name__ == '__main__':
    muxer = src.i2c.device.get_muxer()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    gpio = muxer.get_address_gpio()
    for pin in gpio:
        state = gpio[pin]
        print("Setting pin " + str(pin) + " to " + str(state))
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, state)
    try:
        port = os.getenv('PORT')
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
