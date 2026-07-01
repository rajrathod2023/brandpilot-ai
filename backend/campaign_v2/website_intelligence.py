from typing import Dict, List
import json
import re
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_PRIMARY_COLOR = "#072819"
DEFAULT_ACCENT_COLOR = "#c9963b"

BLOCKED_TITLES = [
    "access denied",
    "forbidden",
    "unauthorized",
    "403",
    "404",
    "not found",
]


def clean_text(value: str) -> str:
    return " ".join(str(value).split()).strip()


def get_domain_name(website_url: str) -> str:
    try:
        domain = urlparse(website_url).netloc.replace("www.", "")
        name = domain.split(".")[0]
        return name.replace("-", " ").title()
    except Exception:
        return "Website"


def is_blocked_title(title: str) -> bool:
    clean_title = clean_text(title).lower()
    return any(blocked in clean_title for blocked in BLOCKED_TITLES)


def safe_json_dict(content: str) -> Dict:
    try:
        content = (content or "").strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)

        if isinstance(data, dict):
            return data

        return {}
    except Exception:
        return {}


def infer_brand_colors_with_ai(
    website_url: str,
    title: str,
    description: str,
    headings: List[str],
) -> Dict[str, str]:
    try:
        prompt = f"""
Return ONLY valid JSON.

You are choosing brand colours for a premium social media campaign card.

Based on this website/business, infer two HEX colours that best represent the brand identity and will look good as a header/footer.

Rules:
- primary_color is used as a large header and footer background.
- primary_color must be dark enough for white text to be readable.
- accent_color is used for icons, headings, dividers, and CTA highlights.
- accent_color must contrast well against primary_color.
- Prefer the official brand colours if they are obvious from the website name, URL, title, description, or headings.
- If the brand uses a very bright colour, choose a darker premium editorial version of that colour.
- Avoid random blue unless the brand is clearly blue.
- Avoid random red unless the brand is clearly red.
- Avoid pure white, light grey, or pale colours as primary_color.
- Avoid neon or fluorescent colours.
- For cafes, restaurants, food and hospitality, prefer warm espresso, brown, charcoal, cream, copper, gold, or deep red if appropriate.
- For banks and finance, prefer deep green, navy, charcoal, burgundy, or strong official brand colours.
- For universities, prefer deep blue, navy, black, or official academic colours.
- For technology and cybersecurity, prefer charcoal, black, navy, electric blue, teal, or gold.
- For tourism and travel, prefer deep green, ocean blue, teal, black, or natural earth tones.
- Return only this JSON shape:
{{
  "primary_color": "#000000",
  "accent_color": "#ffffff"
}}

Website URL:
{website_url}

Title:
{title}

Description:
{description}

Headings:
{headings[:8]}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a brand identity designer. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        data = safe_json_dict(response.choices[0].message.content or "")

        primary = clean_text(data.get("primary_color", ""))
        accent = clean_text(data.get("accent_color", ""))

        if re.match(r"^#[0-9a-fA-F]{6}$", primary) and re.match(r"^#[0-9a-fA-F]{6}$", accent):
            return {
                "primary_color": primary,
                "accent_color": accent
            }

        return {
            "primary_color": DEFAULT_PRIMARY_COLOR,
            "accent_color": DEFAULT_ACCENT_COLOR
        }

    except Exception as error:
        print("AI BRAND COLOR ERROR:", error)
        return {
            "primary_color": DEFAULT_PRIMARY_COLOR,
            "accent_color": DEFAULT_ACCENT_COLOR
        }

def analyze_website(website_url: str) -> Dict:
    try:
        response = requests.get(
            website_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        html = response.text or ""
        soup = BeautifulSoup(html, "html.parser")

        title = clean_text(soup.title.string) if soup.title and soup.title.string else ""

        if is_blocked_title(title):
            title = get_domain_name(website_url)

        meta_description = ""

        description_tag = soup.find("meta", attrs={"name": "description"})

        if description_tag:
            meta_description = clean_text(description_tag.get("content", ""))

        if is_blocked_title(meta_description):
            meta_description = ""

        headings = []

        for heading in soup.find_all(["h1", "h2"]):
            text = clean_text(heading.get_text(strip=True))

            if text and not is_blocked_title(text):
                headings.append(text)

        title = title or get_domain_name(website_url)

        brand_colors = infer_brand_colors_with_ai(
            website_url=website_url,
            title=title,
            description=meta_description,
            headings=headings,
        )

        print("WEBSITE:", website_url)
        print("TITLE:", title)
        print("PRIMARY COLOR:", brand_colors["primary_color"])
        print("ACCENT COLOR:", brand_colors["accent_color"])

        return {
            "website_url": website_url,
            "title": title,
            "description": meta_description,
            "headings": headings[:10],
            "primary_color": brand_colors["primary_color"],
            "accent_color": brand_colors["accent_color"]
        }

    except Exception as error:
        print("Website intelligence error:", error)

        return {
            "website_url": website_url,
            "title": get_domain_name(website_url),
            "description": "",
            "headings": [],
            "primary_color": DEFAULT_PRIMARY_COLOR,
            "accent_color": DEFAULT_ACCENT_COLOR
        }