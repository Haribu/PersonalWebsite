from PIL import Image
import os

assets = [
    'website/public/assets/favicon.png',
    'website/public/assets/logo_guidepoint.png',
    'website/public/assets/header_adversarial_ai.webp',
    'website/public/assets/header_automation_paradox.webp',
    'website/public/assets/header_data_poisoning.webp'
]

for a in assets:
    if os.path.exists(a):
        with Image.open(a) as img:
            print(f"{a}: {img.size} {img.format}")
    else:
        print(f"{a}: MISSING")
