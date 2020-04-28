# DL-Tracker Python Callback Package
A python package for real time tracking of keras model training.

### Requirements:
- Tensorflow or Keras
- pika (RabbitMQ Python client)
- requests (Request HTTP Python library)

Meant to be used in combination with an __Android Client__: https://github.com/thevarunsharma/DL-Tracker-App

_Note_: Some additional prior setup is needed to be done before using this package which includes setting up a webhook for database updation and an AMQP cloud server.

### Instructions for use
- First, make sure that the above requirements are satisfied. 
- Then, add this package in your current working directory
```
"""
model: 
  A tensorflow or keras model instance created using keras.models.Model or keras.models.Sequential
modelKey:
  unique key identifying the model, to be obtained from the App
password:
  user profile password
"""

# import Tracker callback
from dl_tracker import Tracker

# create a Tracker instance, pass modelKey and password as arguments
tracker = Tracker(modelKey, password)

# pass tracker among callbacks while calling .fit ot .fit_generator method on model
model.fit(..., callbacks=[tracker, ...])

# or
model.fit_generator(..., callbacks=[tracker, ...])
```
