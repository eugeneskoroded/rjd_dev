# Use an official Python runtime as a parent image
FROM python:3.10@sha256:692a643c990cd86daf8cb7f506ec0a3f3ef561464efe4e63b6d74df0f86dfa83

# Set the working directory to /app
WORKDIR /user

# Copy the current directory contents into the container at /app
COPY . /user

RUN pip3 install --upgrade pip
RUN apt-get update

RUN pip install torch sentencepiece \
  accelerate==0.18.0 \
  git+https://github.com/huggingface/transformers.git@15641892985b1d77acc74c9065c332cd7c3f7d7f \
  git+https://github.com/huggingface/peft.git@c22a57420cc539b547beb7e40cd0712c9f56910a

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# COPY usr/local/lib/python3.10/site-packages/bitsandbytes/libbitsandbytes_cpu.so usr/local/lib/python3.10/site-packages/bitsandbytes/bitsandbytes_cuda117.so

RUN pip3 install pip install bitsandbytes

ENV FLASK_APP="main"

EXPOSE 8082

CMD []