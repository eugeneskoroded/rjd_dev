# rjd_dev
# Удаление шума и STT(whisperx)
## Установка
1) Создаём виртуальную среду python: ```python -m venv path/to/venv```
2) Запускаем виртуальную среду: ``` path/to/venv/Scripts/activate.bat``` для Windows, ```. path/to/venv/bin/activate``` для Linux
3) Устанавливаем зависимости из папки noise+whisper, файл requirements.txt
4) Запускаем сервер FastApi:``` uvicorn aprep_fast:app --reload --port 1234``` или ``` python -m uvicorn aprep_fast:app --reload --port 1234```
5) Сервер запущен
