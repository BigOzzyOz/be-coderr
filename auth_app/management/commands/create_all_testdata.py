from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Erstellt alle Testdaten für User/Profiles, Offers, OfferDetails, Orders und Reviews."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Erstelle Testdaten für Offers und OfferDetails..."))
        call_command("create_test_offers")
        self.stdout.write(self.style.SUCCESS("Offers und OfferDetails erstellt."))

        self.stdout.write(self.style.NOTICE("Erstelle Testdaten für Orders..."))
        call_command("create_test_orders")
        self.stdout.write(self.style.SUCCESS("Orders erstellt."))

        self.stdout.write(self.style.NOTICE("Erstelle Testdaten für Reviews..."))
        call_command("create_test_reviews")
        self.stdout.write(self.style.SUCCESS("Reviews erstellt."))

        self.stdout.write(self.style.SUCCESS("Alle Testdaten wurden erfolgreich erstellt!"))
