# gen_cert.py
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress

def generate_self_signed_cert():
    # 生成私钥
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 生成证书
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Locality"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyCompany"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"192.168.1.76"), # 你的IP
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # 有效期 10 年
        datetime.datetime.utcnow() + datetime.timedelta(days=3650)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.ip_address("192.168.1.76")),
            x509.DNSName(u"localhost"),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())

    # 写出 key.pem
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 写出 cert.pem
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("证书已生成: cert.pem, key.pem")

if __name__ == "__main__":
    try:
        generate_self_signed_cert()
    except ImportError:
        print("请先安装依赖: pip install cryptography")