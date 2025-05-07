import random
from django.core.management.base import BaseCommand
from offers_app.models import OfferDetail
from orders_app.models import Order
from profiles_app.models import Profile
from django.db import transaction

GERMAN_TITLES = [
    "Webseite Entwicklung",
    "Logo Design",
    "SEO Optimierung",
    "Texterstellung",
    "Social Media Betreuung",
    "Online Shop Aufbau",
    "Fotobearbeitung",
    "Video Produktion",
    "App Entwicklung",
    "Datenanalyse",
]

GERMAN_FEATURES = [
    ["Responsive Design", "SEO-freundlich", "Kontaktformular"],
    ["3 Entwürfe", "Vektordatei", "Farbvarianten"],
    ["Keyword-Analyse", "OnPage-Optimierung", "Backlink-Check"],
    ["500 Wörter", "Korrektorat inklusive", "SEO-optimiert"],
    ["Monatliche Auswertung", "Content-Planung", "Community Management"],
    ["Produktimport", "Zahlungsintegration", "Mobile Ready"],
    ["RAW-Entwicklung", "Retusche", "Farbkorrektur"],
    ["Full-HD", "Schnitt", "Musikunterlegung"],
    ["iOS & Android", "Push-Benachrichtigungen", "App Store Upload"],
    ["Datenvisualisierung", "Berichtserstellung", "Dashboards"],
]

ORDER_TYPES = ["basic", "standard", "premium"]


class Command(BaseCommand):
    help = "Erstellt realistische Test-Orders mit deutschen Daten."

    def handle(self, *args, **options):
        kunden = list(Profile.objects.filter(type="kunde").values_list("user", flat=True))
        businesses = list(Profile.objects.filter(type="business").values_list("user", flat=True))
        offer_details = list(OfferDetail.objects.all())

        if not kunden or not businesses or not offer_details:
            self.stdout.write(
                self.style.ERROR("Es müssen mindestens je ein Kunde, ein Business und ein OfferDetail existieren!")
            )
            return

        num_orders = min(20, len(kunden) * len(businesses), len(offer_details))
        created = 0
        with transaction.atomic():
            for i in range(num_orders):
                customer_id = random.choice(kunden)
                business_id = random.choice(businesses)
                if customer_id == business_id:
                    continue  # Kunde und Business sollen nicht identisch sein
                offer_detail = random.choice(offer_details)
                idx = random.randint(0, len(GERMAN_TITLES) - 1)
                order = Order.objects.create(
                    customer_user_id=customer_id,
                    business_user_id=business_id,
                    title=GERMAN_TITLES[idx],
                    revisions=offer_detail.revisions,
                    delivery_time_in_days=offer_detail.delivery_time_in_days,
                    price=offer_detail.price,
                    features=GERMAN_FEATURES[idx],
                    offer_type=offer_detail.offer_type,
                    status=random.choice(["in_progress", "completed", "cancelled"]),
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} Test-Orders wurden erfolgreich erstellt."))
