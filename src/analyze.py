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
# ---------------- A/B RETENTION COMPARISON ----------------

# Separate signup and active users by variant
signups = df[df["event"] == "signup"][["user_id", "variant"]].drop_duplicates()
active = df[df["event"] == "active"][["user_id", "variant"]].drop_duplicates()

variant_total = signups.groupby("variant")["user_id"].nunique()
variant_active = active.groupby("variant")["user_id"].nunique()

print("\n----- A/B RETENTION COMPARISON -----")

for variant in variant_total.index:
    total = variant_total[variant]
    active_count = variant_active.get(variant, 0)
    retention = round((active_count / total) * 100, 2)

    print(
        f"Variant {variant}: "
        f"Total Users = {total}, "
        f"Active Users = {active_count}, "
        f"Retention = {retention}%"
    )

# Calculate Lift
if "A" in variant_total.index and "B" in variant_total.index:
    lift = round(
        (variant_active.get("B", 0) / variant_total["B"] -
         variant_active.get("A", 0) / variant_total["A"]) * 100,
        2
    )
    print(f"\nVariant B Lift over A: {lift}%")
