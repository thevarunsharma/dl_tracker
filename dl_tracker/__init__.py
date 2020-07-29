from tensorflow import keras
import json
from dl_tracker.amqp_handler import AsyncPubCon
from dl_tracker.dbaccess import DBAccessHandle

class Tracker(keras.callbacks.Callback):

    def __init__(self, model_key, password):
        self.__model_key = model_key
        self.__password = password
        self.__update_handler = None
        self.__dbhandle = DBAccessHandle(model_key, password)
        self.__training_id = None
        self.__curr_epoch = 0
        self.__curr_batch = 0

    @staticmethod
    def serialized(dictionary):
        return json.dumps({key:str(value) for key, value in dictionary.items()},
                          indent="   ")

    def on_train_begin(self, logs=None):
        if logs is None:
            logs = {}
        self.__update_handler = AsyncPubCon(self.__model_key, self.__password, self)
        # print("[s] sending START TRAINING update to DB:\n",
        #       Tracker.serialized(self.params))
        self.__training_id = self.__dbhandle.start_training(self.params)
        logs = self.params.copy()
        logs['type'] = 'train_begin'
        logs['training_id'] = self.__training_id
        self.__update_handler.send(Tracker.serialized(logs))

    def on_train_end(self, logs=None):
        if logs is None:
            logs = {}
        # print("[s] sending END TRAINING update to DB")
        if self.__training_id is None:
            raise ValueError("Invalid training ID")
        self.__dbhandle.end_training(self.__training_id)
        self.__update_handler.send(Tracker.serialized({"training_id" : self.__training_id,
                                                       "type" : "train_end"}))
        self.__update_handler.close_connections()

    def on_epoch_begin(self, epoch, logs=None):
        if logs is None:
            logs = {}
        logs = logs.copy()
        logs['training_id'] = self.__training_id
        logs['type'] = 'epoch_begin'
        self.__curr_epoch = logs['epoch'] = epoch
        logs['progress'] = self.__curr_batch + 1
        # print("[s] sending START EPOCH update to DB:\n",
        #       Tracker.serialized(logs))
        self.__update_handler.send(Tracker.serialized(logs))
        self.__dbhandle.epoch_begin(logs)

    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        logs = logs.copy()
        logs['training_id'] = self.__training_id
        logs['type'] = 'epoch_end'
        self.__curr_epoch = logs['epoch'] = epoch
        logs['progress'] = self.__curr_batch + 1
        # print("[s] sending END EPOCH update to DB:\n",
        #       Tracker.serialized(logs))
        self.__update_handler.send(Tracker.serialized(logs))
        self.__dbhandle.epoch_end(logs)

    def on_train_batch_end(self, batch, logs=None):
        if logs is None:
            logs = {}
        logs = logs.copy()
        logs['training_id'] = self.__training_id
        logs['batch'] = batch
        logs['epoch'] = self.__curr_epoch
        logs['type'] = 'batch'
        logs['progress'] = self.__curr_batch + 1
        self.__curr_batch = batch
        self.__update_handler.send(Tracker.serialized(logs))
