# 📦 ImageChain

**ImageChain** is a secure, blockchain-powered platform for storing digital images and verifying certificates using **MongoDB** and **Hyperledger Fabric**. It enables secure image storage and real-time certificate validation via a simple, responsive UI.

---

## 🚀 Features

- 📤 Upload and store digital images securely
- 🔐 Certificate issuance and verification using Hyperledger Fabric
- 🧾 Transparent and immutable record of images and certificates
- 🧠 MongoDB used for fast and scalable off-chain storage
- 💻 User-friendly UI using HTML + TailwindCSS

---

## 🛠️ Tech Stack

| Layer       | Technology              |
|-------------|--------------------------|
| Frontend    | HTML, TailwindCSS, Jinja2 |
| Backend     | Python (Flask)           |
| Database    | MongoDB                  |
| Blockchain  | Hyperledger Fabric       |
| Tools       | Docker, Docker Compose, Fabric CA |

---

## 🧱 Architecture Overview

```mermaid
graph TD
A[User Uploads Image] --> B[Store image & metadata in MongoDB]
B --> C[Hash image]
C --> D[Record hash in Hyperledger Fabric]
D --> E[Issue or Verify Certificate]
````

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/imagechain.git
cd imagechain
```

### 2. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 3. Start MongoDB

Ensure MongoDB is running locally, or update your `.env` with the connection string.

### 4. Set Up Hyperledger Fabric Test Network

Follow [Fabric documentation](https://hyperledger-fabric.readthedocs.io/en/latest/test_network.html):

```bash
cd fabric-samples/test-network
./network.sh up createChannel -c mychannel -ca
```

### 5. Deploy Chaincode

```bash
./network.sh deployCC -ccn certcc -ccp ../chaincode/cert -ccl javascript
```

### 6. Run Flask Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## 📄 API Endpoints

| Method | Route                           | Description                     |
| ------ | ------------------------------- | ------------------------------- |
| GET    | `/`                             | Homepage with blockchain viewer |
| POST   | `/upload`                       | Upload image                    |
| POST   | `/verify`                       | Verify uploaded image           |
| POST   | `/issue-certificate`            | Issue new certificate           |
| GET    | `/verify-certificate/<cert_id>` | Verify issued certificate       |

---

## 🧪 Sample Use Cases

* University issuing certificates to students on blockchain
* Validating image originality and timestamp
* Tracking digital asset authenticity

---

## 📚 Future Improvements

* Add JWT-based authentication
* Role-based access control (Admin, Institution, User)
* IPFS fallback for optional decentralized image backup
* Add certificate QR code generation

---

