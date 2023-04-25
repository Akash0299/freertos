import os
import base64
import hashlib
import json

def get_file_size(file_path):
    return os.path.getsize(file_path)


def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        return base64.b64encode(hashlib.sha256(bytes).digest()).decode("utf-8")

print(get_file_size('firmware.bin'))

print(get_file_hash('firmware.bin'))
