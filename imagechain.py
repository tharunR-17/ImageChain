import hashlib
import json
import requests
from datetime import datetime
import socket
import threading

IPFS_API_URL = "http://127.0.0.1:5001/api/v0"  # IPFS API endpoint

class ImageChain:
    def __init__(self):
        self.chain = self.load_from_ipfs()
        self.difficulty = 4  # Number of leading zeros required for PoW
        self.peers = set()  # Set of connected peers (IP:Port)

    def add_to_ipfs(self, data):
        """Upload data to IPFS and return its hash."""
        response = requests.post(f"{IPFS_API_URL}/add", files={"file": ("data.json", json.dumps(data))})
        if response.status_code == 200:
            return response.json()["Hash"]
        else:
            raise Exception(f"Error adding to IPFS: {response.text}")

    def load_from_ipfs(self):
        """Retrieve the latest blockchain from IPFS."""
        try:
            with open("blockchain_hash.txt", "r") as f:
                latest_hash = f.read().strip()
            response = requests.get(f"{IPFS_API_URL}/cat?arg={latest_hash}")
            if response.status_code == 200:
                return json.loads(response.text)
        except:
            return []
        return []

    def update_ipfs(self):
        """Update the blockchain in IPFS and save the latest hash."""
        latest_hash = self.add_to_ipfs(self.chain)
        with open("blockchain_hash.txt", "w") as f:
            f.write(latest_hash)

    def proof_of_work(self, previous_hash):
        """Find a nonce that satisfies the Proof of Work condition."""
        nonce = 0
        while True:
            hash_attempt = hashlib.sha256(f"{previous_hash}{nonce}".encode()).hexdigest()
            if hash_attempt[:self.difficulty] == "0" * self.difficulty:
                return nonce
            nonce += 1

    def create_genesis_block(self, file_path):
        """Create the first block in the blockchain with an image."""
        file_hash = self.add_to_ipfs(file_path)
        genesis_block = {
            "index": 0,
            "file_hash": file_hash,
            "previous_hash": "0",
            "nonce": 0,  # No PoW for genesis block
            "timestamp": str(datetime.now()),
        }
        self.chain.append(genesis_block)
        self.update_ipfs()

    def add_block(self, file_path):
        """Add a new block containing an image's IPFS hash."""
        file_hash = self.add_to_ipfs(file_path)
        previous_hash = self.chain[-1]["file_hash"] if self.chain else "0"
        nonce = self.proof_of_work(previous_hash)  # Perform PoW
        new_block = {
            "index": len(self.chain),
            "file_hash": file_hash,
            "previous_hash": previous_hash,
            "nonce": nonce,
            "timestamp": str(datetime.now()),
        }
        self.chain.append(new_block)
        self.update_ipfs()
        self.broadcast_block(new_block)  # Broadcast the new block to peers

    def validate_block(self, block):
        """Validate a received block."""
        if block["index"] != len(self.chain):
            return False
        if block["previous_hash"] != self.chain[-1]["file_hash"]:
            return False
        hash_attempt = hashlib.sha256(
            f"{block['previous_hash']}{block['nonce']}".encode()
        ).hexdigest()
        if hash_attempt[:self.difficulty] != "0" * self.difficulty:
            return False
        return True

    def broadcast_block(self, block):
        """Broadcast a new block to all peers."""
        for peer in self.peers:
            try:
                host, port = peer.split(":")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, int(port)))
                    s.send(json.dumps({"type": "block", "data": block}).encode())
            except:
                print(f"Failed to broadcast to {peer}")

    def add_peer(self, peer):
        """Add a new peer to the network."""
        self.peers.add(peer)
