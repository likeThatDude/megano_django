# Megano Django Website

## Описание проекта

Вебсайт для интернет-магазина ___Megano___. Занимается продажей электроники, бытовой техники и электротоваров.

## Технологии:
- __`Django`__
- __`Django Rest Framework`__

## Руководитель (тимлид):
- __`Сергей`__

## Разработчики:
- __`Иван`__
- __`Бекхан`__
- __`Сергей`__
- __`Владимир`__
- __`Георгий`__

## Требования:
Перед запуском django-проекта необходимо установить интерпретатор _`Python 3.12, PostgreSQL`_

## Запуск проекта:
1. Клонируем репозиторий `https://gitlab.skillbox.ru/pythondjango_team43/djangowebsite` и переходим в папку проекта:
```bash
cd website
```

2. Создать и активировать виртуальное окружение:
- Windows
```bash
python -m venv venv
venv\Scripts\activate
```
- macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

4. Создайте файл с переменными окружения:
```bash
touch .env
```

5. Заполните переменные окружения:
SMTP-сервер почтового клиента `EMAIL_HOST = 'smtp.yandex.com'` - __`Yandex`__. Если вы хотите использовать другой почтовый клиент, например `gmail`, исправьте на `EMAIL_HOST = 'smtp.gmail.com'`

```bash
EMAIL_USER='адрес электронной почты'
EMAIL_PASSWORD='пароль от почты'
```
