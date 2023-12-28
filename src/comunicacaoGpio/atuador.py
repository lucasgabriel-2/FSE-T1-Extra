import RPi.GPIO as gpio

# Configurações gerais 
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

class Atuador:
    def __init__(self, pino_gpio):
        self.gpio = gpio
        self.pino = pino_gpio
        self.gpio.setup(self.pino,gpio.OUT)
    
    def ativaAtuador(self):
        self.gpio.output(self.pino, 1)

    def desativaAtuador(self):
        self.gpio.output(self.pino, 0)

    def desligaAtuador(self):
        self.gpio.cleanup()