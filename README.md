# Disto

> Similar to Facebook or Twitter, everyone who creates a Disto account has a profile and a news feed. When you post a photo or video on Disto, it displays on your profile. Other users who follow you see your posts in their feed. Likewise, you see posts from other users you follow.Like other social networks, you interact with other users on Disto by following them, being followed by them, commenting, liking, tagging etc.

## Setup project locally

[![Python Version](https://img.shields.io/badge/python-3.7-yellow.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-3.1-brightgreen.svg)](https://djangoproject.com)
[![MongoDB Version](https://img.shields.io/badge/mongodb-4.4-orange.svg)](https://docs.mongodb.com)
[![RabbitMQ Version](https://img.shields.io/badge/rabbitMq-3.8-red.svg)](https://www.rabbitmq.com)



First, clone the repository to your local machine:

```
git clone https://github.com/Negar-R/Rubino.git
cd Rubino
```

To activate virtual environments and install dependencies in, run the below commands:

```
virtualenv -p python3 env
source env/bin/activate
pip install -r requirments.txt
```

As databse in this project is `MongoDB` it is not required to migrate, instead you shod pass the host, user and password of your databse in mongo to connect to it.
At last, to run the project:

```
python manage.py runserver
```
The project will be available at **127.0.0.1:8000**

## Request's Introduction

To request to the site, you can use the `Postman Collection` that provided in the project's files, too. First, you should export this collection to your postman, and afterward, the only thing that you should do is change the JSON field's value to whatever you want.

