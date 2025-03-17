import cv2
import json
import numpy as np
import requests
import os

# Get the absolute path to the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"

def str_to_bin(data):
    """Convert string to binary format"""
    return ''.join(format(ord(char), '08b') for char in data)

def bin_to_str(binary_data):
    """Convert binary format to string"""
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(char, 2)) for char in chars if int(char, 2) != 0)

def embed_json(image_path, json_data, output_path):
    """Embed JSON data into an image using LSB steganography"""
    # Convert to absolute path
    image_path = os.path.join(PROJECT_DIR, image_path)
    output_path = os.path.join(PROJECT_DIR, output_path)

    print(f"📂 Attempting to read image from: {image_path}")

    # Check if the image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ Image file not found: {image_path}")

    img = cv2.imread(image_path)  # Read image
    if img is None:
        raise ValueError(f"❌ Unable to read image file: {image_path}")

    json_str = json.dumps(json_data) + "###"  # Append end marker
    json_bin = str_to_bin(json_str)  # Convert JSON to binary

    height, width, channels = img.shape
    total_pixels = height * width * 3  # RGB channels

    if len(json_bin) > total_pixels:
        raise ValueError("❌ JSON data is too large to fit inside the image.")

    index = 0
    for row in range(height):
        for col in range(width):
            for channel in range(3):  # Iterate over RGB channels
                if index < len(json_bin):
                    img[row, col, channel] = (img[row, col, channel] & ~1) | int(json_bin[index])
                    index += 1

    cv2.imwrite(output_path, img)
    print(f"✅ JSON data embedded successfully in {output_path}")

def extract_json(image_path):
    """Extract JSON data from an image using LSB steganography"""
    # Convert to absolute path
    image_path = os.path.join(PROJECT_DIR, image_path)

    print(f"📂 Attempting to read image from: {image_path}")

    # Check if the image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ Image file not found: {image_path}")

    img = cv2.imread(image_path)  # Read image
    if img is None:
        raise ValueError(f"❌ Unable to read image file: {image_path}")

    height, width, channels = img.shape
    binary_data = ""

    # Extract LSBs from the image
    for row in range(height):
        for col in range(width):
            for channel in range(3):  # Iterate over RGB channels
                binary_data += str(img[row, col, channel] & 1)

    # Convert binary data to string
    json_str = bin_to_str(binary_data)

    # Find the end marker and extract JSON
    end_marker = "###"
    if end_marker in json_str:
        json_str = json_str.split(end_marker)[0]  # Remove end marker
        try:
            json_data = json.loads(json_str)  # Parse JSON
            print(f"✅ JSON data extracted successfully from {image_path}")
            return json_data
        except json.JSONDecodeError:
            raise ValueError("❌ Extracted data is not valid JSON.")
    else:
        raise ValueError("❌ End marker not found in extracted data.")

def add_to_ipfs(file_path):
    """Add an image to IPFS using requests and return the hash"""
    file_path = os.path.join(PROJECT_DIR, file_path)
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(IPFS_API_URL, files=files)

    if response.status_code == 200:
        ipfs_hash = response.json()["Hash"]
        print(f"📌 Image uploaded to IPFS: {ipfs_hash}")
        return ipfs_hash
    else:
        raise Exception(f"❌ Failed to upload to IPFS: {response.text}")

# Step 1: Embed and upload Image 1
json_data_1 = {
    "image_id": "img_1",
    "description": "First image in the chain",
    "transactions": [
        {"type": "credit", "amount": 500, "date": "2025-03-16"},
        {"type": "debit", "amount": 200, "date": "2025-03-15"}
    ],
    "previous_hash": None  # First image has no previous hash
}

input_image_1 = "static/images/mypic1.jpg"
output_image_1 = "output_image1.png"

embed_json(input_image_1, json_data_1, output_image_1)
ipfs_hash_1 = add_to_ipfs(output_image_1)  # Upload to IPFS

# Step 2: Embed and upload Image 2 (linked to Image 1)
json_data_2 = {
    "image_id": "img_2",
    "description": "Second image in the chain",
    "transactions": [
        {"type": "credit", "amount": 700, "date": "2025-03-17"},
        {"type": "debit", "amount": 300, "date": "2025-03-16"}
    ],
    "previous_hash": ipfs_hash_1  # Link to the first image
}

input_image_2 = "static/images/ARamesh_photo.jpg"
output_image_2 = "output_image2.png"

embed_json(input_image_2, json_data_2, output_image_2)
ipfs_hash_2 = add_to_ipfs(output_image_2)  # Upload to IPFS

# Final Output: Chain Data
image_chain = {
    "image_1": {
        "ipfs_hash": ipfs_hash_1,
        "metadata": json_data_1
    },
    "image_2": {
        "ipfs_hash": ipfs_hash_2,
        "metadata": json_data_2
    }
}

print("\n🔗 Image Chain:", json.dumps(image_chain, indent=4))

# Step 3: Extract JSON data from the images
print("\n🔍 Extracting JSON data from embedded images...")

# Extract JSON from Image 1
extracted_json_1 = extract_json(output_image_1)
print("📄 Extracted JSON from Image 1:", json.dumps(extracted_json_1, indent=4))

# Extract JSON from Image 2
extracted_json_2 = extract_json(output_image_2)
print("📄 Extracted JSON from Image 2:", json.dumps(extracted_json_2, indent=4))