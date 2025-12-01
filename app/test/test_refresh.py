import requests

BASE = "http://localhost:8000"

session = requests.Session()

#  Login → gets refresh_token #1
login_res = session.post(f"{BASE}/auth/login", json={
    "email": "user@example.com",
    "password": "stringst"
})
print("Login cookies:", session.cookies.get_dict())

old_token = session.cookies.get("refresh_token")   # Save OLD token
print("Old RT:", old_token)

#  Refresh → rotate → refresh_token #2 stored in session
refresh_res_1 = session.post(f"{BASE}/auth/refresh")
print("After refresh rotation:", session.cookies.get_dict())

# Now manually send OLD refresh token to simulate reuse
bad_cookie = {"refresh_token": old_token}
reuse_attack_res = requests.post(f"{BASE}/auth/refresh", cookies=bad_cookie)

print("Reuse attack response:", reuse_attack_res.status_code, reuse_attack_res.text)
