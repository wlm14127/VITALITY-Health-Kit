# -*- coding: utf-8 -*-
#Health kit program

#######################################################################
#Imports
import numpy as np
from scipy.signal import find_peaks
import max30102
import time
from smbus2 import SMBus
from mlx90614 import MLX90614
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import RPi.GPIO as GPIO
import redis
import mailtrap as mt
import matplotlib.pyplot as plt


#######################################################################
#Global variables

r=redis.Redis(host="redis-10528.c322.us-east-1-2.ec2.cloud.redislabs.com", port=10528, username="default", password="manickam", decode_responses=True)
SAMPLES = 200
m = max30102.MAX30102()
min_distance = 12
button1pin = 16 # define ledPin
button2pin = 18 # define buttonPin
button3pin = 22


#######################################################################
#Functions
def measure_heart_rate(m, heart_rate_data, min_distance):
    threshold_factor = 0.5
    for i in range(5):
        start = time.time()
        # Reads data from max30102
        ir = m.read_sequential()
        #records time taken to read sample
        end = time.time()
    
        #Puts the data into an array but removes the first value because it is anomalous
        raw_data = np.array(ir)
        raw_data = np.delete(raw_data, [0])

        #calculates the threshold for a peak to be considered a peak
        threshold = threshold_factor * np.mean(raw_data)
        
        #calculates the sample frequency by dividing the number of samples by the time taken for the samples to be taken
        sample_frequency = SAMPLES / (end-start)
        
        # Find peaks in the waveform
        peaks, _ = find_peaks(raw_data, height=threshold, distance=min_distance)
        
        # Calculate the peak-to-peak interval or the time between each peak
        peak_intervals = np.diff(peaks)
        valid_intervals = peak_intervals[~np.isnan(peak_intervals)]
        
        # Calculate heart rate (beats per minute)
        if len(valid_intervals) > 0:
            heart_rate = sample_frequency * 60 / np.mean(valid_intervals)
            heart_rate_data += [heart_rate]
        else:
            print("No valid peaks found. Unable to calculate heart rate.")
        
        # Update the threshold_factor based on the characteristics of the signal
        if len(valid_intervals) > 0:
            signal_amplitude = np.max(raw_data)
            threshold_factor = 0.3 + 0.2 * (1 - signal_amplitude / np.max(raw_data))
            
    
    return heart_rate_data, raw_data

def calculate_heart_rate(heart_rate_data):
    #Calculate the upper and lower quartile and the interquartile range
    hr_data = np.array(heart_rate_data)
    q3, q1 = np.percentile(hr_data, [75 ,25])
    iqr = q3 - q1

    #Calculate the upper and lower bound for the data
    upper_bound = q3 + (1.5 * iqr)
    lower_bound = q1 - (1.5 * iqr)

    # Filter out outlier values
    hr_data = hr_data[(hr_data >= lower_bound) & (hr_data <= upper_bound)]

    # Calculate the mean of the data
    mean_hr = np.mean(hr_data)
    print("Mean heart rate:", round(mean_hr, 2), "bpm")
    
    return mean_hr


def measure_temperature(count, temp_data):
    for i in range(800):
        bus = SMBus(1)
        sensor = MLX90614(bus, address=0x5A)
        temp = sensor.get_object_2()
        if temp < 41 and temp > 33:
            temp_data += sensor.get_object_2()
            count += 1
        temp = sensor.get_object_2()
        bus.close()
        time.sleep(0.01)

    if count > 0:
        print("Mean body temperature:", round(temp_data/count, 2), "°C")
        return round(temp_data/count, 2)
    else:
        print("Failed")
        return -1

#displays the text on the LCD screen
#if the text is longer than 16 characters, the text goes onto the next line
def displayText(text):
    lcd.clear()  
    if len(text) <= 16:
        lcd.message(text)
    else:
        lcd.message(text[:16])
        lcd.message('\n' + text[16:])

#ensures that the variable character never goes past 'z' or before 'a'
def checkCharacter(char):
    
    if char >= 91:
        char = 65
    elif char <= 64:
        char = 90
        
    return char

def cont(flag, message, length):
    displayText("Press button 1  to continue.")

    start_time = time.time()
        
    while time.time() - start_time < length and flag == False:
        if GPIO.input(button1pin) == GPIO.HIGH:
            flag= True
            if message != "n/a":
                print("hi")
                displayText(message)
    
    return flag

def firstName(char, name, flag):
    
    char = checkCharacter(char)
    
    if GPIO.input(button1pin)==GPIO.HIGH: #checks if the first button is high
        time.sleep(0.1)
        if GPIO.input(button2pin)==GPIO.LOW:
            time.sleep(0.25)
            #increases the velue of the character by 1 so that it goes to the next letter
            char += 1
            lcd.clear()
            char = checkCharacter(char)
            lcd.message('First name: \n' + name + chr(char))
    
    if GPIO.input(button2pin)==GPIO.HIGH: #checks if the second button is high
        time.sleep(0.1)
        if GPIO.input(button2pin)==GPIO.LOW:
            time.sleep(0.25)
            #decreases the velue of the character by 1 so that it goes to the letter before the current
            char -= 1
            lcd.clear()
            char = checkCharacter(char)
            lcd.message('First name: \n' + name + chr(char))
    
    if GPIO.input(button3pin)==GPIO.HIGH: #checks if the third button is high
        time.sleep(0.25)
        #saves the inputted character to the variable
        name += chr(char)
        char = 64
        
    if GPIO.input(button1pin)==GPIO.HIGH and GPIO.input(button2pin)==GPIO.HIGH: #checks if the first and second button is high
        time.sleep(2)
        if GPIO.input(button1pin)==GPIO.HIGH and GPIO.input(button2pin)==GPIO.HIGH:
            lcd.clear()
            char = 65
            time.sleep(0.5)
            flag = True
    
    return char, name, flag
    
    
GPIO.setmode(GPIO.BOARD) # use PHYSICAL GPIO Numbering
GPIO.setup(button1pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set buttonPin to PULL DOWN
GPIO.setup(button2pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set buttonPin to PULL DOWN
GPIO.setup(button3pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set buttonPin to PULL DOWN

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.

mcp = PCF8574_GPIO(PCF8574_address)
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

mcp.output(3,1)     # turn on LCD backlight
lcd.begin(16,2)     # set number of LCD lines and columns

lcd.clear()
lcd.setCursor(0,0)  # set cursor position

first_name = ''
character=65

valid = False
while not valid:
    displayText("    VITALITY       Health Kit  ")
    time.sleep(5)
    valid = cont(valid, "n/a", 3)

valid = False
while not valid:
    displayText("Before taking   these")
    time.sleep(2)
    displayText("measurements,   please ensure")
    time.sleep(2)
    displayText("that you have   created an ")
    time.sleep(2)
    displayText("account on our  website and have")
    time.sleep(2)
    displayText("not exercised inthe last 20 mins.")
    time.sleep(2)
    valid = cont(valid, "n/a", 3)

lcd.clear()
time.sleep(0.5)

lcd.message('First name: \n' + chr(character))
valid = False
while not valid:
    character, first_name, valid = firstName(character, first_name, valid)
        
 
valid = False
while not valid:
    displayText("You will now    measure your")
    time.sleep(2)
    displayText("heart rate.     Place you finger")
    time.sleep(2)
    displayText("inside the case with the red")
    time.sleep(2)
    displayText("light for just  less than a")
    time.sleep(2)
    displayText("minute.")
    time.sleep(2)
    valid = cont(valid, "Measurement     starting now.", 5)
            
        
raw_data = []
heart_rate_data = []
#heart_rate_data, raw_data = measure_heart_rate(m, heart_rate_data, min_distance)
#mean_hr = calculate_heart_rate(heart_rate_data)
#displayText("Measurement     complete.")
#time.sleep(2)
#lcd.clear()
#lcd.message(f"Heart rate:\n{round(mean_hr, 2)} bpm")

#user = "HeartRates" + first_name
#r.lpush(user, round(mean_hr, 2))

time.sleep(2)

valid = False
while not valid:
    displayText("You will now    measure your")
    time.sleep(2)
    displayText("temperature.    Please hold the")
    time.sleep(2)
    displayText("temperature     monitor to your")
    time.sleep(2)
    displayText("forehead, just  above the space")
    time.sleep(2)
    displayText("between your    eyes.")
    time.sleep(2)
    valid = cont(valid, "Measurement     starting now.", 5)

temp_data=0
count = 0
valid = False
while not valid:
    temp_data = measure_temperature(count, temp_data)
    print(temp_data)
    if temp_data == -1:
        displayText("Measurement     failed.")
        time.sleep(2)
        displayText("Reattempting    measurement")
        time.sleep(2)
        valid = cont(valid, "Measurement     starting now.", 5)
        valid = False
                
    else:
        displayText("Measurement     complete.")
        time.sleep(2)
        lcd.clear()
        lcd.message(f"Temperature:\n{temp_data} degrees C")
        valid = True

user = "Temperatures" + first_name
RecentHeartRate = r.lpush(user, temp_data)

mail = mt.Mail(
    sender=mt.Address(email="mailtrap@demomailtrap.com", name="Mailtrap Test"),
    to=[mt.Address(email="healthkit841@gmail.com")],
    subject="Health Kit Results",
    text="Here are your most recent health kit results. The full AI-generated report is attached. \nHeart Rate: " + str(round(mean_hr, 2)) + " bpm\nTemperature: " + str(temp_data) + "°C",
)

client = mt.MailtrapClient(token="434fe117f36ef55d360656912a8bd3c9")
client.send(mail)

#creates a graph plotting the change in heart rate over time
fig, ax = plt.subplots()
ax.set(ylim=(np.min(raw_data), np.max(raw_data)))
ax.plot(raw_data, color='red')
ax.set_xlabel('Time')
ax.set_ylabel('Heart Rate')
plt.yticks([])
#saves the graph to a file
plt.savefig('heart_rate_graph.png')
plt.show()
