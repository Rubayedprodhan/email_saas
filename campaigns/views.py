from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    ListView,
    CreateView
)

from django.core.mail import send_mail

from contacts.models import Contact

from .models import Campaign
from .forms import CampaignForm


class CampaignListView(
    LoginRequiredMixin,
    ListView
):
    model = Campaign
    template_name = 'campaigns/list.html'

    def get_queryset(self):
        return Campaign.objects.filter(
            user=self.request.user
        )


class CampaignCreateView(
    LoginRequiredMixin,
    CreateView
):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/create.html'
    success_url = reverse_lazy('campaign_list')

    def form_valid(self, form):

        campaign = form.save(commit=False)

        campaign.user = self.request.user

        campaign.save()

        contacts = Contact.objects.filter(
            user=self.request.user
        )

        email_list = [
            contact.email
            for contact in contacts
        ]

        send_mail(
            campaign.subject,
            campaign.message,
            None,
            email_list,
            fail_silently=False,
        )

        campaign.status = 'sent'

        campaign.save()

        return redirect('campaign_list')