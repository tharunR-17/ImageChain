from datetime import datetime
import hashlib
import json
import os
from bson import ObjectId
from pymongo import MongoClient
import gridfs
from PIL import Image
from stegano import lsb

class ImageChain:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["imagechain_db"]  # Database
        self.fs = gridfs.GridFS(self.db)  # GridFS instance
        
        self.chain = self.load_from_mongodb()
        self.difficulty = 4
        self.peers = set()

    def load_from_mongodb(self):
        """Retrieve the latest blockchain from MongoDB."""
        blockchain_data = self.db["blockchain"].find_one({"_id": "imagechain"})
        return blockchain_data["chain"] if blockchain_data else []
    
    def update_mongodb(self):
        """Update the blockchain in MongoDB."""
        self.db["blockchain"].update_one(
            {"_id": "imagechain"},
            {"$set": {"chain": self.chain}},
            upsert=True
        )

    def save_image_to_mongodb(self, file_path):
        """Store image in MongoDB GridFS and return the file ID."""
        with open(file_path, "rb") as f:
            file_id = self.fs.put(f, filename=file_path)
        return str(file_id)  # Return as a string

    def get_image_from_mongodb(self, file_id, output_path):
        """Retrieve an image from MongoDB GridFS and save it locally."""
        file_id = ObjectId(file_id)  # Ensure ObjectId format
        file_data = self.fs.get(file_id).read()
        with open(output_path, "wb") as f:
            f.write(file_data)
        return output_path

    def create_genesis_block(self, file_path):
        """Create the first block with an image stored in MongoDB."""
        signature = input("Enter your signature for the genesis block: ")
        message = input("Enter the message to hide in the image: ")
        png_path = self.convert_to_png(file_path)

        # Hash the image
        with open(png_path, "rb") as f:
            image_hash = hashlib.sha256(f.read()).hexdigest()

        # Create JSON block (without file_id)
        genesis_block = {
            "index": 0,
            "file_hash": image_hash,
            "previous_hash": "0",
            "nonce": 0,
            "timestamp": str(datetime.now()),
            "signature": signature,
            "message": message,
        }

        # Embed JSON data into the image
        self.embed_json_into_image(png_path, genesis_block)

        # Store Image in MongoDB
        file_id = self.save_image_to_mongodb(png_path)

        # Add file_id to the block (not part of the embedded JSON)
        genesis_block["file_id"] = file_id

        self.chain.append(genesis_block)
        self.update_mongodb()

    def add_block(self, file_path):
        """Add a new block containing an image's MongoDB ID."""
        signature = input("Enter your signature for the new block: ")
        message = input("Enter the message to hide in the image: ")
        png_path = self.convert_to_png(file_path)

        # Hash the image
        with open(png_path, "rb") as f:
            image_hash = hashlib.sha256(f.read()).hexdigest()

        previous_hash = self.chain[-1]["file_hash"] if self.chain else "0"
        nonce = self.proof_of_work(previous_hash)

        # Create JSON block (without file_id)
        new_block = {
            "index": len(self.chain),
            "file_hash": image_hash,
            "previous_hash": previous_hash,
            "nonce": nonce,
            "timestamp": str(datetime.now()),
            "signature": signature,
            "message": message,
        }

        # Embed JSON data into the image
        self.embed_json_into_image(png_path, new_block)

        # Store Image in MongoDB
        file_id = self.save_image_to_mongodb(png_path)

        # Add file_id to the block (not part of the embedded JSON)
        new_block["file_id"] = file_id

        self.chain.append(new_block)
        self.update_mongodb()

    def proof_of_work(self, previous_hash):
        nonce = 0
        while True:
            hash_attempt = hashlib.sha256(f"{previous_hash}{nonce}".encode()).hexdigest()
            if hash_attempt[:self.difficulty] == "0" * self.difficulty:
                return nonce
            nonce += 1

    def verify_chain_real_time(self):
        """Retrieve images from MongoDB, extract JSON, and verify integrity."""
        previous_hash = "0"

        for block in self.chain:
            index = block["index"]
            file_id = block["file_id"]

            print(f"\n🔍 Verifying Block {index}...")

            # Retrieve image from MongoDB
            temp_image_path = f"temp_{index}.png"
            try:
                self.get_image_from_mongodb(file_id, temp_image_path)
            except Exception as e:
                print(f"❌ Retrieval Failed: {e}")
                return False

            # Extract JSON from image
            try:
                extracted_json = self.extract_json_from_image(temp_image_path)
                print(f"✅ Extracted JSON: {extracted_json}")
            except ValueError as e:
                print(f"❌ Extraction Failed: {e}")
                return False

            # Verify the file_hash from extracted JSON matches the stored file_hash
            if extracted_json["file_hash"] != block["file_hash"]:
                print(f"❌ Image hash mismatch for block {index}!")
                print(f"Stored Hash: {block['file_hash']}")
                print(f"Extracted Hash: {extracted_json['file_hash']}")
                return False

            # Create a copy of the block without file_id for comparison
            block_without_file_id = block.copy()
            del block_without_file_id["file_id"]

            # Normalize JSON data for comparison
            extracted_json_normalized = json.dumps(extracted_json, sort_keys=True)
            block_normalized = json.dumps(block_without_file_id, sort_keys=True)

            # Verify extracted JSON matches stored block data
            if extracted_json_normalized != block_normalized:
                print(f"❌ Integrity Check Failed: Block {index} has been tampered with!")
                print(f"Stored Block: {block_normalized}")
                print(f"Extracted JSON: {extracted_json_normalized}")
                return False

            # Update previous hash for next block
            previous_hash = block["file_hash"]

            # Cleanup temporary file
            os.remove(temp_image_path)

        print("\n✅ ImageChain integrity is intact.\n")
        return True

    def convert_to_png(self, image_path):
        """Convert an image to PNG format."""
        png_path = os.path.splitext(image_path)[0] + ".png"
        if not image_path.lower().endswith(".png"):
            image = Image.open(image_path)
            image.save(png_path, "PNG")
            print(f"✅ Converted {image_path} to {png_path}")
        else:
            png_path = image_path
        return png_path

    def embed_json_into_image(self, image_path, json_data):
        """Embed JSON data into an image using steganography."""
        try:
            image = Image.open(image_path)
            hidden_image = lsb.hide(image, json.dumps(json_data, sort_keys=True))
            hidden_image.save(image_path)
            print(f"✅ JSON data embedded into {image_path}")
        except Exception as e:
            raise ValueError(f"Failed to embed JSON into image: {e}")

    def extract_json_from_image(self, image_path):
        """Extract hidden JSON metadata from an image."""
        try:
            hidden_data = lsb.reveal(image_path)
            if hidden_data is None:
                raise ValueError("No hidden data found in image!")

            extracted_json = json.loads(hidden_data)  # Convert to dictionary
            return extracted_json
        except Exception as e:
            raise ValueError(f"Failed to extract JSON: {e}")

if __name__ == "__main__":
    imagechain = ImageChain()

    if not imagechain.chain:
        imagechain.create_genesis_block("mypic1.jpg")
    else:
        print("Loaded existing blockchain from MongoDB.")

    imagechain.add_block("ARamesh_photo.jpg")
    # imagechain.add_block("sample2.jpg")

    if imagechain.verify_chain_real_time():
        print("\n✅ ImageChain is valid.\n")
    else:
        print("\n❌ ImageChain is corrupted.\n")

    print("\n🖼️ ImageChain Blocks:\n")
    print(json.dumps(imagechain.chain, indent=4))