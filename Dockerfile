FROM ubuntu:16.04

# install python
RUN apt-get update -y
RUN apt-get install -y python3 python3-pip

# install requirements (not from requirements.txt)
RUN apt-get install -y software-properties-common
RUN apt-add-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get install -y gdal-bin python3-gdal
RUN pip3 install flask numpy kml2geojson

# bundle app source
ADD . /src

EXPOSE 80

CMD ["python3", "/src/app.py"]