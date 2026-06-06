import sys
import hashlib

API_SECRET = "91971e462d5b2d6d9fdfc8a27924f99c1a224fea84bcf6c506b7a9731bfd8584"

def validate(key: str) -> bool:
    hashed = hashlib.sha256((key + API_SECRET).encode()).hexdigest()
    return hashed.startswith("0000")

if __name__ == "__main__":
    key = sys.argv[1]
    if validate(key):
        sys.exit(0)
    else:
        sys.exit(1)
