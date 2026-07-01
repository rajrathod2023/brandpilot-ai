from campaign_v2.website_intelligence import analyze_website
from campaign_v2.text_generator import (
    generate_text_for_photo,
    generate_text_for_post
)
from campaign_v2.image_generator import generate_campaign_images


def build_campaign(
    website_url: str,
    topic: str,
    target_audience: str,
    cta_text: str,
    cta_link: str,
    offer_promotion: str,
    photo_count: int,
    text_count: int
):
    website_data = analyze_website(website_url)

    photo_texts = generate_text_for_photo(
        website_data=website_data,
        topic=topic,
        target_audience=target_audience,
        cta_text=cta_text,
        cta_link=cta_link,
        offer_promotion=offer_promotion,
        count=photo_count
    )

    images = generate_campaign_images(
        website_data=website_data,
        topic=topic,
        target_audience=target_audience,
        cta_text=cta_text,
        cta_link=cta_link,
        offer_promotion=offer_promotion,
        photo_count=photo_count
    )

    photo_outputs = []

    for index in range(photo_count):
        photo_outputs.append({
            "text_for_photo": photo_texts[index],
            "image": images[index]
        })

    text_for_posts = generate_text_for_post(
        website_data=website_data,
        topic=topic,
        target_audience=target_audience,
        cta_text=cta_text,
        cta_link=cta_link,
        offer_promotion=offer_promotion,
        count=text_count
    )

    return {
        "website_data": website_data,

        "brand_style": {
            "primary_color": website_data.get("primary_color", "#072819"),
            "accent_color": website_data.get("accent_color", "#c9963b")
        },

        "campaign_settings": {
            "topic": topic,
            "target_audience": target_audience,
            "cta_text": cta_text,
            "cta_link": cta_link,
            "offer_promotion": offer_promotion
        },

        "photo_outputs": photo_outputs,
        "text_for_posts": text_for_posts,

        "visual_outputs": [
            {
                "text": item["text_for_photo"],
                "image": item["image"]
            }
            for item in photo_outputs
        ],

        "text_outputs": text_for_posts
    }