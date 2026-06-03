import os
import traceback
import httpx
from dotenv import load_dotenv
from supabase import create_client

print("=" * 50)
print("DEBUG SUPABASE")
print("=" * 50)

# Load .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("\n[1] Environment Variables")
print("URL :", repr(url))

if key:
    print("KEY :", key[:15] + "...")
else:
    print("KEY : None")

print("\n" + "=" * 50)

# Cek apakah env terbaca
if not url:
    print("ERROR: SUPABASE_URL tidak ditemukan")
    exit()

if not key:
    print("ERROR: SUPABASE_KEY tidak ditemukan")
    exit()

# ====================================================
# TEST 1 - HTTPX langsung
# ====================================================

print("\n[2] Test HTTPX Connection")

try:
    response = httpx.get(url, timeout=10)
    print("SUCCESS")
    print("Status Code:", response.status_code)

except Exception as e:
    print("FAILED")
    print("Type:", type(e))
    print("Error:", repr(e))

print("\n" + "=" * 50)

# ====================================================
# TEST 2 - Supabase Client
# ====================================================

print("\n[3] Create Supabase Client")

try:
    supabase = create_client(url, key)

    print("SUCCESS")
    print("Client berhasil dibuat")

except Exception as e:
    print("FAILED")
    print("Type:", type(e))
    print("Error:", repr(e))
    traceback.print_exc()
    exit()

print("\n" + "=" * 50)

# ====================================================
# TEST 3 - Query sederhana
# ====================================================

print("\n[4] Query Users Table")

try:
    result = (
        supabase
        .table("users")
        .select("*")
        .limit(1)
        .execute()
    )

    print("SUCCESS")
    print("Jumlah data:", len(result.data))

    if result.data:
        print("Sample Data:")
        print(result.data[0])

except Exception as e:
    print("FAILED")
    print("Type:", type(e))
    print("Error:", repr(e))
    traceback.print_exc()

print("\n" + "=" * 50)

# ====================================================
# TEST 4 - REST Endpoint Supabase
# ====================================================

print("\n[5] Test REST Endpoint")

try:
    rest_url = f"{url}/rest/v1/"

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }

    response = httpx.get(
        rest_url,
        headers=headers,
        timeout=10
    )

    print("SUCCESS")
    print("Status:", response.status_code)
    print("Response:")
    print(response.text[:500])

except Exception as e:
    print("FAILED")
    print("Type:", type(e))
    print("Error:", repr(e))

print("\n" + "=" * 50)
print("DEBUG SELESAI")
print("=" * 50)