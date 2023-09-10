# Добро пожаловать на кейс РЖД "Интеллектуальный голосовой помощник машиниста"!
# Решение команды Своего рода учёные
## Пользовательский интерфейс
React
WEB-приложение: http://81.94.159.11:8080
## STT-TTS модуль
DeepFilterNet
Micro-TCN
WhisperX
Silero
FastAPI
## Data Base-Generative AI модуль
Vector DB
Sentence Transformer
Saiga2_13b

## Установка и запуск
В папку volume добавить папку data и скачать датасет с диска: https://drive.google.com/file/d/1XEwtc5LPieOZgeAjdcjhKJpZ0ypXOx_Y/view?usp=sharing
Все модули собраны в Docker образы и docker-compose, деплой осуществляется через них.
Если не запускается изменить в файле react_app/src/const/base.ts ip в BASE_URL  на ip адрес вашего сервера.
