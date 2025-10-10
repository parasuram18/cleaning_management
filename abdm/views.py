from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json, base64, os, requests
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from django.utils.timezone import now, timedelta
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# ✅ Step 1: Generate Ephemeral Key Pair
def generate_ephemeral_key():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, base64.b64encode(public_key.public_bytes_raw()).decode()

# ✅ Step 2: Derive Shared Secret
def derive_secret(private_key, recipient_pub_key_b64):
    recipient_pub_key_bytes = base64.b64decode(recipient_pub_key_b64)
    print("done==========", len(recipient_pub_key_bytes))
    recipient_pub_key = x25519.X25519PublicKey.from_public_bytes(recipient_pub_key_b64[:32])
    print("done=ww=========", len(recipient_pub_key))
    return private_key.exchange(recipient_pub_key)

# ✅ Step 3: Encrypt Content (FHIR JSON)
def encrypt_content(content, secret):
    aesgcm = AESGCM(secret[:32])  # use first 32 bytes
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, content.encode(), None)
    return base64.b64encode(ciphertext).decode(), base64.b64encode(nonce).decode()

# ✅ Step 4: Build Transfer Payload
def build_transfer_payload(fhir_resource, recipient_pub_key_b64):
    priv, eph_pub_b64 = generate_ephemeral_key()
    print("here.....", priv, eph_pub_b64)
    secret = derive_secret(priv, recipient_pub_key_b64)
    encrypted, nonce_b64 = encrypt_content(json.dumps(fhir_resource), secret)

    return {
        "pageNumber": 1,
        "pageCount": 1,
        "transactionId": "your-transaction-id",
        "entries": [
            {
                "content": encrypted,
                "media": "application/fhir+json",
                "checksum": "dummy-checksum",
                "careContextReference": "context-123"
            }
        ],
        "keyMaterial": {
            "cryptoAlg": "ECDH",
            "curve": "Curve25519",
            "dhPublicKey": {
                "expiry": (now() + timedelta(minutes=10)).isoformat(),
                "parameters": "Ephemeral public key",
                "keyValue": eph_pub_b64
            },
            "nonce": nonce_b64
        }
    }

# ✅ Step 5: Send to ABHA API
def send_to_abha(fhir_data, recipient_pub_key):
    url = "https://abhasbx.abdm.gov.in/abha/api/v3/patient-hiu/app/v0.5/health-information/transfer"
    payload = build_transfer_payload(fhir_data, recipient_pub_key)
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    return response.json()

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
 
# --------- Step 1: Read image and convert to Base64 ---------
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string
 
# --------- Step 2: Encrypt Base64 string using AES ---------
def encrypt_base64(base64_string, key):
    key = key.ljust(32)[:32].encode('utf-8')  # AES-256 requires 32 bytes key
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(base64_string.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct
def image_encrypt():
    # --------- Step 3: Example usage ---------
    # Paths to your front and back images
    front_image_path = "front.jpg"
    back_image_path = "back.jpg"
    
    # Secret key for encryption (must be kept safe)
    secret_key = "mysecretpassword123"
    
    # Convert images to Base64
    front_base64 = image_to_base64(front_image_path)
    back_base64 = image_to_base64(back_image_path)
    
    # Encrypt the Base64 strings
    front_iv, front_encrypted = encrypt_base64(front_base64, secret_key)
    back_iv, back_encrypted = encrypt_base64(back_base64, secret_key)
    
    print("Front Image Encrypted Base64:", front_encrypted)
    print("Front Image IV:", front_iv)
    print("Back Image Encrypted Base64:", back_encrypted)
    print("Back Image IV:", back_iv)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_keys(request):
    try:

        ephemeral_private_key = x25519.X25519PrivateKey.generate()

        ephemeral_public_key = ephemeral_private_key.public_key()

        public_key_bytes = ephemeral_public_key.public_bytes(
                serialization.Encoding.Raw,
                serialization.PublicFormat.Raw
            )
        ephemeral_pub_b64 = base64.b64encode(public_key_bytes).decode("utf-8")
        
        # Serialize private key (only for server-side storage, not returned)
        private_key_bytes = ephemeral_private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_key_b64 = base64.b64encode(private_key_bytes).decode("utf-8")

        nonce = os.urandom(12)
        nonce_b64 = base64.b64encode(nonce).decode("utf-8")

        credentials = {
            "private_key":private_key_b64,
            "public_key":ephemeral_pub_b64,
            "nonce":nonce_b64
        }
        return Response({"data":credentials})
    except:
        import traceback
        print("-------------------------ERROR--------------------------")
        traceback.print_exc()
        return Response({"data":"failed"})
    

@api_view(['POST'])
@permission_classes([AllowAny])
def encrypt_data(request):
    try:
        print("---------------------------------")
        # image_encrypt()
        data = request.data

        # === Step 2: Extract ABDM HIU’s public key ===
        recipient_pub_b64 = data["RecieverPublicKey"]
        recipient_pub_bytes = base64.b64decode(recipient_pub_b64)
        if len(recipient_pub_bytes) == 65:  # sometimes ABDM sends 65-byte key
            recipient_pub_bytes = recipient_pub_bytes[1:33]

        recipient_public_key = x25519.X25519PublicKey.from_public_bytes(recipient_pub_bytes)

        # === Step 3: Generate your own ephemeral key pair ===
        sender_private_key_b64 = data['SenderPrivateKey']
        sender_private_key_bytes = base64.b64decode(sender_private_key_b64)
        sender_private_key = x25519.X25519PrivateKey.from_private_bytes(sender_private_key_bytes)
        
        sender_public_key_b64 = data['SenderPublicKey']

        # === Step 4: Perform ECDH to derive shared secret ===
        shared_secret = sender_private_key.exchange(recipient_public_key)
        hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b"abdm-ecdh-aes-key",
            )

        # aes_key = shared_secret[:32]  # AES-256 key
        aes_key = hkdf.derive(shared_secret)  # AES-256 key

        # === Step 5: Encrypt health data / Load from the json file or get it in payload ===
        try:
            current_dir = os.path.dirname(__file__)   # folder of the current .py file
            file_path = os.path.join(current_dir, "newdata.json")
            file = open(file_path, 'r')
            health_data = json.load(file)
        except Exception as e:
            print("exc = ", str(e))

        # health_data =data['health_data']

        plaintext = json.dumps(health_data).encode("utf-8")

        nonce_str = data['SenderNonce']
        # convert string  to bytes
        nonce_bytes = nonce_str.encode("utf-8")
        # for sendig in response
        nonce_b64 = base64.b64encode(nonce_bytes).decode("utf-8")

        aesgcm = AESGCM(aes_key)
        ciphertext = aesgcm.encrypt(nonce_bytes, plaintext, None)
        ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")

        check_sum = data['check_sum']
        check_sum_bytes = check_sum.encode("utf-8")
        check_sum_b64 = base64.b64encode(check_sum_bytes).decode()
        print("sum type === ", type(check_sum))
        print("sum type === ", type(check_sum_b64))

        encrypted_data = {
          "expiry": (now() + timedelta(minutes=10)).isoformat(),
          "parameters": "Curve25519/32byte random key",
          "keyValue": sender_public_key_b64,
          "nonce": nonce_b64,
          "content": ciphertext_b64,
          "ckeck_sum": check_sum
        }

        return Response({"data":encrypted_data})
    except:
        import traceback
        print("-------------------------ERROR--------------------------")
        traceback.print_exc()
        return Response({"data":"failed"})
    
@api_view(['POST'])
@permission_classes([AllowAny,])
def decrypt_data_HIU(request):
    try:
        data = request.data

        # === Step 1: Decode inputs ===
        ciphertext_b64 = data['encoded_content']
        ciphertext = base64.b64decode(ciphertext_b64)

        hiu_private_key_b64 = data['hiu_privatekey']
        hiu_private_key_bytes = base64.b64decode(hiu_private_key_b64)

        hip_public_key_b64 = data['hip_publickey']
        hip_public_key_bytes = base64.b64decode(hip_public_key_b64)

        nonce_b64 = data['hiu_nonce']
        nonce_bytes = base64.b64decode(nonce_b64)

        # === Step 2: Reconstruct key objects ===
        hiu_private_key = x25519.X25519PrivateKey.from_private_bytes(hiu_private_key_bytes)
        hip_public_key = x25519.X25519PublicKey.from_public_bytes(hip_public_key_bytes)

        # === Step 3: Derive shared secret ===
        shared_secret = hiu_private_key.exchange(hip_public_key)

        # === Step 4: Derive AES key from shared secret using HKDF ===
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"abdm-ecdh-aes-key",
        )
        aes_key = hkdf.derive(shared_secret)

        # === Step 5: Decrypt with AES-GCM ===
        aesgcm = AESGCM(aes_key)
        plaintext = aesgcm.decrypt(nonce_bytes, ciphertext, None)

        return Response({"decoded_data":plaintext}) 
    except:
        import traceback
        print("-------------------------ERROR--------------------------")
        traceback.print_exc()
        return Response({"data":"failed"})
    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def listen_webhook(request):
    print('-----------------')
    print(request.data)
    return Response({'status':'success'})