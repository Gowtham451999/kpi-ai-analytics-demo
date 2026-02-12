import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

os.makedirs("data", exist_ok=True)

num_users = 500
rows = []

start_date = datetime(2024, 1, 1)

for user in range(1, num_users+1):
    signup_date = start_date + timedelta(days=random.randint(0, 10))
    variant = random.choice(["A", "B"])

    rows.append([user, signup_date, "signup", variant])

    for day in range(1, 7):
        if random.random() < 0.6:
            rows.append([user, signup_date + timedelta(days=day), "active", variant])

df = pd.DataFrame(rows, columns=["user_id", "timestamp", "event", "variant"])

df.to_csv("data/events.csv", index=False)

print("Test data created at data/events.csv")
