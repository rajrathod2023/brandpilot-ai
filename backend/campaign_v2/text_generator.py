from typing import Dict, List
import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_text(value: str) -> str:
    return " ".join(str(value).split()).strip()


def clean_hashtag(value: str) -> str:
    tag = clean_text(value)

    if not tag:
        return ""

    tag = tag.replace("#", "")
    tag = re.sub(r"[^A-Za-z0-9]", "", tag)

    if not tag:
        return ""

    return f"#{tag}"


def clean_display_link(value: str) -> str:
    link = clean_text(value)

    if not link:
        return ""

    return link.replace("https://", "").replace("http://", "").rstrip("/")


def safe_json_list(content: str) -> List:
    try:
        content = (content or "").strip()

        if not content:
            return []

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```JSON", "")
            content = content.replace("```", "")
            content = content.strip()

        data = json.loads(content)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ["posts", "items", "outputs", "results", "data"]:
                value = data.get(key)
                if isinstance(value, list):
                    return value

        return []

    except Exception as error:
        print("JSON PARSE ERROR:", error)
        print("RAW CONTENT:", content)
        return []


def generate_text_for_photo(
    website_data: Dict,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str,
    count: int
) -> List[Dict]:
    brand_name = clean_text(website_data.get("title") or "the brand")
    description = clean_text(website_data.get("description") or "")
    audience = clean_text(target_audience or "the intended audience")
    cta = clean_text(cta_text or "")
    offer = clean_text(offer_promotion or "")

    system_prompt = """
You are an expert premium campaign copywriter.

Generate Text for Photo outputs for a narrow left-side editorial panel.

Return JSON only.

Each object must have:
{
  "headline": "",
  "body": "line one\\nline two\\nline three\\nline four\\nline five\\nline six"
}

Strict rules:
- Body must contain exactly 6 lines.
- Each line must contain 2 to 3 words only.
- Never exceed 3 words on any line.
- Maximum 16 words total.
- Every line must be under 18 characters where possible.
- Do not write sentences.
- Create short emotional editorial phrases.
- No punctuation.
- No hashtags.
- No CTA links.
- No emojis.
- No full sentences.
- No long phrases.
- Each line must be short, natural, and campaign-ready.
- Must match the website business, campaign topic, and target audience.

Good example:
Explore Aotearoa
Meet local culture
Find adventure
Travel freely
Create memories
Begin today

Bad example:
Discover breathtaking landscapes
Experience vibrant culture
Plan your unforgettable journey
"""

    user_prompt = f"""
Use only this campaign data.

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

Offer / promotion:
{offer}

Generate {count} different Text for Photo outputs.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )

        raw_content = response.choices[0].message.content or "[]"
        print("TEXT FOR PHOTO RAW:", raw_content)

        items = safe_json_list(raw_content)

        if not items:
            return []

        outputs = []

        for index in range(count):
            if index >= len(items):
                break

            item = items[index]

            if not isinstance(item, dict):
                continue

            raw_body = str(item.get("body", "")).strip()
            lines = []

            for line in raw_body.split("\n"):
                clean_line = clean_text(line)
                clean_line = re.sub(r"[^\w\sāēīōūĀĒĪŌŪ-]", "", clean_line)
                words = clean_line.split()

                if len(words) > 3:
                    words = words[:3]

                if len(words) >= 2:
                    line_text = " ".join(words)

                    if len(line_text) <= 18:
                        lines.append(line_text)

                if len(lines) == 6:
                    break

            if len(lines) >= 5:
                outputs.append({
                    "headline": "",
                    "body": "\n".join(lines[:6]),
                    "cta": cta,
                    "hashtags": []
                })

        return outputs

    except Exception as error:
        print("TEXT FOR PHOTO ERROR:", error)
        return []


def generate_text_for_post(
    website_data: Dict,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str,
    count: int
) -> List[Dict]:
    brand_name = clean_text(website_data.get("title") or "the brand")
    description = clean_text(website_data.get("description") or "")
    audience = clean_text(target_audience or "the intended audience")
    cta = clean_text(cta_text or "")
    link = clean_text(cta_link or website_data.get("website_url", ""))
    offer = clean_text(offer_promotion or "")

    system_prompt = """
You are an expert social media campaign strategist and copywriter.

Generate standalone Text for Post outputs.

Rules:
- Return JSON only.
- Do not wrap JSON in markdown.
- Return an array of objects.
- Generate the exact number of objects requested.
- Each object must have:
{
  "headline": "short post headline",
  "body": "post text only",
  "hashtags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4"]
}
- Headline must be 4 to 8 words.
- Body must be 2 to 3 short sentences.
- Body must not include CTA link.
- Body must not include hashtags.
- Body must strongly match the website theme, brand context, industry, campaign topic, audience, CTA, and offer.
- Do not write generic posts.
- Every post must be clearly different.
- Do not repeat the same sentence structure.
- Generate 4 to 6 relevant hashtags.
- Hashtags must match the website industry and campaign topic.
- No emojis.
- Keep the post premium, clear, and campaign-ready.
"""

    user_prompt = f"""
Use only the campaign data below.
Do not invent unrelated fallback content.
Write posts that clearly match this website/business.

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

Generate {count} different standalone Text for Post outputs.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85,
        )

        raw_content = response.choices[0].message.content or "[]"
        print("TEXT FOR POST RAW:", raw_content)

        posts = safe_json_list(raw_content)

        if not posts:
            print("TEXT FOR POST INVALID JSON:", raw_content)
            return []

        outputs = []

        for index in range(count):
            if index >= len(posts):
                break

            post = posts[index]

            if not isinstance(post, dict):
                continue

            body = clean_text(str(post.get("body", "")))
            headline = clean_text(str(post.get("headline", "")))
            hashtags = post.get("hashtags", [])

            if not isinstance(hashtags, list):
                hashtags = []

            cleaned_hashtags = []

            for tag in hashtags[:6]:
                cleaned = clean_hashtag(str(tag))
                if cleaned:
                    cleaned_hashtags.append(cleaned)

            if body:
                outputs.append({
                    "headline": headline,
                    "body": body,
                    "cta": cta,
                    "cta_link": clean_display_link(link),
                    "offer_promotion": offer,
                    "hashtags": cleaned_hashtags
                })

        return outputs

    except Exception as error:
        print("TEXT FOR POST ERROR:", error)
        return []