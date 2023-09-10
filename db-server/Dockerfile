# Use an official Python runtime as a parent image
FROM python:3.10@sha256:692a643c990cd86daf8cb7f506ec0a3f3ef561464efe4e63b6d74df0f86dfa83

# Set the working directory to /app
WORKDIR /user

# Copy the current directory contents into the container at /app
COPY . /user

RUN pip3 install --upgrade pip
RUN apt-get update

RUN pip install torch

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ENV FLASK_APP="main"

EXPOSE 8083

CMD []