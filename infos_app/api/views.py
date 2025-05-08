from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db.models import Avg
from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        review_count = Review.objects.all().count()
        average_rating = round(Review.objects.aggregate(Avg("rating"))["rating__avg"] or 0, 1)
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.all().count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)
