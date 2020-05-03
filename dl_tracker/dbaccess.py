from dl_tracker.auth import authenticate_database
import requests

class DBAccessHandle:

    def __init__(self, model_key, password):
        self.__username = authenticate_database(model_key, password)
        self.__model_key = model_key
        with open("dl_tracker/webhook-url", "r") as fh:
            self.__url = fh.read().strip() 

    @staticmethod
    def serialized(JSON):
        JSON = JSON.copy()
        for k in JSON:
            JSON[k] = str(JSON[k])
        return JSON

    def start_training(self, JSON):
        resp = requests.post(self.__url+"start_training", json={
            "model_key" : self.__model_key,
            "username" : self.__username,
            "JSON" : self.serialized(JSON)
        })

        new_training_id = resp.json().get("new_training_id")
        return new_training_id

    def end_training(self, training_id):
        resp = requests.post(self.__url+"end_training", json={
            "model_key" : self.__model_key,
            "username" : self.__username,
            "training_id" : training_id
        })

    def epoch_begin(self, JSON):
        resp = requests.post(self.__url+"epoch_begin", json={
            "model_key" : self.__model_key,
            "username" : self.__username,
            "JSON" : self.serialized(JSON)
        })

    def epoch_end(self, JSON):
        resp = requests.post(self.__url+"epoch_end", json={
            "model_key" : self.__model_key,
            "username" : self.__username,
            "JSON" : self.serialized(JSON)
        })
