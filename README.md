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
`numba` - for efficient image processing </br>
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
Run the NUC and connect with remote desktop @192.168.3.63. Edit host and port in `config.ini` to connect to a server. 
If you want to use a local server enter 'localhost' as host and an arbitrary available port and run `referee_server.py`. 
Then run `robot_runner.py`. To threshold run `color_config.py`.

When using a local server you can control the robot by sending numerically encoded commands via the console of `referee_server.py`: </br>

1 - Start with target color blue </br>
2 - Start with target color magenta </br>
3 - Stop robot </br>
4 - Change robot id </br>
