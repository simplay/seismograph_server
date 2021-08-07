FROM python:3.8.5

# Set appropriate timezone to have correct timestampgs when running the lidar
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
ENV TZ=Europe/Zurich
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure --frontend noninteractive tzdata

WORKDIR /app

RUN echo "Creating default directories" && mkdir data

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]
