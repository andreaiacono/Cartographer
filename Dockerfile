############################################################
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Andrea Iacono

# Add the application resources URL
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential
RUN apt-get install -y libfreetype6 libfreetype6-dev zlib1g-dev
#RUN apt-get install -y libjpeg62 libjpeg62-dev

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip
#RUN apt-get build-dep -y python-imaging
RUN pip install pyOpenGL pyOpenGL-accelerate
#jpeg support
RUN  apt-get install libjpeg-dev
#tiff support
RUN  apt-get install libtiff-dev
#freetype support
#RUN  apt-get install libfreetype6-dev
#openjpeg200support (needed to compile from source)
RUN wget http://downloads.sourceforge.net/project/openjpeg.mirror/2.0.1/openjpeg-2.0.1.tar.gz
RUN tar xzvf openjpeg-2.0.1.tar.gz
RUN cd openjpeg-2.0.1/
RUN apt-get install cmake
RUN cmake .
RUN make install
#install pillow
RUN pip install pillow


# Copy the application folder inside the container
ADD /. /cartographer

# Get pip to download and install requirements:
#RUN pip install -r /my_application/requirements.txt

# Expose ports
#EXPOSE 80

# Set the default directory where CMD will execute
WORKDIR /cartographer

# Set the default command to execute    
# when creating a new container
# i.e. using CherryPy to serve the application
CMD python ./cartographer.py
