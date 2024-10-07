import base64
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes



def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    
    public_key = private_key.public_key()


    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem.decode(), public_key_pem.decode()



def encrypt_message(message: str, publicKeyStr: str):
    publicKey: PublicKeyTypes = serialization.load_pem_public_key(publicKeyStr.encode(), backend=default_backend())

    
    e_padding = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )

    encrypted_message = publicKey.encrypt(message.encode(), e_padding)

    encoded_message = base64.b64encode(encrypted_message)

    return encoded_message.decode()



def encrypt_message_for_sending(message: str, my_public_key: str, companion_public_key: str, user_id: int, reciever_id: int):
    message_as_dict = {}

    message_as_dict[user_id] = encrypt_message(message, my_public_key)
    message_as_dict[reciever_id] = encrypt_message(message, companion_public_key)

    return json.dumps(message_as_dict)

