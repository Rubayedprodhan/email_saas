import google.generativeai as genai

from django.conf import settings

genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

def generate_email_content(prompt):

    full_prompt = f"""
    You are an expert email marketer.

    Write:
    - Catchy subject line
    - Professional email body
    - CTA button text

    Tone:
    Professional and persuasive.

    Prompt:
    {prompt}
    """

    response = model.generate_content(
        full_prompt
    )

    return response.text


def optimize_subject_line(subject):

    prompt = f"""
    Improve this email subject line
    for higher open rate.

    Subject:
    {subject}

    Rules:
    - Keep under 60 characters
    - Make it catchy
    - Avoid spammy wording
    """

    response = model.generate_content(
        prompt
    )

    return response.text