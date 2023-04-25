import httpx

res = httpx.get("http://127.0.0.1")
assert res.json()["ok"]
