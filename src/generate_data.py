import pandas as pd
from datetime import datetime, timedelta
import random
import os

os.makedirs("data", exist_ok=True)

num_users = 800
start_date = datetime(2026, 1, 1)

rows = []

# Simple retention curve: probability of being active decays by day
# Variant B gets a small lift.
base_day_probs = {
    1: 0.55,
    2: 0.45,
    3: 0.38,
    4: 0.32,
    5: 0.28,
    6: 0.25,
    7: 0.22,
}

for user_id in range(1, num_users + 1):
    signup_date = start_date + timedelta(days=random.randint(0, 10))
    variant = random.choice(["A", "B"])

    rows.append([user_id, signup_date, "signup", variant])

    for day in range(1, 8):
        p = base_day_probs[day]

        # give variant B a small lift
        if variant == "B":
            p += 0.03

        if random.random() < p:
            event_date = signup_date + timedelta(days=day)
            rows.append([user_id, event_date, "active", variant])

df = pd.DataFrame(rows, columns=["user_id", "timestamp", "event", "variant"])
df.to_csv("data/events.csv", index=False)

print("✅ Test data created at data/events.csv")
