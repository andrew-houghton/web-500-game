import base64
from PIL import Image
from io import BytesIO
import os
import json

image_base64 = {}
for filename in os.listdir('static/cards'):
    image = Image.open(f'static/cards/{filename}')
    image = image.resize((image.size[0]//2,image.size[1]//2), Image.ANTIALIAS)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64[filename.replace('.png', '')] = str(base64.b64encode(buffered.getvalue()))

json.dump(image_base64, open('image_base64.json', 'w'), indent=2)