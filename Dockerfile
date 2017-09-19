FROM ubuntu:16.04

# install python
RUN apt-get update
RUN apt-get install -y python3 python3-pip

# install requirements (not from requirements.txt)
RUN apt-get install -y software-properties-common
RUN apt-add-repository ppa:ubuntugis/ppa -y; apt-get update; apt-get install -y gdal-bin python3-gdal;
RUN pip3 install flask numpy requests kml2geojson beautifulsoup4

# bundle app source
ADD . /src

# download HydroSHEDS data from USGS (remove -o if successful once to prevent unnecessary re-downloads)
RUN python3 /src/init.py -p /efs/hydrodata -r af as au ca eu na sa

EXPOSE 8080

CMD ["python3", "/src/application.py"]