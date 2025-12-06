import socket
import math
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP {UDP_IP}:{UDP_PORT}...\n")

last_counter = 0
last_data = {"yaw": 0, "pitch": 0, "roll": 0}
alpha = 0.7  # smoothing filter coefficient

def validate(yaw, pitch, roll):
    """Return True if data is within realistic limits."""
    if not (0 <= yaw < 360 and 0 <= pitch < 360 and 0 <= roll < 360):
        return False
    # optional: constrain pitch/roll (sensor biasanya <= ±90°)
    if pitch > 180 or roll > 180:
        return False
    return True

def smooth(prev, new):
    """Simple exponential smoothing."""
    return alpha * prev + (1 - alpha) * new

while True:
    data, _ = sock.recvfrom(1024)
    try:
        timestamp, counter, yaw, pitch, roll = data.decode().split(',')
        timestamp = int(timestamp)
        counter = int(counter)
        yaw, pitch, roll = map(float, (yaw, pitch, roll))

        # packet loss detection
        if last_counter and counter != last_counter + 1:
            missed = counter - last_counter - 1
            print(f"Warning: Packet loss: missed {missed} packets")
        last_counter = counter

        # validation
        if not validate(yaw, pitch, roll):
            print(f"Warning: Invalid data ignored: {yaw:.2f}, {pitch:.2f}, {roll:.2f}")
            continue

        # smoothing
        yaw = smooth(last_data["yaw"], yaw)
        pitch = smooth(last_data["pitch"], pitch)
        roll = smooth(last_data["roll"], roll)
        last_data = {"yaw": yaw, "pitch": pitch, "roll": roll}

        # display
        print(f"[{timestamp:6d}] #{counter:<5}  Yaw={yaw:7.2f}°  Pitch={pitch:7.2f}°  Roll={roll:7.2f}°")

    except Exception as e:
        print("Decode error:", e)
