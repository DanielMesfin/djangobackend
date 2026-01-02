from django.apps import AppConfig


class BrokerConfig(AppConfig):
    name = 'broker'
    def ready(self):
        # Import signals to register them
        import broker.signals
