import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def decrypt_message(enc_message: str, private_key_str: str):
    private_key = serialization.load_pem_private_key(
        private_key_str.encode(),
        password=None,
        backend=default_backend()
    )


    enc_message_de64 = base64.b64decode(enc_message)


    original_message = private_key.decrypt(
        enc_message_de64,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return original_message.decode()

