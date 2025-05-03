import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail


class Command(BaseCommand):
    help = "Erstellt 10 Test-Offers mit jeweils 3 abwechslungsreichen OfferDetails und mehreren Usern."

    def handle(self, *args, **options):
        now = timezone.now()
        users = []
        for u in range(1, 5):
            user, _ = User.objects.get_or_create(
                username=f"testuser{u}",
                defaults={"email": f"testuser{u}@mail.de"}
            )
            users.append(user)
        for i in range(1, 11):
            user = random.choice(users)
            created = now - timedelta(days=i)
            updated = created + timedelta(hours=random.randint(0, 48))
            offer = Offer.objects.create(
                user=user,
                title=f"Test Offer {i}",
                description=f"Beschreibung für Test Offer {i}",
                created_at=created,
                updated_at=updated,
            )
            for j in range(1, 4):
                OfferDetail.objects.create(
                    offer=offer,
                    title=f"Detail {j} für Offer {i}",
                    revisions=random.randint(1, 10),
                    delivery_time_in_days=random.randint(1, 21),
                    price=random.randint(50, 1000) + i * 7 + j * 3,
                    features=[f"Feature {k}" for k in range(1, random.randint(2, 5))],
                    offer_type=["basic", "standard", "premium"][j - 1],
                )
        self.stdout.write(self.style.SUCCESS("10 Offers mit je 3 abwechslungsreichen OfferDetails und mehreren Usern erstellt."))
