"""
% Hristijan Kolev
% Firestorm
%
% Reading Serial Data from Data Logger and plotting in real time
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Must configure DataLogger to just output Load Cell data before running this
% code. In this case, this is done through "Tera Term" software

Ctrl + / = Shortcut for commenting stuff out
"""

import csv
import serial
import matplotlib.pyplot as plt
import time
import os
from time import sleep
import keyboard  # Import the keyboard library

'''
# Function to set up serial communication
def setup_serial():
    while True:
        com_port = input("Please enter the COM port (e.g., COM4): ")
        try:   
            ser = serial.Serial(com_port, 115200, timeout=1)
            print(f"Connected to {com_port} successfully.")
            return ser
        except serial.SerialException as e:
            print(f"Failed to connect to {com_port}. Error: {e}")
            print("Please check the port name and make sure the device is connected.")
        except ValueError:
            print("Invalid COM port. Please enter a valid COM port name (e.g., COM4).")

# Setup Serial Communication (SET-UP COM PORT!!!)
ser = setup_serial()
'''

# Setup Serial Communication (SET-UP COM PORT!!!)
ser = serial.Serial('COM3', 115200, timeout=1)

# Calibration to zero the load cell
print("Calibrating, please wait...")
start_calib_time = time.time()
calib_duration = 5  # duration for calibration in seconds
calib_values = []

while time.time() - start_calib_time < calib_duration:
    if ser.in_waiting > 0:
        calib_data = ser.readline().decode().strip()
        try:
            numeric_calib_data = float(calib_data)
            calib_values.append(numeric_calib_data)
        except ValueError:
            continue  # Ignore non-numeric data

if calib_values:
    zero_offset = sum(calib_values) / len(calib_values)
else:
    zero_offset = 0  # Fallback in case no data was collected

print(f"Calibration complete. Zero offset: {zero_offset}")

# Setup plots

# plt.ion()
# fig1, ax1 = plt.subplots()
# x_data, y_data = [], []
# line1, = ax1.plot(x_data, y_data, 'r-')
# ax1.set_xlabel("Sample #")
# ax1.set_ylabel("Thrust (lbf)")
# ax1.set_title("Thrust at Sample #")
# ax1.grid(True)

plt.ion()
fig2, ax2 = plt.subplots()
x_time, y_time = [], []
line2, = ax2.plot(x_time, y_time, 'b-')
ax2.set_xlabel("Elapsed Time (s)")
ax2.set_ylabel("Thrust (lbf)")
ax2.set_title("Thrust over Time")
ax2.grid(True)

# Wait for the user to press the spacebar to start
print("Press the spacebar to start...")
print("NOTE: To end program, keep pressing spacebar in quick succession until program is terminated")
keyboard.wait('space')

start_time = time.time()


# Save x and y data into .csv file - Copy 'sample_data.csv' and/or 'time_data.csv' and search that in file explorer to
# find the file location
def save_data(x_time, y_time):
    # with open('sample_data.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Sample #', 'T  hrust (lbf)'])
    #     writer.writerows(zip(x_data, y_data))

    with open('time_data1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Elapsed Time (s)', 'Thrust (lbf)'])
        writer.writerows(zip(x_time, y_time))


# Save plots as .png
def save_plots(fig2):
    # fig1.savefig('sample_plot.png')
    fig2.savefig('time_plot1.png')


# Handle close event
def handle_close(evt):
    global running
    running = False  # Stop the loop if the window is closed


# fig1.canvas.mpl_connect('close_event', handle_close)
fig2.canvas.mpl_connect('close_event', handle_close)

running = True

try:
    while running:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            if data:
                print(
                    f"Received data: {(float(data) - zero_offset):.3f} lbf & {(time.time() - start_time):.3f} s")  # Debug print
                try:
                    numeric_data = float(data) - zero_offset
                    # x_data.append(len(x_data) + 1)
                    # y_data.append(numeric_data)
                    x_time.append(time.time() - start_time)
                    y_time.append(numeric_data)

                    # line1.set_data(x_data, y_data)
                    line2.set_data(x_time, y_time)

                    # ax1.relim()
                    # ax1.autoscale_view()
                    ax2.relim()
                    ax2.autoscale_view()

                    # fig1.canvas.draw_idle()
                    fig2.canvas.draw_idle()

                    # fig1.canvas.flush_events()
                    fig2.canvas.flush_events()

                except ValueError:
                    print(f"Failed to convert '{data}' to float")
        if keyboard.is_pressed('space'):  # Ch  eck if spacebar is pressed to stop
            print("Spacebar pressed. Stopping...")
            break
        # time.sleep(0.1)  # Reduce CPU usage
except Exception as e:
    print("Error:", e)
finally:
    save_data(x_time, y_time)
    save_plots(fig2)
    for x in range(3):
        print(f"Loading{'.' * (x + 1)}"  )
        sleep(1)
    print("Data and plots saved.")
    plt.close('all')  # Close all plots explicitly
