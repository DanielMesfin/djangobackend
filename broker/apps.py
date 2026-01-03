from django.apps import AppConfig
from django.conf import settings


class BrokerConfig(AppConfig):
    name = 'broker'
    def ready(self):
        # Import signals to register them
        import broker.signals
        # Tweak Jazzmin sidebar at runtime to organize Business models and collapse menu
        jazzmin = getattr(settings, 'JAZZMIN_SETTINGS', None)
        if isinstance(jazzmin, dict):
            # Collapse sidebar by default
            jazzmin['navigation_expanded'] = False
            # Group Business models together in the Broker app and set overall order
            jazzmin['order_with_respect_to'] = [
                'broker.BusinessProfile',
                'broker.BusinessDocument',
                'broker.BusinessMember',
                'broker',
                'product',
                'auth',
            ]
            # Remove broken custom links (e.g., make_messages) to avoid reverse errors
            jazzmin['custom_links'] = {}
            # Hide Conversation model from the sidebar while keeping Message visible
            hide_models = jazzmin.get('hide_models') or []
            if 'broker.Conversation' not in hide_models:
                hide_models.append('broker.Conversation')
            jazzmin['hide_models'] = hide_models
