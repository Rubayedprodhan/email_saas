from rest_framework import generics

from rest_framework.permissions import (
    IsAuthenticated
)

from contacts.models import Contact

from campaigns.models import Campaign

from .serializers import (
    ContactSerializer,
    CampaignSerializer
)


class ContactListAPI(
    generics.ListCreateAPIView
):

    serializer_class = ContactSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return Contact.objects.filter(
            user=self.request.user
        )

    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            user=self.request.user
        )


class CampaignListAPI(
    generics.ListAPIView
):

    serializer_class = CampaignSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return Campaign.objects.filter(
            user=self.request.user
        )