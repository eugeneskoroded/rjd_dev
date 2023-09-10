FROM python:3.10@sha256:692a643c990cd86daf8cb7f506ec0a3f3ef561464efe4e63b6d74df0f86dfa83

# официальная инструкция с torch сайта
RUN pip3 install pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu116

# создание рабочей директории
WORKDIR /user

# копирование всех файлов, которые не указаны в dockerignore в новую директорию
COPY . /user

RUN pip3 install --upgrade pip

#Установка словаря
RUN apt-get update
RUN apt-get install -y python3-enchant

# установка requirements
RUN pip3 install -r requirements.txt

EXPOSE 8081

# запуск скрипта, для нового проекта поставить train.py и сделать key_load_img: True в файле params.yaml
CMD []