from django.apps import AppConfig


class PaymentgatewayConfig(AppConfig):
    name = 'paymentgateway'

    def ready(self):
        import paymentgateway.signals
