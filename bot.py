import os
import requests
from instagrapi import Client
import google.generativeai as genai


# ----------------------------------
# ENVIRONMENT SECRETS (GitHub)
# ----------------------------------
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER = os.getenv("INSTA_USER")
IG_PASS = os.getenv("INSTA_PASS")
IG_SESSION = os.getenv("INSTA_SES")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


# ----------------------------------
# Generate 10 mysterious topics
# ----------------------------------
def generate_topics():
    prompt = """
    Create 10 unique mysterious and historical topics.
    Themes must include: ancient mysteries, lost civilizations, 
    unexplained events, vanished cultures, mythological enigmas,
    lost ships, strange artifacts, forgotten kingdoms.
    Only provide a list of 10 titles.
    """
    raw = model.generate_content(prompt).text
    topics = [t.strip("-• ") for t in raw.split("\n") if t.strip()]
    return topics[:10]


# ----------------------------------
# Generate cinematic AI prompt
# ----------------------------------
def generate_prompt(topic):
    prompt = f"""
    Create a cinematic, dark, realistic image prompt based on:
    {topic}
    Requirements: atmospheric fog, dramatic shadows, ancient mystery mood,
    ultra-detailed, photorealistic, high contrast.
    """
    return model.generate_content(prompt).text.strip()


# ----------------------------------
# Generate caption + hashtags
# ----------------------------------
def generate_caption_and_tags(topic):
    prompt = f"""
    Create an Instagram caption for: {topic}
    Style: dark, mysterious, atmospheric, short but impactful.
    Then give 10 relevant hashtags.

    Format:
    CAPTION: <text>
    TAGS: <hashtags>
    """
    text = model.generate_content(prompt).text
    parts = text.split("TAGS:")
    caption = parts[0].replace("CAPTION:", "").strip()
    tags = parts[1].strip().replace("\n", " ")
    return caption, tags


# ----------------------------------
# Pollinations: Generate image
# ----------------------------------
def generate_image(prompt, idx):
    print(f"Generating image {idx + 1}/10")
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    data = requests.get(url).content

    filename = f"img_{idx}.jpg"
    with open(filename, "wb") as f:
        f.write(data)
    return filename


# ----------------------------------
# Instagram Login (Cookie or Password)
# ----------------------------------
def insta_login():
    cl = Client()
    try:
        cl.login(IG_USER, IG_PASS)
    except:
        cl.set_settings({"sessionid": IG_SESSION})
        cl.login(IG_USER, IG_PASS)
    return cl


# ----------------------------------
# MAIN BOT LOGIC
# ----------------------------------
if __name__ == "__main__":
    cl = insta_login()

    topics = generate_topics()
    final_caption = ""
    images = []

    for i, topic in enumerate(topics):
        prompt = generate_prompt(topic)
        img_path = generate_image(prompt, i)

        images.append(img_path)

        caption, tags = generate_caption_and_tags(topic)
        final_caption += f"\n\n{topic}\n{caption}\n{tags}"

    # Upload as a multi-image carousel
    cl.album_upload(images, caption=final_caption)

    print("INSTAGRAM POST SUCCESSFULLY PUBLISHED.")
