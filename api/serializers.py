from rest_framework import serializers

from contacts.models import Contact

from campaigns.models import Campaign


class ContactSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Contact

        fields = [
            'id',
            'name',
            'email',
            'is_subscribed'
        ]


class CampaignSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Campaign

        fields = [
            'id',
            'subject',
            'message',
            'status',
            'scheduled_time'
        ]