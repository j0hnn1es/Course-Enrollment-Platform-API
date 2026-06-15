import time
import httpx

BASE = "http://127.0.0.1:8000"

def wait_for_up(retries=15, delay=0.5):
    for i in range(retries):
        try:
            r = httpx.get(f"{BASE}/health", timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

if not wait_for_up():
    print("Server not available at", BASE)
    raise SystemExit(1)

email = "smoketest_user@example.com"
password = "TestPass123!"
payload = {"name": "Smoke Tester", "email": email, "password": password}

with httpx.Client() as client:
    print("Registering user...")
    r = client.post(f"{BASE}/auth/register", json=payload)
    print("Register status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

    if r.status_code not in (200, 201):
        print("Registration failed; aborting login test.")
        raise SystemExit(1)

    print("Logging in...")
    data = {"username": email, "password": password}
    r2 = client.post(f"{BASE}/auth/login", data=data)
    print("Login status:", r2.status_code)
    try:
        print(r2.json())
    except Exception:
        print(r2.text)

    if r2.status_code == 200:
        print("Smoke test succeeded: token received.")
    else:
        print("Smoke test failed: login unsuccessful.")
