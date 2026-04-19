CREATE TABLE trusted_devices(
    cert_serial_number INTEGER PRIMARY KEY,
    device_name VARCHAR(50),
    revoked BOOLEAN NOT NULL
);