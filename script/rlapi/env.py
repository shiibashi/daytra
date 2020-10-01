import os

HOST = os.environ.get("RLAPI_HOST", "127.0.0.1")
PORT = int(os.environ.get("RLAPI_PORT", "8000"))

if __name__ == "__main__":
    print(HOST)
    print(PORT)
