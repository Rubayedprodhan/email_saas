from celery import shared_task

import random
import time

from django.core.mail import (
    EmailMultiAlternatives
)

from django.core.mail.backends.smtp import (
    EmailBackend
)

from contacts.models import Contact

from accounts.models import SMTPSetting

from campaigns.models import (
    Campaign,
    EmailTrack,
    ClickTrack,
    ABTestResult
)

from .utils import render_email_template, personalize_content


@shared_task
def send_campaign_email(
    campaign_id,
    subject,
    message,
    email_list,
    domain
):

    # =========================
    # CAMPAIGN
    # =========================

    campaign = Campaign.objects.get(
        id=campaign_id
    )

    # =========================
    # SMTP SETTINGS
    # =========================

    smtp = SMTPSetting.objects.get(
        user=campaign.user
    )

    # =========================
    # SMTP BACKEND
    # =========================

    backend = EmailBackend(

        host=smtp.smtp_host,

        port=smtp.smtp_port,

        username=smtp.smtp_username,

        password=smtp.smtp_password,

        use_tls=smtp.use_tls
    )

    # =========================
    # BATCH SETTINGS
    # =========================

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

            try:

                # =========================
                # DEFAULT VARIANT
                # =========================

                variant = "A"

                current_subject = subject

                current_message = message

                # =========================
                # A/B TEST
                # =========================

                if campaign.is_ab_test:

                    variant = random.choice(
                        ["A", "B"]
                    )

                    if variant == "A":

                        current_subject = (
                            campaign.variant_a_subject
                        )

                        current_message = (
                            campaign.variant_a_message
                        )

                    else:

                        current_subject = (
                            campaign.variant_b_subject
                        )

                        current_message = (
                            campaign.variant_b_message
                        )

                # =========================
                # SAVE AB RESULT
                # =========================

                ABTestResult.objects.create(

                    campaign=campaign,

                    variant=variant,

                    email=email
                )

                # =========================
                # CONTACT
                # =========================

                contact = Contact.objects.get(

                    email=email,

                    user_id=campaign.user.id
                )

                # =========================
                # PERSONALIZATION
                # =========================

                personalized_message = (
                    personalize_content(
                        current_message,
                        contact
                    )
                )
                

                # =========================
                # EMAIL TRACK
                # =========================

                track = EmailTrack.objects.create(

                    campaign_id=campaign_id,

                    email=email,

                    status='sent'
                )

                # =========================
                # OPEN TRACKING
                # =========================

                tracking_url = (

                    f"{domain}/campaigns/track/"
                    f"{track.id}/"
                )

                # =========================
                # CLICK TRACKING
                # =========================

                original_url = (
                    "https://google.com"
                )

                click = ClickTrack.objects.create(

                    campaign_id=campaign_id,

                    email=email,

                    original_url=original_url
                )

                click_url = (

                    f"{domain}/campaigns/click/"
                    f"{click.id}/"
                )

                # =========================
                # UNSUBSCRIBE
                # =========================

                unsubscribe_url = (

                    f"{domain}/contacts/unsubscribe/"
                    f"{contact.id}/"
                )

                # =========================
                # TEMPLATE HTML
                # =========================

                if campaign.template:

                    html_content = render_email_template(
                        campaign.template
                    )

                    html_content = (
                        html_content.replace(
                            "{{message}}",
                            current_message
                        )
                    )

                else:

                    html_content = f"""

                    <h2>
                        {current_subject}
                    </h2>

                    <p>
                        {current_message}
                    </p>

                    """

                # =========================
                # FOOTER
                # =========================

                html_content += f"""

                <br>
                <br>

                <p>

                    <a href="{click_url}">

                        Visit Offer

                    </a>

                </p>

                <br>

                <p>

                    <a href="{unsubscribe_url}">

                        Unsubscribe

                    </a>

                </p>

                <img src="{tracking_url}"
                     width="1"
                     height="1">

                """

                # =========================
                # EMAIL OBJECT
                # =========================

                msg = EmailMultiAlternatives(

                    current_subject,

                    current_message,

                    smtp.from_email,

                    [email],

                    connection=backend
                )

                # =========================
                # ATTACH HTML
                # =========================

                msg.attach_alternative(

                    html_content,

                    "text/html"
                )

                # =========================
                # SEND EMAIL
                # =========================

                msg.send()

                print(
                    f"Sent to {email}"
                )

            except Exception as e:

                EmailTrack.objects.create(

                    campaign_id=campaign_id,

                    email=email,

                    status='failed',

                    error_message=str(e)
                )

                print(
                    f"Failed for {email}"
                )

                print(str(e))

        # =========================
        # RATE LIMIT
        # =========================

        time.sleep(5)

    return "Emails Sent"




def check_spam_score(content):

    prompt = f"""
    Analyze this email content.

    Give:
    1. Spam score from 1-10
    2. Spam issues
    3. Suggestions to improve deliverability

    Email:
    {content}
    """

    response = model.generate_content(
        prompt
    )

    return response.text