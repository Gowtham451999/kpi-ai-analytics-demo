import pandas as pd

df = pd.read_csv("data/events.csv")

# Total users who signed up
total_users = df[df["event"] == "signup"]["user_id"].nunique()

# Users who came back (active)
active_users = df[df["event"] == "active"]["user_id"].nunique()

retention_rate = round((active_users / total_users) * 100, 2)

print("----- KPI METRICS -----")
print("Total Users:", total_users)
print("Active Users:", active_users)
print("Retention Rate:", retention_rate, "%")
