import pika
from threading import Thread
from model_tracker.auth import authenticate_aqmp

class AsyncPubCon:

    def __init__(self, model_key, password, model_callback):
        self.__uri = authenticate_aqmp(model_key, password)
        self.__model_callback = model_callback
        self.__model_key  = model_key
        self.__publish_ch = None
        self.__consume_ch = None
        self.__consume_run()
        self.__publisher_init()

    def send(self, data):
        thr = Thread(target=self._send_on_thread, args=(data,))
        thr.start()
        thr.join()

    def _send_on_thread(self, data):
        self.__publish_ch.basic_publish(exchange="",
                                        routing_key="updates_"+self.__model_key,
                                        body=data)
        # print("[s] data:",data)


    def __publisher_init(self):
        params = pika.URLParameters(self.__uri)
        self.__publish_conn = pika.BlockingConnection(params)
        self.__publish_ch = self.__publish_conn.channel()
        self.__publish_ch.queue_declare(queue="updates_"+self.__model_key,
                                        arguments={'x-message-ttl' : 5000})
        print("Publisher Connection Established")

    def __callback(self, ch, method, properties, body):
        if body == b"stop":
            self.__model_callback.model.stop_training = True
            ch.stop_consuming()

        print("[r] recieved stop signal")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __setup_consumer_channel(self):
        params = pika.URLParameters(self.__uri)
        self.__consume_conn = pika.BlockingConnection(params)
        self.__consume_ch = self.__consume_conn.channel()

        # consuming channel
        self.__consume_ch.queue_declare(queue="signal_"+self.__model_key,
                              arguments={'x-message-ttl' : 5000})
        self.__consume_ch.basic_consume(queue="signal_"+self.__model_key,
                              on_message_callback=self.__callback)

        print("Consumer Connection Established")

    def __consume(self):
        try:
            self.__consume_ch.start_consuming()
        except KeyboardInterrupt:
            pass

    def __consume_run(self):
        self.__setup_consumer_channel()
        thr = Thread(target=self.__consume)
        thr.start()

    def close_connections(self):
        try:
            self.__consume_conn.close()
        except:
            pass
        print("Closed consumer connection")

        try:
            self.__publish_conn.close()
        except:
            pass
        print("Closed publisher connection")
