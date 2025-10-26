#!/bin/bash

# Generate Weak SSL Certificates for Vulnerable Chat App
# Using 2048-bit key (acceptable to Python) but with weak configuration

echo "🔓 Generating WEAK SSL certificates for penetration testing..."
echo "⚠️  These are intentionally insecure - DO NOT use in production!"

mkdir -p ssl
cd ssl

# Generate 2048-bit RSA private key (accepted by Python, but still exploitable)
echo "🔑 Generating 2048-bit RSA private key..."
openssl genrsa -out weak-key.pem 2048

# Generate self-signed certificate with weak SHA-1
echo "📜 Generating self-signed certificate with SHA-1..."
openssl req -new -x509 -key weak-key.pem -out weak-cert.pem -days 365 \
  -subj "/C=US/ST=Gotham/L=GothamCity/O=VulnerableChat/CN=localhost" \
  -sha1

chmod 600 weak-key.pem
chmod 644 weak-cert.pem

echo ""
echo "✅ Weak SSL certificates generated!"
echo ""
echo "📄 Certificate Details:"
openssl x509 -in weak-cert.pem -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After|Public-Key:|Signature Algorithm)"

echo ""
echo "🔐 Files created:"
echo "  - weak-key.pem (2048-bit RSA private key)"
echo "  - weak-cert.pem (Self-signed certificate with SHA-1)"
echo ""
echo "⚠️  VULNERABILITIES:"
echo "  ✗ Self-signed certificate (no CA validation)"
echo "  ✗ SHA-1 signature algorithm (deprecated, collision attacks)"
echo "  ✗ No hostname verification"
echo "  ✗ Weak cipher suites supported"
echo ""
