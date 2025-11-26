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
    return False


def check_nessie():
    """Check Nessie availability."""
    uri = os.getenv("ICEBERG_CATALOG_URI", "http://localhost:19120/api/v1")
    try:
        response = requests.get(f"{uri}/config", timeout=5)
        if response.status_code == 200:
            print("✓ Nessie catalog is running")
            return True
    except:
        pass
    print("✗ Nessie catalog is not accessible")
    return False


def main():
    print("=== Service Health Check ===\n")
    minio_ok = check_minio()
    nessie_ok = check_nessie()

    print("\n" + "=" * 30)
    if minio_ok and nessie_ok:
        print("✓ All services ready")
        sys.exit(0)
    else:
        print("✗ Some services unavailable")
        sys.exit(1)


if __name__ == "__main__":
    main()
