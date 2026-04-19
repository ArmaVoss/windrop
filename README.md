# windrop
An "airdrop" applicition for windows

## endpoints 
- /api/v1/otp/generate ← exposed locally 
- /api/v1/enroll ← exposed on LAN
- /api/v1/upload ← exposed on LAN


# local config 
Set up certs in localdev directory for local development 

1. Ensure you are in localdev directory then run next steps 
2. `openssl ecparam -name prime256v1 -genkey -noout -out root_ca.key`
3.  ``` 
    openssl req -x509 -new -key root_ca.key -sha256 -days 3650 \
        -out root_ca.crt \
        -subj "/CN=Windrop Root CA"
    ```
