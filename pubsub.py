
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

class AsyncConn:
    def __init__(self, id: str, channel_name: str) -> None:
        config = PNConfiguration()
        config.subscribe_key = 'sub-c-22cdf9b7-ca1d-4af3-9fb4-8a34a0106007'
        config.publish_key = 'pub-c-e13d78f9-6c34-4087-a7a2-d95ae19936db'
        config.user_id = id
        config.enable_subscribe = True
        config.daemon = True

        self.pubnub = PubNub(config)
        self.channel_name = channel_name

        print(f"Configurando conexão com o canal '{self.channel_name}'...")
        subscription = self.pubnub.channel(self.channel_name).subscription()
        subscription.subscribe()

    def publish(self, data: dict):
        print("tentando enviar uma mensagem")
        self.pubnub.publish().channel(self.channel_name).message(data).sync()

