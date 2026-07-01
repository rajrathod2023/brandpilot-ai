from typing import Dict, List
import json
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_text(value: str) -> str:
    return " ".join(value.split()).strip()


def build_image_brief(
    website_data: Dict,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str
) -> Dict:
    brand_name = clean_text(website_data.get("title") or "the brand")
    description = clean_text(website_data.get("description") or "")
    audience = clean_text(target_audience or "professional audience")
    cta = clean_text(cta_text or "")
    link = clean_text(cta_link or "")
    offer = clean_text(offer_promotion or "")

    system_prompt = """
You are an expert creative director for premium social media campaigns.

Create an image brief for one AI-generated campaign photo.

Important rules:
- Return JSON only.
- PHOTO ONLY.
- The image must look like a real photograph, not a poster.
- Do not create poster design.
- Do not create a marketing banner inside the image.
- Do not include text, words, typography, headlines, letters, numbers, captions, signs, logos, labels, or watermarks.
- Do not hardcode any industry.
- Use the website context, campaign topic, audience, CTA, and offer to decide the scene.
- The campaign topic must lead the creative direction.
- The image must be relevant to the business and the campaign topic.
- The image should visually support the CTA or offer when provided, without placing text in the image.
- Do not generate culturally specific imagery unless explicitly requested.
- Avoid Māori-specific imagery unless the user explicitly asks for Māori culture, Māori people, te ao Māori, tikanga, or similar.
- Avoid generic office scenes unless the business/topic clearly needs it.
- Avoid generic stock-photo poses.
- Avoid people standing with arms crossed.
- Show authentic activity, interaction, or storytelling.

Return this JSON shape:
{
  "scene": "specific scene description",
  "people": "who should be shown",
  "activity": "what people are doing",
  "environment": "where it happens",
  "emotion": "emotional tone",
  "style": "photography style"
}
"""

    user_prompt = f"""
Brand/business:
{brand_name}

Website context:
{description}

Campaign topic:
{topic}

Target audience:
{audience}

CTA text:
{cta}

CTA link:
{link}

Offer / promotion:
{offer}

Create a specific image brief that fits this exact campaign.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content or "{}"
        brief = json.loads(content)

        if not isinstance(brief, dict):
            raise ValueError("Image brief response was not a dictionary")

        return brief

    except Exception as error:
        print("IMAGE BRIEF ERROR:", error)

        return {
            "scene": "authentic campaign moment connected to the business and topic",
            "people": "relevant real people from the target audience",
            "activity": "people actively engaging with the service, experience, or topic",
            "environment": "a realistic environment connected to the business",
            "emotion": "trust, confidence, connection, and purpose",
            "style": "realistic premium editorial photography"
        }


def build_openai_image_prompt(
    website_data: Dict,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str
) -> str:
    brand_name = clean_text(website_data.get("title") or "the brand")
    description = clean_text(website_data.get("description") or "")
    audience = clean_text(target_audience or "professional audience")
    cta = clean_text(cta_text or "")
    link = clean_text(cta_link or "")
    offer = clean_text(offer_promotion or "")

    brief = build_image_brief(
        website_data=website_data,
        topic=topic,
        target_audience=target_audience,
        cta_text=cta_text,
        cta_link=cta_link,
        offer_promotion=offer_promotion
    )

    scene = clean_text(str(brief.get("scene", "")))
    people = clean_text(str(brief.get("people", "")))
    activity = clean_text(str(brief.get("activity", "")))
    environment = clean_text(str(brief.get("environment", "")))
    emotion = clean_text(str(brief.get("emotion", "")))
    style = clean_text(str(brief.get("style", "realistic premium editorial photography")))

    prompt = f"""
Create one high-quality realistic PHOTO ONLY for a social media campaign.

This must be a real photographic image only.
Do not create a poster.
Do not create a marketing banner.
Do not create a graphic design layout.
Do not create any text inside the image.

Brand/business:
{brand_name}

Website/business context:
{description}

Campaign topic:
{topic}

Target audience:
{audience}

CTA text:
{cta}

CTA link:
{link}

Offer / promotion:
{offer}

Creative brief:
Scene: {scene}
People: {people}
Activity: {activity}
Environment: {environment}
Emotion: {emotion}
Photography style: {style}

Style direction:
- PHOTO ONLY
- Realistic premium editorial photography
- Real people in a professional workshop or learning environment
- Business capability building
- Authentic human interaction
- Aotearoa New Zealand context when relevant
- Warm natural light
- Clean premium composition
- Candid storytelling moment
- Professional but authentic
- Do not show screens
- Do not show presentation slides
- Do not show whiteboards
- Do not show posters
- Do not show signage
- Do not show monitors
- Do not show projectors

Image requirements:
- Portrait social media composition suitable for 1080 x 1350 output
- Realistic editorial photography, not illustration
- Premium campaign quality
- Natural human expressions
- Clear subject focus
- Clean background
- Show authentic activity and interaction
- Avoid generic office scenes unless clearly relevant
- Avoid generic stock-photo poses
- Avoid people posing directly for camera
- Avoid arms-crossed corporate portraits
- Do not generate culturally specific imagery unless explicitly requested
- Avoid cultural stereotypes

Strict negative rules:
- PHOTO ONLY
- No text
- No words
- No typography
- No headlines
- No letters
- No numbers
- No punctuation
- No poster design
- No marketing banner inside the image
- No captions
- No labels
- No signs
- No text overlays
- No readable screens
- No logos
- No signage with readable text
- No watermarks
- No fantasy elements
- No cartoon style
- No distorted faces
- No distorted hands
- No face paint
"""

    return " ".join(prompt.split())


def generate_openai_image(prompt: str) -> str:
    try:
        print("OPENAI IMAGE PROMPT:", prompt)

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="medium",
            n=1,
        )

        image_base64 = response.data[0].b64_json

        if not image_base64:
            return ""

        return f"data:image/png;base64,{image_base64}"

    except Exception as error:
        print("OPENAI IMAGE ERROR:", error)
        return ""


def generate_campaign_images(
    website_data: Dict,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str,
    photo_count: int
) -> List[Dict]:
    images = []

    for index in range(photo_count):
        prompt = build_openai_image_prompt(
            website_data=website_data,
            topic=topic,
            target_audience=target_audience,
            cta_text=cta_text,
            cta_link=cta_link,
            offer_promotion=offer_promotion
        )

        image_url = generate_openai_image(prompt)

        images.append({
            "prompt": prompt,
            "image_url": image_url,
            "status": "generated" if image_url else "placeholder"
        })

    return images