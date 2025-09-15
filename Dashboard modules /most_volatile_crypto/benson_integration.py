"""
Benson integration stubs. You can import this to push candidates into
your Benson FastAPI or Redis queue. Not used directly by the tracker.
"""
import json, os, redis, requests

def push_to_redis(json_path="exports/volatile_candidates.json", redis_url="redis://localhost:6379/0", key="benson:volatile:candidates"):
    r = redis.from_url(redis_url)
    with open(json_path, "r") as f:
        payload = f.read()
    r.set(key, payload)
    return True

def post_webhook(json_path="exports/volatile_candidates.json", url="http://localhost:8000/api/volatility/candidates", api_key=None):
    with open(json_path, "r") as f:
        candidates = json.load(f)
    headers = {"Content-Type":"application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    requests.post(url, headers=headers, json={"candidates": candidates}, timeout=15)
    return True
