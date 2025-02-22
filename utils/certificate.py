from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import random
import datetime as dt
from datetime import datetime, timedelta


def create_domain_certificate(domain_name: str,
                              issuer_cert_path: str,
                              issuer_key_path: str,
                              output_cert_path: str = "output_certificate.crt",
                              output_key_path: str = "output_key.key",
                              days_valid: int = 365):
    with open(issuer_cert_path, 'rb') as f:
        issuer_cert = x509.load_pem_x509_certificate(f.read())
        
    with open(issuer_key_path, 'rb') as f:
        issuer_key = load_pem_private_key(f.read(), password=None)
        
    new_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domain_name),
    ])
    
    new_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer_cert.subject
    ).public_key(
        new_key.public_key()
    ).serial_number(
        random.SystemRandom().randint(1, 2**64 - 1)
    ).not_valid_before(
        datetime.now(dt.timezone.utc)
    ).not_valid_after(
        datetime.now(dt.timezone.utc) + timedelta(days=days_valid)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(domain_name)]),
        critical=False,
    ).add_extension(
        x509.KeyUsage(digital_signature=True, key_encipherment=True, content_commitment=False,
                      data_encipherment=False, key_agreement=False, key_cert_sign=False, crl_sign=False,
                      encipher_only=False, decipher_only=False),
        critical=False,
    ).add_extension(
        x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.SERVER_AUTH]),
        critical=False,
    ).sign(issuer_key, hashes.SHA256())
    
    cert_pem = new_cert.public_bytes(serialization.Encoding.PEM)
    key_pem = new_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(output_cert_path, "wb") as f:
        f.write(cert_pem)
    with open(output_key_path, "wb") as f:
        f.write(key_pem)