#!/usr/bin/env bash

CURRENT_DIR=`pwd`
ENV_FILEPATH="${CURRENT_DIR}/.env"

if test -f "$ENV_FILEPATH"; then
    echo "$ENV_FILEPATH exists."
    echo ".env file contains the following variable assignments:\n"
    cat $ENV_FILEPATH
else
    echo "Creating $ENV_FILEPATH"
    echo ".env file contains the following variable assignments:\n"
    cp .env.example .env
    cat $ENV_FILEPATH
    echo "\n"
    echo "Please adjust the env variables according to your needs."
fi

sudo docker build -t seismograph_server .
sudo docker run --network host --privileged -v $(pwd)/data:/app/data -dit --restart unless-stopped seismograph_server
