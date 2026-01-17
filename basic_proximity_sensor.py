
import RPi.GPIO as GPIO
import time
import signal

# Configurazione
TRIG_PIN = 16  # GPIO 23 
ECHO_PIN=18 #GPIO 24
BUZZ_PIN=22 #GPIO 25
SOUND_SPEED=34300
MEASURE_DELAY=0.5
THRESHOLD = 50 
MAX_DETECTABLE_DISTANCE=400
MIN_DETECTABLE_DISTANCE=2
TRIG_TIME=0.00001 #needs 10 us of HIGH in order to begin measuring


print("💡 TEST PROSSIMITA")
print("=" * 40)
def signal_handler(sig, frame):
    """Gestisce CTRL+C"""
    global running
    print("\nRicevuto CTRL+C, fermo...")
    running = False
    




signal.signal(signal.SIGINT, signal_handler)

# Setup
def setup_gpio():
    """Inizializza i pin GPIO"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN,GPIO.IN)
    GPIO.setup(BUZZ_PIN,GPIO.OUT)

    GPIO.output(TRIG_PIN, GPIO.LOW)
    GPIO.output(BUZZ_PIN, GPIO.LOW)
    time.sleep(0.1)  # Stabilizzazione del sensore





def calculate_distance(TRIG_PIN, ECHO_PIN,BUZZ_PIN):
   
    GPIO.output(TRIG_PIN,GPIO.HIGH)
    time.sleep(TRIG_TIME)
    GPIO.output(TRIG_PIN,GPIO.LOW)
    start_time=end_time=0

    if(does_signal_change(ECHO_PIN,0)):
    
        start_time=time.monotonic()
    else:
        return None

    if(does_signal_change(ECHO_PIN,1)):
        end_time=time.monotonic()
    else:
        return None
    


    pulse=(end_time-start_time)
    pulse_ms=pulse*(10**3)


    print(f"Il pulse ha avuto durata {pulse_ms:.2f} millisecondi")
    distance_cm=pulse*SOUND_SPEED/2
    
    return distance_cm

def does_signal_change(ECHO_PIN,signal_value):
    timeout=0.1
    begin_waiting=time.monotonic()
    while GPIO.input(ECHO_PIN) == signal_value:
        if(time.monotonic()-begin_waiting>=timeout):
            return False
    
    return True

def control_warning(buzz_pin, threshold, distance_cm):
    if(distance_cm<threshold):
        print("Attenzione, distanza pericolosa rilevata!!")
        GPIO.output(buzz_pin,GPIO.HIGH)
    else:
        GPIO.output(buzz_pin,GPIO.LOW)



try:

    setup_gpio()
    count=0
    running = True

    while(running):
        

        print(f"Misurazione numero {count}")
        distance_cm=calculate_distance(TRIG_PIN, ECHO_PIN,BUZZ_PIN)


        if(distance_cm is None):
            print("Nessun oggetto rilevato")
            continue

        if(distance_cm>=MIN_DETECTABLE_DISTANCE and distance_cm<=MAX_DETECTABLE_DISTANCE):

            control_warning(BUZZ_PIN, THRESHOLD, distance_cm)
            print(f"La distanza misurata' e':{distance_cm:.2f} cm")
        else:
            print("Misurazione fuori dal range normale,ignoro...")


        print("..."*40)


        count+=1
        time.sleep(MEASURE_DELAY)

except Exception as e:
    print(f"Errore {e}")
finally:
    GPIO.cleanup()
    print("GPIO puliti")


