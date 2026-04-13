#!/bin/bash

# Create keys directory if it does not exist
mkdir -p keys

# Generate a Root CA
openssl genrsa -out keys/root-ca-key.pem 2048
openssl req -x509 -new -nodes -key keys/root-ca-key.pem -sha256 -days 365 -out keys/root-ca.pem -subj "/CN=Root CA"

# Generate a private key for 'kirk'
openssl genrsa -out keys/kirk-key.pem 2048

# Create a certificate signing request for 'kirk'
openssl req -new -key keys/kirk-key.pem -out keys/kirk.csr -subj "/CN=kirk"

# Generate 'kirk' certificate signed by the Root CA
openssl x509 -req -in keys/kirk.csr -CA keys/root-ca.pem -CAkey keys/root-ca-key.pem -CAcreateserial -out keys/kirk.pem -days 365 -sha256

# Cleanup the CSR file
rm -f keys/kirk.csr

echo "Certificates generated in the keys/ directory."