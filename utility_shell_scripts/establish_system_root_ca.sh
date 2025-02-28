#!/usr/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <path-to-rootCA.crt>"
  exit 1
fi

CERT_PATH=$1
CERT_NAME=$(basename "$CERT_PATH")

if [ -f "/usr/local/share/ca-certificates/$CERT_NAME" ]; then
  echo "Certificate already exists in /usr/local/share/ca-certificates/"
else
  sudo cp "$CERT_PATH" /usr/local/share/ca-certificates/
  sudo update-ca-certificates
fi

openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt "$CERT_PATH"

PROFILE=$(ls ~/.mozilla/firefox/ | grep '\.default-release')
if [ -z "$PROFILE" ]; then
  echo "No firefox profile found"
  exit 1
fi

echo "Found firefox profile: $PROFILE"
echo "Importing root CA to firefox profile"

certutil -A -n "Aarav Root CA" -t "TC,C,C" -i "$CERT_PATH" -d sql:$HOME/.mozilla/firefox/$PROFILE
echo "Successfully imported root CA to firefox profile"

echo "Verifying root CA in firefox profile"
certutil -L -d sql:$HOME/.mozilla/firefox/$PROFILE | grep "Aarav Root CA"