"""Seeds DEMO data into a fresh deployment. Everything here is synthetic."""
import json, sys, urllib.request

API = sys.argv[1].rstrip("/")

def post(path, body=None):
    data = json.dumps(body).encode() if body is not None else b""
    req = urllib.request.Request(API + path, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode()

print(post("/api/v1/locations/seed"))
print(post("/api/v1/supply/seed"))

starts = ["2026-03-01", "2026-03-29", "2026-04-25", "2026-05-24",
          "2026-06-21", "2026-07-21", "2026-08-17", "2026-09-14"]
lengths = [28, 27, 29, 28, 30, 27, 28, 28]
for i, (d, n) in enumerate(zip(starts, lengths), 1):
    post("/api/v1/cycles/", {"id": f"demo-{i:03d}", "user_id": "demo_user",
                             "start_date": d + "T00:00:00", "cycle_length": n,
                             "period_length": 5, "flow_intensity": "medium"})
print("seeded 8 demo cycles for demo_user")
