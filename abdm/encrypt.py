import json
import base64
import os
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# === Step 1: Your JSON payload (to be encrypted) ===
payload = {
    "transactionId": "55921571-0938-4815-a218-483b60cd6680",
    "hiRequest": {
        "consent": {
            "id": "1f409252-6424-493b-82fe-5ea19466fe58"
        },
        "dateRange": {
            "from": "1925-08-28T13:02:26.719Z",
            "to": "2025-08-28T13:02:26.719Z"
        },
        "dataPushUrl": "https://abhasbx.abdm.gov.in/abha/api/v3/patient-hiu/app/v0.5/health-information/transfer",
        "keyMaterial": {
            "cryptoAlg": "ECDH",
            "curve": "curve25519",
            "dhPublicKey": {
                "expiry": "2025-09-07T13:02:27.133Z",
                "parameters": "Ephemeral public key",
                "keyValue": "BF6QpxxGue8enuq3azcPXrSmW4dz1yJ+xWYerw3kYCJ8az162Yn7gQgeqLnJnlUXejlGYTVeiRLgzJVpAZYqNiA="
            },
            "nonce": "AI7Rc2Sf0u65luXgy41IOiVS361BqDPehzel0oK4Ue4="
        }
    }
}

# === Step 2: Extract ABDM HIU’s public key (Curve25519) ===
# Provided in "dhPublicKey.keyValue" (Base64)
recipient_pub_b64 = payload["hiRequest"]["keyMaterial"]["dhPublicKey"]["keyValue"]
recipient_pub_bytes = base64.b64decode(recipient_pub_b64)
recipient_public_key = x25519.X25519PublicKey.from_public_bytes(recipient_pub_bytes)

# === Step 3: Generate your own ephemeral key pair ===
ephemeral_private_key = x25519.X25519PrivateKey.generate()
ephemeral_public_key = ephemeral_private_key.public_key()

# === Step 4: Perform ECDH to derive a shared secret ===
shared_secret = ephemeral_private_key.exchange(recipient_public_key)

# === Step 5: Derive AES key (can use HKDF, but for demo using shared_secret directly) ===
# ABDM uses AES-256-GCM, so ensure key is 32 bytes
aes_key = shared_secret[:32]

# === Step 6: Encrypt the actual data you want to push ===
# Example: only encrypt the patient health data (not keyMaterial itself)
health_data = {"some": "patient health info"}  # Replace with actual health data JSON
plaintext = json.dumps(health_data).encode("utf-8")

# Use ABDM-provided nonce (Base64 decode)
nonce_b64 = payload["hiRequest"]["keyMaterial"]["nonce"]
nonce = base64.b64decode(nonce_b64)

aesgcm = AESGCM(aes_key)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)

# === Step 7: Prepare final encrypted package ===
encrypted_data = {
    "encryptedHealthInfo": base64.b64encode(ciphertext).decode("utf-8"),
    "ephemeralPublicKey": base64.b64encode(ephemeral_public_key.public_bytes()).decode("utf-8"),
    "nonce": nonce_b64
}

print(json.dumps(encrypted_data, indent=2))

