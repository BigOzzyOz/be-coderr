import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reviews_app.models import Review
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Erstellt Test-Reviews für bestehende Benutzer."

    def handle(self, *args, **options):
        num_reviews_to_create = 20  # Wie viele Reviews sollen erstellt werden?

        # 1. Benutzer holen oder erstellen (Beispiel: 5 Business-User, 10 Reviewer)
        business_users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f"business_user_{i}", defaults={"email": f"business{i}@example.com", "password": "password123"}
            )
            if created:
                user.set_password("password123")  # Passwort setzen, wenn neu erstellt
                user.save()
            business_users.append(user)
            if created:
                self.stdout.write(f"Business User '{user.username}' erstellt.")

        reviewers = []
        for i in range(1, 11):
            user, created = User.objects.get_or_create(
                username=f"reviewer_{i}", defaults={"email": f"reviewer{i}@example.com", "password": "password123"}
            )
            if created:
                user.set_password("password123")  # Passwort setzen, wenn neu erstellt
                user.save()
            reviewers.append(user)
            if created:
                self.stdout.write(f"Reviewer '{user.username}' erstellt.")

        # 2. Reviews erstellen
        created_count = 0
        skipped_count = 0
        attempt_count = 0
        max_attempts = num_reviews_to_create * 3  # Verhindert Endlosschleife, falls alle Kombinationen belegt sind

        review_descriptions = [
            "Absolutely fantastic service!",
            "Good value for money.",
            "Could be better, had some issues.",
            "Very professional and efficient.",
            "Not what I expected.",
            "Highly recommended!",
            "Average experience.",
            "Delivery was quick.",
            "Customer support was helpful.",
            "Will use again.",
        ]

        while created_count < num_reviews_to_create and attempt_count < max_attempts:
            attempt_count += 1
            business_user = random.choice(business_users)
            reviewer = random.choice(reviewers)

            # Sicherstellen, dass ein Benutzer sich nicht selbst bewertet
            if business_user == reviewer:
                continue

            rating = random.randint(1, 5)
            description = random.choice(review_descriptions)

            try:
                review, created = Review.objects.get_or_create(
                    business_user=business_user,
                    reviewer=reviewer,
                    defaults={"rating": rating, "description": description},
                )
                if created:
                    created_count += 1
                    self.stdout.write(
                        f"Review von '{reviewer.username}' für '{business_user.username}' erstellt (Rating: {rating})."
                    )
                else:
                    skipped_count += 1
                    # Optional: Nachricht ausgeben, wenn übersprungen wird
                    # self.stdout.write(f"Review von '{reviewer.username}' für '{business_user.username}' existiert bereits.")
                    pass

            except IntegrityError:
                # Sollte durch get_or_create abgedeckt sein, aber zur Sicherheit
                self.stdout.write(
                    self.style.WARNING(
                        f"IntegrityError beim Versuch, Review von '{reviewer.username}' für '{business_user.username}' zu erstellen."
                    )
                )
                skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unerwarteter Fehler: {e}"))
                skipped_count += 1

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"{created_count} Test-Reviews erfolgreich erstellt."))
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"{skipped_count} Reviews wurden übersprungen (existierten bereits oder Fehler).")
            )
        if attempt_count >= max_attempts and created_count < num_reviews_to_create:
            self.stdout.write(
                self.style.ERROR(
                    "Maximale Anzahl an Versuchen erreicht. Konnten nicht alle gewünschten Reviews erstellen."
                )
            )
