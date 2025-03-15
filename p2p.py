import hashlib
import json
import requests
from datetime import datetime
import socket
import threading
from imagechain import ImageChain

class P2PNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.imagechain = ImageChain()
        self.peers = set()

    def start(self):
        """Start the P2P node."""
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

    def _run_server(self):
        """Run a server to accept connections from peers."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Node listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                print(f"Connected to {addr}")
                threading.Thread(target=self._handle_connection, args=(conn,)).start()

    def _handle_connection(self, conn):
        """Handle incoming connections."""
        with conn:
            data = conn.recv(1024).decode()
            if data:
                message = json.loads(data)
                if message["type"] == "block":
                    block = message["data"]
                    if self.imagechain.validate_block(block):
                        self.imagechain.chain.append(block)
                        print(f"New block added: {block}")
                    else:
                        print("Invalid block received")
                elif message["type"] == "peer":
                    self.imagechain.add_peer(message["data"])

    def connect_to_peer(self, peer_host, peer_port):
        """Connect to another peer."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_host, int(peer_port)))
            self.peers.add(f"{peer_host}:{peer_port}")
            self.imagechain.add_peer(f"{peer_host}:{peer_port}")
            s.send(json.dumps({"type": "peer", "data": f"{self.host}:{self.port}"}).encode())
            print(f"Connected to peer {peer_host}:{peer_port}")

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

if __name__ == "__main__":
    # Initialize the P2P node
    node1 = P2PNode("127.0.0.1", 5000)
    node1.start()

    # Connect to another peer
    node1.connect_to_peer("127.0.0.1", 5001)

    # Add blocks to the chain
    node1.imagechain.create_genesis_block("mypic1.jpg")
    node1.imagechain.add_block("ARamesh_photo.jpg")
    node1.imagechain.add_block("20171113_181802.jpg")

    # Verify the chain
    if node1.imagechain.verify_chain():
        print("\n✅ ImageChain is valid.\n")
    else:
        print("\n❌ ImageChain is corrupted.\n")

    # Print the blockchain
    print("🖼️ ImageChain Blocks:\n")
    print(json.dumps(node1.imagechain.chain, indent=4))