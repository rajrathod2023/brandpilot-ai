import { useState } from "react";
import html2canvas from "html2canvas";
import "./CampaignBuilderV2.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

type CampaignText = {
  headline?: string;
  body: string;
  cta: string;
  hashtags: string[];
  cta_link?: string;
  offer_promotion?: string;
};

type CampaignImage = {
  prompt: string;
  image_url: string;
  status: string;
};

type VisualOutput = {
  text: CampaignText;
  image: CampaignImage;
};

type CampaignResult = {
  website_data: {
    website_url?: string;
    title: string;
    description: string;
    headings: string[];
    primary_color?: string;
    accent_color?: string;
  };

  campaign_settings?: {
    topic?: string;
    target_audience?: string;
    cta_text?: string;
    cta_link?: string;
    offer_promotion?: string;
  };

  visual_outputs: VisualOutput[];
  text_outputs: CampaignText[];
};

export default function CampaignBuilderV2() {
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [topic, setTopic] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [ctaText, setCtaText] = useState("");
  const [ctaLink, setCtaLink] = useState("");
  const [offerPromotion, setOfferPromotion] = useState("");
  const [photoCount, setPhotoCount] = useState(1);
  const [textCount, setTextCount] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CampaignResult | null>(null);

  function shorten(value: string, max = 18) {
    if (!value) return "";
    if (value.length <= max) return value;
    return value.substring(0, max).trim() + "...";
  }

  async function copyPost(text: CampaignText) {
    try {
      await navigator.clipboard.writeText(text.body);
      alert("Post copied");
    } catch (error) {
      console.error(error);
    }
  }

  async function downloadPhoto(index: number) {
    const photo = document.getElementById(`photo-output-${index}`);

    if (!photo) {
      alert("Photo not found");
      return;
    }

    try {
      const canvas = await html2canvas(photo, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#ffffff",
      });

      const image = canvas.toDataURL("image/png");

      const link = document.createElement("a");
      link.href = image;
      link.download = `campaign-photo-${index + 1}.png`;
      link.click();
    } catch (error) {
      console.error(error);
      alert("Failed to download photo");
    }
  }

  async function handleGenerate() {
    try {
      setLoading(true);

      const response = await fetch(`${API_BASE_URL}/api/campaign-v2/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          websiteUrl,
          topic,
          targetAudience,
          ctaText,
          ctaLink,
          offerPromotion,
          photoCount,
          textCount,
        }),
      });

      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error(error);
      alert("Failed to generate campaign");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="campaign-v2-page">
      <section className="campaign-v2-hero">
        <p className="campaign-v2-eyebrow">Campaign Builder V2</p>

        <h1>Build complete AI campaigns from one brief</h1>

        <p className="campaign-v2-description">
          Generate requested photo outputs and separate text for post from one
          website and campaign topic.
        </p>

        <div className="campaign-v2-form">
          <input
            placeholder="Website URL"
            value={websiteUrl}
            onChange={(event) => setWebsiteUrl(event.target.value)}
          />

          <input
            placeholder="Campaign Topic"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />

          <input
            placeholder="Target Audience (Optional)"
            value={targetAudience}
            onChange={(event) => setTargetAudience(event.target.value)}
          />

          <input
            placeholder="CTA Text"
            value={ctaText}
            onChange={(event) => setCtaText(event.target.value)}
          />

          <input
            placeholder="CTA Link (Optional)"
            value={ctaLink}
            onChange={(event) => setCtaLink(event.target.value)}
          />

          <input
            placeholder="Offer / Promotion (Optional)"
            value={offerPromotion}
            onChange={(event) => setOfferPromotion(event.target.value)}
          />

          <div className="campaign-v2-counts">
            <label>
              Photo Amount
              <input
                type="number"
                min={1}
                max={10}
                value={photoCount}
                onChange={(event) => setPhotoCount(Number(event.target.value))}
              />
            </label>

            <label>
              Text Posts Amount
              <input
                type="number"
                min={1}
                max={10}
                value={textCount}
                onChange={(event) => setTextCount(Number(event.target.value))}
              />
            </label>
          </div>

          <button onClick={handleGenerate} disabled={loading}>
            {loading
              ? "Generating AI images... please wait"
              : "Generate Campaign"}
          </button>
        </div>

        {result && (
          <>
            <section className="campaign-v2-output-section">
              <p className="campaign-v2-eyebrow">Text For Post</p>

              <h2 className="campaign-v2-section-title">
                Standalone social posts
              </h2>

              {result.text_outputs.length === 0 ? (
                <p className="campaign-v2-empty-message">
                  No text posts generated. Please check OpenAI API quota or
                  billing.
                </p>
              ) : (
                <div className="campaign-v2-social-grid">
                  {result.text_outputs.map((text, index) => (
                    <div key={index} className="campaign-v2-social-output">
                      <article className="campaign-v2-social-card">
                        <p className="campaign-v2-label">Post {index + 1}</p>

                        <p className="campaign-v2-social-body">{text.body}</p>

                        <div className="campaign-v2-social-footer">
                          {text.cta_link && (
                            <p className="campaign-v2-social-link">
                              {text.cta_link}
                            </p>
                          )}

                          {text.hashtags?.length > 0 && (
                            <p className="campaign-v2-social-hashtags">
                              {text.hashtags.join(" ")}
                            </p>
                          )}
                        </div>
                      </article>

                      <button
                        className="campaign-v2-copy-floating-btn"
                        onClick={() => copyPost(text)}
                      >
                        Copy Output
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="campaign-v2-output-section">
              <p className="campaign-v2-eyebrow">Photo Outputs</p>

              <h2 className="campaign-v2-section-title">Photo Outputs</h2>

              <div className="campaign-v2-results">
                {result.visual_outputs.map((output, index) => {
                  const campaignTopic =
                    topic || result.campaign_settings?.topic || "";

                  const campaignAudience =
                    targetAudience ||
                    result.campaign_settings?.target_audience ||
                    "";

                  const campaignOffer =
                    offerPromotion ||
                    result.campaign_settings?.offer_promotion ||
                    "";

                  const campaignLink =
                    output.text.cta_link ||
                    ctaLink ||
                    result.campaign_settings?.cta_link ||
                    websiteUrl ||
                    result.website_data.website_url ||
                    "";

                  return (
                    <div key={index} className="campaign-v2-photo-wrapper">
                      <article
                        id={`photo-output-${index}`}
                        className="campaign-v2-card"
                        style={
                          {
                            "--brand-primary":
                              result.website_data.primary_color,
                            "--brand-accent": result.website_data.accent_color,
                          } as React.CSSProperties
                        }
                      >
                        <section className="campaign-v2-photo-main">
                          <div className="campaign-v2-left-panel">
                            <div className="campaign-v2-left-meta">
                              {campaignTopic && (
                                <div className="campaign-v2-left-meta-item">
                                  <span className="campaign-v2-top-icon">
                                    ✦
                                  </span>
                                  <strong>{shorten(campaignTopic)}</strong>
                                </div>
                              )}

                              {campaignAudience && (
                                <div className="campaign-v2-left-meta-item">
                                  <span className="campaign-v2-top-icon">
                                    👥
                                  </span>
                                  <strong>{shorten(campaignAudience)}</strong>
                                </div>
                              )}

                              {campaignOffer && (
                                <div className="campaign-v2-left-meta-item">
                                  <span className="campaign-v2-top-icon">
                                    ★
                                  </span>
                                  <strong>{shorten(campaignOffer)}</strong>
                                </div>
                              )}
                            </div>

                            <div className="campaign-v2-left-body">
                              <p>{output.text.body}</p>
                            </div>

                            {campaignLink && (
                              <div className="campaign-v2-left-footer">
                                <span>◎</span>
                                <small>{campaignLink}</small>
                              </div>
                            )}
                          </div>

                          <div className="campaign-v2-image">
                            {output.image.image_url ? (
                              <img
                                src={output.image.image_url}
                                alt="Campaign"
                              />
                            ) : (
                              <div className="campaign-v2-placeholder">
                                AI Generated Image
                              </div>
                            )}
                          </div>
                        </section>
                      </article>

                      <button
                        className="campaign-v2-download-btn campaign-v2-download-outside"
                        onClick={() => downloadPhoto(index)}
                      >
                        Download Photo
                      </button>
                    </div>
                  );
                })}
              </div>
            </section>
          </>
        )}
      </section>
    </main>
  );
}