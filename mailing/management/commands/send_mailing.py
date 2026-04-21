from django.core.mail import send_mail
from django.core.management import BaseCommand

from config.settings import EMAIL_HOST_USER
from mailing.models import Campaign, DeliveryAttempt


class Command(BaseCommand):
    def handle(self):

        def send_mailing():
            mailings = Campaign.objects.filter(status__in=("created", "launched"))
            for mailing in mailings:

                if mailing.enabled is True:

                    recipients = mailing.recipients.all()

                    for recipient in recipients:
                        try:
                            send_mail(
                                mailing.message.subject, mailing.message.body, EMAIL_HOST_USER, [recipient.email]
                            )

                            DeliveryAttempt.objects.create(
                                mailing=mailing, status="success", response="Сообщение отправлено успешно"
                            )

                        except Exception as e:
                            DeliveryAttempt.objects.create(mailing=mailing, status="not_success", response=str(e))

                    mailing.status = "launched"
                    mailing.save()

        send_mailing()
