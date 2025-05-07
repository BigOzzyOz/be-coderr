import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review
from profiles_app.models import Profile
from django.db import transaction
from django.utils import timezone

KUNDEN_DATEN = [
    ("Anna", "Müller"),
    ("Max", "Mustermann"),
    ("Lena", "Schmidt"),
    ("Paul", "Schneider"),
    ("Laura", "Fischer"),
    ("Tim", "Weber"),
    ("Julia", "Meyer"),
    ("Felix", "Wagner"),
    ("Sophie", "Becker"),
    ("Jonas", "Hoffmann"),
    ("Marie", "Schäfer"),
    ("Lukas", "Koch"),
    ("Lea", "Richter"),
    ("Finn", "Klein"),
    ("Mia", "Wolf"),
    ("Ben", "Neumann"),
    ("Emilia", "Schröder"),
    ("Noah", "Schwarz"),
    ("Emma", "Zimmermann"),
    ("Elias", "Braun"),
]
BUSINESS_DATEN = [
    ("Webagentur", "Berlin"),
    ("DesignStudio", "Hamburg"),
    ("ITService", "München"),
    ("Texterei", "Köln"),
    ("FotoProfi", "Frankfurt"),
    ("AppSchmiede", "Stuttgart"),
    ("SEOExpert", "Düsseldorf"),
    ("ShopBuilder", "Leipzig"),
    ("MediaHouse", "Bremen"),
    ("DatenAnalytik", "Dresden"),
]


class Command(BaseCommand):
    help = "Erstellt vollständige Testdaten: 30 User (20 Kunden, 10 Businesses), je Business ein Offer mit 3 OfferDetails, Orders und Reviews."

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. User und Profile anlegen
            kunden = []
            businesses = []
            for vorname, nachname in KUNDEN_DATEN:
                username = f"{vorname.lower()}.{nachname.lower()}"
                email = f"{vorname.lower()}.{nachname.lower()}@beispiel.de"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"email": email, "first_name": vorname, "last_name": nachname, "password": "pass1234"},
                )
                if created:
                    user.set_password("pass1234")
                    user.save()
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.type = "customer"
                profile.save()
                kunden.append(user)
            for firmenname, stadt in BUSINESS_DATEN:
                username = f"{firmenname.lower()}_{stadt.lower()}"
                email = f"{firmenname.lower()}@{stadt.lower()}.de"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"email": email, "first_name": firmenname, "last_name": stadt, "password": "pass1234"},
                )
                if created:
                    user.set_password("pass1234")
                    user.save()
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.type = "business"
                profile.save()
                businesses.append(user)
            self.stdout.write(self.style.SUCCESS(f"{len(kunden)} Kunden und {len(businesses)} Businesses angelegt."))

            # 2. Für jeden Business ein Offer mit 3 OfferDetails
            offerdetails_typen = ["basic", "standard", "premium"]
            offers = []
            offerdetails = []
            for idx, business in enumerate(businesses, 1):
                offer = Offer.objects.create(
                    user=business,
                    title=f"Professioneller Service {idx}",
                    description=f"Top Dienstleistung von {business.username}",
                )
                offers.append(offer)
                for j, typ in enumerate(offerdetails_typen, 1):
                    od = OfferDetail.objects.create(
                        offer=offer,
                        title=f"{typ.capitalize()} Paket",
                        revisions=random.randint(1, 5),
                        delivery_time_in_days=random.randint(2, 14),
                        price=round(random.uniform(49, 499), 2),
                        features=[f"Feature {k}" for k in range(1, random.randint(2, 5))],
                        offer_type=typ,
                    )
                    offerdetails.append(od)
            self.stdout.write(self.style.SUCCESS(f"{len(offers)} Offers mit je 3 OfferDetails erstellt."))

            # 3. Orders von Kunden an Businesses
            orders = []
            for i in range(1, 41):
                customer = random.choice(kunden)
                offer_detail = random.choice(offerdetails)
                business = offer_detail.offer.user
                if customer == business:
                    continue  # Kein Auftrag an sich selbst
                status = random.choices(["in_progress", "completed", "cancelled"], weights=[0.5, 0.4, 0.1])[0]
                order = Order.objects.create(
                    customer_user=customer,
                    business_user=business,
                    title=offer_detail.title,
                    revisions=offer_detail.revisions,
                    delivery_time_in_days=offer_detail.delivery_time_in_days,
                    price=offer_detail.price,
                    features=offer_detail.features,
                    offer_type=offer_detail.offer_type,
                    status=status,
                )
                orders.append(order)
            self.stdout.write(self.style.SUCCESS(f"{len(orders)} Orders erstellt."))

            # 4. Reviews für abgeschlossene Orders
            reviews = 0
            beschreibungen = [
                "Sehr zufrieden!",
                "Schnelle Lieferung.",
                "Top Qualität.",
                "Gerne wieder!",
                "Empfehlenswert.",
                "Kommunikation könnte besser sein.",
                "Alles wie besprochen.",
                "Preis-Leistung stimmt.",
                "Super Service.",
                "Nicht ganz zufrieden.",
            ]
            for order in orders:
                if order.status == "completed":
                    if not Review.objects.filter(
                        business_user=order.business_user, reviewer=order.customer_user
                    ).exists():
                        Review.objects.create(
                            business_user=order.business_user,
                            reviewer=order.customer_user,
                            rating=random.randint(3, 5),
                            description=random.choice(beschreibungen),
                        )
                        reviews += 1
            self.stdout.write(self.style.SUCCESS(f"{reviews} Reviews für abgeschlossene Orders erstellt."))

        self.stdout.write(self.style.SUCCESS("Alle Testdaten wurden erfolgreich erstellt!"))
