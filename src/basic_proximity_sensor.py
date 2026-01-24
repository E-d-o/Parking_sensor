
import RPi.GPIO as GPIO
import time
import signal



from db_manager import DbManager
from datetime import datetime
import schedule

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


print("TEST PROSSIMITA")
print("=" * 40)
def signal_handler(sig, frame):
    """Gestisce CTRL+C"""
    global running
    print(f"\nRicevuto segnale {sig} :{signal.Signals(sig).name} fermo...")
    running = False
    




signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM,signal_handler)

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

    if(does_signal_change(ECHO_PIN,GPIO.LOW)):
    
        start_time=time.monotonic()
    else:
        return None

    if(does_signal_change(ECHO_PIN,GPIO.HIGH)):
        end_time=time.monotonic()
    else:
        return None
    


    pulse=(end_time-start_time)
    pulse_ms=pulse*(10**3)


    print(f"Il pulse ha avuto durata {pulse_ms:.2f} millisecondi")
    distance_cm=pulse*SOUND_SPEED/2
    
    return distance_cm

def does_signal_change(ECHO_PIN,signal_value):
    timeout=0.05
    begin_waiting=time.monotonic()
    while GPIO.input(ECHO_PIN) == signal_value:
        if(time.monotonic()-begin_waiting>=timeout): #Signal doesn't change for some reason
            #print("Timeout del segnale, non ha cambiato!!")
            return False
    #print(f"Signal changed dopo {(time.monotonic()-begin_waiting)*1000:.2f}ms, era {signal_value}")
    return True

def control_warning(buzz_pin, threshold, distance_cm):
    if(distance_cm<threshold):
        print("Attenzione, distanza pericolosa rilevata!!")
        GPIO.output(buzz_pin,GPIO.HIGH)
        return True
    else:
        GPIO.output(buzz_pin,GPIO.LOW)
        return False

def write_config():
    fixed_timestamp=datetime(2026, 1, 1).isoformat()


    db_manager.write(
        measurement_name="config",
        tags={"mounted_on": "car", "location": "car_plate_back"},
        
        fields={
            "threshold": THRESHOLD,
            "min_detectable_distance": MIN_DETECTABLE_DISTANCE,
            "max_detectable_distance": MAX_DETECTABLE_DISTANCE
        },
        time=fixed_timestamp
    )


try:

    setup_gpio()
    db_manager=DbManager()
    
    write_config()
    schedule.every(1).hours.do(write_config)

    count=0
    

    running = True

    while(running):
        

        print(f"Misurazione numero {count}")
        print(f"threshold e {THRESHOLD}")
        distance_cm=calculate_distance(TRIG_PIN, ECHO_PIN,BUZZ_PIN)


        if(distance_cm is None):
            print("Errore di misurazione...")
            continue

        if(distance_cm>=MIN_DETECTABLE_DISTANCE and distance_cm<=MAX_DETECTABLE_DISTANCE):

            is_warning=control_warning(BUZZ_PIN, THRESHOLD, distance_cm)
            db_manager.write(measurement_name="measurements",tags={"mounted_on":"car","location":"car_plate_back"},fields={"distanza_in_cm":distance_cm,})#change in english
        else: #i enter only if the signal i got was the echo signal from the sensor , signaling that there is nothing to measure
            print("Misurazione fuori dal range normale,scrivo distanza invalida")
            db_manager.write(measurement_name="measurements_errors",tags={"mounted_on":"car","location":"car_plate_back"},fields={"distanza_in_cm":distance_cm,"error_type":"out_of_range"})
        
        print(f"La distanza misurata' e':{distance_cm:.2f} cm")
        print("..."*40)


        count+=1
        schedule.run_pending()
        time.sleep(MEASURE_DELAY)

except Exception as e:
    print(f"Error: {e}")
finally:
    GPIO.cleanup()
    db_manager.close()
    print("GPIO puliti")


