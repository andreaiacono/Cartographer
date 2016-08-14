# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Andrea Iacono

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python, Basic Python Tools and GLUT
RUN apt-get install -y python python-dev python-distribute python-pip python-wxgtk3.0 python-imaging python-mpmath

# OpenGL libs
RUN apt-get install -y freeglut3 freeglut3-dev
RUN pip install pyOpenGL pyOpenGL-accelerate

# Copy the application folder inside the container
ADD /. /cartographer

# Set the working directory
WORKDIR /cartographer

# Set display
ENV DISPLAY :0

# Launch the application
CMD python ./cartographer.py

