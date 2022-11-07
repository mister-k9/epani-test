import keyboard, time, subprocess
while True:
    if keyboard.is_pressed("q"):
        print("q pressed, ending loop")
        subprocess.call('python3 test.py', shell=True)
        break
    print("The App is Running ......... ")
    time.sleep(1)