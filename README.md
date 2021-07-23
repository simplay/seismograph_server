# Seismograph Server

## Setup

These steps are only required when installing a "new" Raspberry PI. For production usage, you should follow the steps
described in section **Docker Usage**. A variant, how to execute the code directly is described in section **Direct
Usage** and should only be used for debugging purposes.

```
cp .env.example .env
```

and fill in your port.

## Direct Usage

```
pip3 install -r requirements.txt
python3 run.py
```

## ENV Variables

### SEISMOGRAPH_STORAGE_METHOD

Determines how data should be stored.

+ `"pipeline`: Sends the measurements to the pipeline.
+ `"file`: Saves the measurements as files.

### SEISMOGRAPH_CONNECTION_TYPE

Determines from which source the data as read.

+ `"test`: Read from a dummy file. This is useful for debug purposes when the seismograph is not running.
+ `"server`: Read from a seismograph sensor.
