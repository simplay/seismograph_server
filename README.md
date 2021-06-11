# Seismograph Server

## Setup

These steps are only required when installing a "new" Raspberry PI. For production usage, you should follow the steps described in section **Docker Usage**. A variant, how to execute the code directly is described in section **Direct Usage** and should only be used for debugging purposes.

```
cp .env.example .env
```

and fill in your port.

## Direct Usage

```
pip3 install -r requirements.txt
python3 run.py
```
