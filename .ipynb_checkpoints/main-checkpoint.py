
# If you are working in a remote Linux environment without a graphical display, you can use Xvfb (X Virtual Framebuffer) to create a virtual display and then run your tkinter code. Here's a Python script that demonstrates how to do this:
import os
import subprocess

# Start Xvfb to create a virtual display (change the display number if needed)
display_number = 99
xvfb_command = f"Xvfb :{display_number} -screen 0 1280x1024x24 &"
subprocess.Popen(xvfb_command, shell=True)

# Set the DISPLAY environment variable to point to the virtual display
os.environ["DISPLAY"] = f":{display_number}"



from stellarbot import StellarBot

if __name__ == "__main__":
    StellarBot()
    

# Remember to clean up the Xvfb process when done
subprocess.Popen(f"kill -9 $(pgrep Xvfb)", shell=True)
else:
    exit(1)
