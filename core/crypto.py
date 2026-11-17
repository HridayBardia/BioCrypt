"""
BioCrypt-DNA Cryptographic Layer
================================
Provides authenticated encryption (AES-256-GCM), key derivation via PBKDF2-HMAC-SHA256,
pre-compression with zlib (level 9), CRC-32 data integrity verification, and
deterministic binary framing.

Framing Layout:
[MAGIC_BYTES (4B: b"BCOP")] +
[PAYLOAD_LEN (4B, big-endian uint32)] +
[SALT (16B)] +
[IV (12B)] +
[TAG (16B)] +
[CRC32 (4B, big-endian uint32)] +
[CIPHERTEXT (PAYLOAD_LEN bytes)]
"""

from __future__ import annotations

import os
import struct
import zlib
from typing import Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


MAGIC_BYTES: bytes = b"BCOP"
HEADER_FORMAT: str = ">4sI16s12s16sI"
HEADER_SIZE: int = struct.calcsize(HEADER_FORMAT)  # 4 + 4 + 16 + 12 + 16 + 4 = 56 bytes
SALT_SIZE: int = 16
IV_SIZE: int = 12
TAG_SIZE: int = 16
PBKDF2_ITERATIONS: int = 100_000


class CryptoError(Exception):
    """Base exception for cryptographic operations in BioCrypt-DNA."""


class InvalidMagicError(CryptoError):
    """Raised when the payload header does not match expected magic bytes."""


class HeaderCorruptError(CryptoError):
    """Raised when the framed binary header is malformed or truncated."""


class ChecksumMismatchError(CryptoError):
    """Raised when the CRC-32 checksum verification fails."""


class AuthenticationError(CryptoError):
    """Raised when AES-256-GCM authentication tag verification fails (e.g. wrong password)."""


class CryptoEngine:
    """
    Handles authenticated encryption, deterministic header packaging,
    and integrity-checked decryption.
    """

    def __init__(self, passphrase: str):
        """
        Initialize the cryptographic engine with a user passphrase.

        Args:
            passphrase: User-supplied secret passphrase.
        """
        if not passphrase:
            raise ValueError("Passphrase must not be empty.")
        self.passphrase: bytes = passphrase.encode("utf-8")

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive a 256-bit AES key from the passphrase and salt using PBKDF2-HMAC-SHA256.

        Args:
            salt: 16-byte cryptographically secure random salt.

        Returns:
            32-byte (256-bit) symmetric key.
        """
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return kdf.derive(self.passphrase)

    def encrypt_and_pack(self, plaintext: bytes) -> bytes:
        """
        Compresses plaintext, encrypts via AES-256-GCM, and frames into the binary header.

        Pipeline:
        1. zlib compress (level 9) -> eliminates entropy skews & ASCII patterns.
        2. Generate 16-byte random salt & 12-byte IV.
        3. Derive 256-bit key via PBKDF2 (100k iterations).
        4. Encrypt with AESGCM -> produces ciphertext + 16-byte tag.
        5. Compute CRC-32 checksum on ciphertext.
        6. Pack [MAGIC | LEN | SALT | IV | TAG | CRC32 | CIPHERTEXT].

        Args:
            plaintext: Raw secret bytes to conceal.

        Returns:
            Framed binary bytes ready for biological transduction.
        """
        # 1. Compress with zlib level 9
        compressed = zlib.compress(plaintext, level=9)

        # 2. Cryptographic randomness
        salt = os.urandom(SALT_SIZE)
        iv = os.urandom(IV_SIZE)

        # 3. Derive 256-bit key
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)

        # 4. Encrypt (AESGCM returns ciphertext + 16-byte tag)
        encrypted = aesgcm.encrypt(iv, compressed, None)
        ciphertext = encrypted[:-TAG_SIZE]
        tag = encrypted[-TAG_SIZE:]

        # 5. Compute CRC-32 on ciphertext
        crc = zlib.crc32(ciphertext) & 0xFFFFFFFF
        payload_len = len(ciphertext)

        # 6. Binary framing
        header = struct.pack(
            HEADER_FORMAT,
            MAGIC_BYTES,
            payload_len,
            salt,
            iv,
            tag,
            crc,
        )
        return header + ciphertext

    def unpack_and_decrypt(self, framed_data: bytes) -> bytes:
        """
        Parses binary framing, verifies CRC-32, authenticates AES-GCM tag,
        and decompresses plaintext.

        Args:
            framed_data: Framed binary bytes retrieved from biological decoding.

        Returns:
            Original lossless plaintext bytes.

        Raises:
            HeaderCorruptError: If data is shorter than header or payload length is invalid.
            InvalidMagicError: If magic bytes do not equal b"BCOP".
            ChecksumMismatchError: If CRC-32 fails.
            AuthenticationError: If AES-GCM authentication fails (incorrect passphrase or tampering).
        """
        if len(framed_data) < HEADER_SIZE:
            raise HeaderCorruptError(
                f"Data size ({len(framed_data)} bytes) is smaller than minimum header ({HEADER_SIZE} bytes)."
            )

        magic, payload_len, salt, iv, tag, expected_crc = struct.unpack(
            HEADER_FORMAT, framed_data[:HEADER_SIZE]
        )

        if magic != MAGIC_BYTES:
            raise InvalidMagicError(
                f"Invalid magic bytes: expected {MAGIC_BYTES!r}, got {magic!r}."
            )

        ciphertext = framed_data[HEADER_SIZE : HEADER_SIZE + payload_len]
        if len(ciphertext) != payload_len:
            raise HeaderCorruptError(
                f"Ciphertext truncated: expected {payload_len} bytes, found {len(ciphertext)} bytes."
            )

        # Verify CRC-32
        actual_crc = zlib.crc32(ciphertext) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ChecksumMismatchError(
                f"CRC-32 checksum mismatch: expected {expected_crc:#010x}, calculated {actual_crc:#010x}."
            )

        # Derive key and authenticate / decrypt
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        encrypted_with_tag = ciphertext + tag

        try:
            compressed = aesgcm.decrypt(iv, encrypted_with_tag, None)
        except InvalidTag as exc:
            raise AuthenticationError(
                "Decryption failed: cryptographic tag mismatch or incorrect passphrase."
            ) from exc

        # Decompress
        try:
            plaintext = zlib.decompress(compressed)
        except zlib.error as exc:
            raise CryptoError(f"Decompression error: {exc}") from exc

        return plaintext

