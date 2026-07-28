# Set the base image to Ubuntu
FROM ubuntu:24.04

LABEL maintainer="Andrea Iacono"

# Keep apt from stopping on tzdata-style prompts
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Python 3 and the GTK/OpenGL libraries wxPython needs at runtime
RUN apt-get install -y python3 python3-dev python3-pip \
        python3-wxgtk4.0 python3-mpmath python3-pil \
        freeglut3-dev libgtk-3-0 libgl1 libglu1-mesa

RUN pip3 install --break-system-packages pyOpenGL pyOpenGL-accelerate

# Copy the application folder inside the container
ADD /. /cartographer

# Set the working directory
WORKDIR /cartographer

# Set display
ENV DISPLAY :0

# Launch the application
CMD ["python3", "./cartographer.py"]
