from django.core.management import BaseCommand

from mailing.services import run_mail


class Command(BaseCommand):
    help = "Initiates a specific mailing by its primary key"

    def add_arguments(self, parser):
        parser.add_argument("campaign_pk", type=int, help="Primary Key of the Mailing to be initiated")

    def handle(self, *args, **options):
        campaign_pk = options["campaign_pk"]
        run_mail(campaign_pk)
        self.stdout.write(self.style.SUCCESS(f"Mailing with PK={campaign_pk} initiated."))
