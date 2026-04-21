from django.core.cache import cache

from config.settings import CACHE_ENABLED
from mailing.models import Campaign, Message, Subscriber


def get_all_recipients():
    if CACHE_ENABLED:
        recipients = cache.get("recipients")
        if recipients is None:
            recipients = Subscriber.objects.all()
            cache.set("recipients", recipients, 120)
        else:
            recipients = Subscriber.objects.all()

        return recipients


def get_all_messages():
    if CACHE_ENABLED:
        messages = cache.get("messages")
        if messages is None:
            messages = Message.objects.all()
            cache.set("messages", messages, 120)
        else:
            messages = Message.objects.all()

        return messages


def get_all_mailing():
    if CACHE_ENABLED:
        mailing = cache.get("mailing")
        if mailing is None:
            mailing = Campaign.objects.all()
            cache.set("mailing", mailing, 120)
        else:
            mailing = Campaign.objects.all()

        return mailing
