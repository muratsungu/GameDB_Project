"""Check if required services are running."""
import os
import sys

import requests


def check_minio():
    """Check MinIO availability."""
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    try:
        response = requests.get(f"{endpoint}/minio/health/live", timeout=5)
        if response.status_code == 200:
            print("✓ MinIO is running")
            return True
    except:
        pass
    print("✗ MinIO is not accessible")
    print("  Start with: docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data")
    return False


def main():
    print("=== Service Health Check ===\n")
    minio_ok = check_minio()

    print("\n" + "=" * 30)
    if minio_ok:
        print("✓ Services ready")
        sys.exit(0)
    else:
        print("✗ MinIO not available")
        sys.exit(1)


if __name__ == "__main__":
    main()
