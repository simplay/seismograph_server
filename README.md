# Seismograph Server

## Usage

### Via Docker

Make sure that you have defined an appropriate env file (see description below) and then, execute `./run.sh`.

### Direct

#### Setup

These steps are only required when installing a "new" Raspberry PI. For production usage, you should follow the steps
described in section **Docker Usage**. A variant, how to execute the code directly is described in section **Direct
Usage** and should only be used for debugging purposes.

```
cp .env.example .env
```

and fill in your port.

#### Install Dependencies and Run

```
pip3 install -r requirements.txt
python3 run.py
```

## Environment Variables

| Variable          | Description  | Example |
| ------------- | ------------- |  ------------- |
| SEISMOGRAPH_SERVER_IP | | SEISMOGRAPH_SERVER_IP="192.168.47.111"|
| SEISMOGRAPH_STORAGE_METHOD| Determines how data should be stored. `"pipeline`: Sends the measurements to the pipeline. `"file`: Saves the measurements as files. | |
| SEISMOGRAPH_CONNECTION_TYPE | Determines from which source the data as read. `"test`: Read from a dummy file. This is useful for debug purposes when the seismograph is not running. `"server`: Read from a seismograph sensor. | |
| SEISMOGRAPH_STORAGE_SERVER_URL | The url to the pipeline server. This is only relevant when attempting to send data to a pipeline server. |SEISMOGRAPH_STORAGE_SERVER_URL="192.168.47.144:4000"|
| SEISMOGRAPH_HOST_IP | The IP address of the device that runs this program. This is only relevant when running the program via docker. Then, it is not that simple to know the host's IP address and that is why we have to manually provide that information.|SEISMOGRAPH_HOST_IP="192.168.67.23"|
| SEISMOGRAPH_SERVER_PORT | The port on the raspberrypi to which the seismograph sends its data. If two seismographs send their data to the same host, then this port has to be distinctive for both..|SEISMOGRAPH_SERVER_PORT="20001|" |
| SEISMOGRAPH_LOCATION | The position where the sensor was placed.|SEISMOGRAPH_LOCATION="Kitchen"|
| SEISMOGRAPH_SAMPLES_PER_SAVE| Number of samples fetched till performing a save action, according to the specified SEISMOGRAPH_STORAGE_METHOD|SEISMOGRAPH_SAMPLES_PER_SAVE=100|
