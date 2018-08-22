class LoggerModule:
    async def on_message_proxied(self, message, member):
        print("Got message: {} {}".format(message, member))

    async def on_proxy_message_deleted(self, message):
        print("Deleted message: {}".format(message))