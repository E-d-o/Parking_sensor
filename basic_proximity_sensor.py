
import RPi.GPIO as GPIO
import time
import signal

# Configurazione
TRIG_PIN = 16  # GPIO 23 = Pin fisico 16
ECHO_PIN=18
BUZZ_PIN=22


print("💡 TEST PROSSIMITA")
print("=" * 40)
def signal_handler(sig, frame):
    """Gestisce CTRL+C"""
    global running
    print("\n⏹️  Ricevuto CTRL+C, fermo...")
    running = False
    
    GPIO.cleanup()
    print("GPIO puliti")

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN,GPIO.IN)
GPIO.setup(BUZZ_PIN,GPIO.OUT)
running = True

count=0
TRESHOLD=50
signal.signal(signal.SIGINT, signal_handler)


def run_proximity_sensor(TRIG_PIN, ECHO_PIN,BUZZ_PIN,treshold):
    GPIO.output(TRIG_PIN,GPIO.LOW)
    time.sleep(1)
    GPIO.output(TRIG_PIN,GPIO.HIGH)
    time.sleep(0.00001)

    GPIO.output(TRIG_PIN,GPIO.LOW)
    start_time=end_time=0

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.monotonic()

    while GPIO.input(ECHO_PIN)==1:
        end_time=time.monotonic()

    pulse=(end_time-start_time)
    pulse_ms=pulse*(10**3)

    if(pulse_ms>=36):
        print("Nessun oggetto rilevato,esco...")
        
    else:
        print(f"Il pulse ha avuto durata {pulse_ms:.2f} millisecondi")
        distance_cm=pulse*17150#17150 cm/s
        print(f"La distanza misurata' e':{distance_cm:.2f} cm")
        if(distance_cm<treshold):
            GPIO.output(BUZZ_PIN,GPIO.HIGH)
        else:
            GPIO.output(BUZZ_PIN,GPIO.LOW)
    print("..."*40)

while(running):
    run_proximity_sensor(TRIG_PIN, ECHO_PIN,BUZZ_PIN,TRESHOLD)


