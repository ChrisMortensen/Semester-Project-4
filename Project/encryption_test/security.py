from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class ECDHKeyExchange:
    """
    Handles Elliptic-Curve Diffie-Hellman (ECDH) key exchange for secure communication. 
    
    Generates a private key using the SECP256R1 Elliptic Curve.
    """

    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        """
        Returns the public key as a properly formatted PEM string.
        """
        return self.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    def generate_shared_secret(self, peer_public_key_bytes):
        """
        Generates a shared secret using ECDH.

        Args:
            peer_public_key_bytes (bytes): The public key received from the peer in PEM format.
        Returns:
            bytes: A derived 32-byte encryption key.
        """
        # If the public key is in raw binary format (not PEM), no need to load it as PEM
        try:
            peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
        except ValueError:
            # If it's not in PEM format, treat it as raw public key data (bytes)
            peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), peer_public_key_bytes)

        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)
        derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'ecdh key').derive(shared_secret)
        return derived_key

def encrypt_message(message, key):
    """
    Encrypts a message using AES-GCM.

    Args:
        message (str): The message to encrypt.
        key (bytes): The encryption key.
    Returns:
        bytes: The encrypted message with IV and authentication tag.
    """
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext


def decrypt_message(encrypted_message, key):
    """
    Decrypts an AES-GCM encrypted message.

    Args:
        encrypted_message (bytes): The encrypted message.
        key (bytes): The decryption key.
    Returns:
        str: The decrypted message.
    """
    iv, tag, ciphertext = encrypted_message[:12], encrypted_message[12:28], encrypted_message[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()
