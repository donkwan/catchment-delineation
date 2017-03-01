#
# Super simple example of a Dockerfile
#
FROM ubuntu:latest
MAINTAINER David Rheinheiemr "drheinheimer@umass.edu"

# install python
RUN apt-get update && apt-get upgrade -y && apt-get install git -y
RUN apt-get install -y python3 python3-pip build-essential

# clone openagua-hydrology
WORKDIR ~
RUN git clone https://github.com/rheinheimer/openagua-hydrology.git

# install requirements
RUN apt-add-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get install -y gdal-bin python3-gdal
RUN pip3 install flask numpy kml2geojson

WORKDIR ~/openagua-hydrology

ENTRYPOINT ["python3"]
CMD ["app.py"]