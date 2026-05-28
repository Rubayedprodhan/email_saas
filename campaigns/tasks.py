from celery import shared_task

from django.core.mail import (
    EmailMultiAlternatives
)

from contacts.models import Contact

from campaigns.models import (
    Campaign,
    EmailTrack,
    ClickTrack
)

import time


@shared_task
def send_campaign_email(
    campaign_id,
    subject,
    message,
    email_list,
    domain
):

    campaign = Campaign.objects.get(
        id=campaign_id
    )

    batch_size = 10

    for i in range(
        0,
        len(email_list),
        batch_size
    ):

        batch = email_list[
            i:i + batch_size
        ]

        for email in batch:

            contact = Contact.objects.get(
                email=email,
                user_id=campaign.user.id
            )

            track = EmailTrack.objects.create(
                campaign_id=campaign_id,
                email=email,
                status='sent'
            )

            tracking_url = (
                f"{domain}/campaigns/track/"
                f"{track.id}/"
            )

            original_url = "https://google.com"

            click = ClickTrack.objects.create(
                campaign_id=campaign_id,
                email=email,
                original_url=original_url
            )

            click_url = (
                f"{domain}/campaigns/click/"
                f"{click.id}/"
            )

            unsubscribe_url = (
                f"{domain}/contacts/unsubscribe/"
                f"{contact.id}/"
            )

            if campaign.template:

                html_content = (
                    campaign.template.html_content
                )

                html_content = html_content.replace(
                    "{{message}}",
                    message
                )

            else:

                html_content = f"""
                <h2>{subject}</h2>

                <p>{message}</p>
                """

            html_content += f"""

            <p>
                <a href="{click_url}">
                    Visit Offer
                </a>
            </p>

            <br>

        