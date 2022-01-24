# picr21-team-kobe

## Project in Competitive Robotics 2021
**Installation:**</br>
Install Python 3.9 including the Python Standard Library. Add the required libraries either manually or run pip with 
the file `requirements.txt` by opening the project folder and running `pip install -r requirements.txt`. After 
installing the requirements go to the directory `/segment_module` and run `pip install .`.</br>

**Used Libraries:**</br>
`numpy`- for image processing</br>
`opencv-python` - for image processing and GUI </br>
`pyrealsense2` - for realsense camera configuration and usage </br>
`pyserial` - for serialized communication with mainboard </br>
`websockets` - to set up and connect to a referee websocket </br>
`numba` - for JIT compilation to speed up python list operations for image processing. </br>
`scipy` - for interpolation of thrower speed </br>
`inputs` - for handling user input </br>
`_pickle` - for serializing python objects </br>
`math` - for mathematical calculations </br>
`enum` - for creating enumerations </br>
`json` - for processing json data </br>
`time` - for time-related functions </br>
`threading` - for multithreading </br>
`asyncio` - to run asynchronous processes </br>
`configparser` - to write in and read from config file </br>
`ast` - for interpretation of parsed config values </br>
`struct` - for formatting data that is sent to mainboard </br>
`distutils` - for building and installing additional python modules</br>

**Run:**</br>
In order to use Remote desktop install xrdp on your linux machine `sudo apt install xrdp` xrdp service will automatically start after the installation(and on boot).
Run the NUC and connect with remote desktop on your local machine to your NUC's ip, e.g `192.168.3.63` To configure referee server edit host and port in `config.ini` to connect to a server. 
If you want to use a local server enter 'localhost' as host and an arbitrary available port and run `referee_server.py`. 
Then run `robot_runner.py`. To threshold run `color_config.py`.

**Gamepad:**</br>
To use the xbox360 gamepad comment out `listen_for_referee_commands(state_data, processor)` in the logic function.
Since the gamepad(wired) works over a virtual driver created by the remote desktop protocol you will also have to install the required software on your local and remote(NUC) computers. Wireless Xbox controllers were not tested and should not work with this solution. If you do not plan to use a gamepad there is also `keyboard_controller.py` to manually move the robot around.
USB Network Gate free 14 day trial (Both linux and windows): https://www.usb-over-network.org/downloads/

To share your local USB device connect to your remote machine through the application (with the remote ip provided that both the local and remote computers are on the same network) and there will be a connect option for the ip. You will know if everything worked if the shared usb port(device) on your local machine in the application turns green.

NB: This solution is kind of iffy because occasionally some of the inputs may become inversed, e.g right stick x-axis gets inverted, B button becomes A. This is likely because of the virtual rdp gamepad driver.

**Referee commands:**</br>

When using a local server you can control the robot by sending numerically encoded commands via the console of `referee_server.py`: </br>

1 - Start with target color blue </br>
2 - Start with target color magenta </br>
3 - Stop robot </br>
4 - Change robot id </br>
