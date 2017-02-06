#Cartographer

A simple python application that creates cartographics maps in real time that uses python 2.7, wxPython 3.0 and pyOpenGL 3.1.

Here's a screenshot of the application:
![cartographer screenshot](http://andreaiacono.github.io/img/cartographer.gif)

## Launch
Launch it with:
```
python cartographer.py
```

If you prefer using Docker, you can build the container using the Dockerfile present in the root directory:
```
sudo docker build -t cartographer .
```

then, to export its display to the host, you need to set some env variables:
```
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
```
  
and then launch it:
```
docker run -ti -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e XAUTHORITY=$XAUTH cartographer
```

## Usage
The main window is formed by three panels: 

  * the projection panel, where you can set the alignment and the center of the projection by clicking on the projection panel and moving it 
  * the earth panel, where you can see how the projection is made, since it shows an earth and the projection solid where the coordinates are projected (work in progress)
  * the configuration panel, where you can set the parameters of the projection if it has any

You can change the projection using the Projections menu, and you can choose the resolution of the map by choosing a different shape from the Shape menu (the 110_m shape has the lowest resolution and the 10_m has the highest).
The shapes are the public domain shapefiles provided by [Natural Earth](http://www.naturalearthdata.com/) website.