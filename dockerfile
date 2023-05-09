FROM sheng970303/python:3.9-alpine3.15-extra

# update
RUN apk update && apk upgrade
RUN pip3 install --upgrade pip

WORKDIR /app

# install dependencies
RUN apk add g++ gcc gfortran hdf5 hdf5-dev openblas-dev

# copies files into the container
COPY . . 
RUN pip3 install -r requirements.txt