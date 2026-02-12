import os
import pandas as pd
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

DATA_PATH = "data/events.csv"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Anchor each user to signup_time (cohort start)
signup = df[df["event"] == "signup"][["user_id", "timestamp", "variant"]].copy()
signup = signup.rename(columns={"timestamp": "signup_time"})

# Join signup_time onto all events
df = df.merge(signup[["user_id", "signup_time"]], on="user_id", how="left")
df["days_since_signup"] = (df["timestamp"] - df["signup_time"]).dt.days

def day_retention(day: int) -> float:
    """Overall retention for exactly day N after signup."""
    total = signup["user_id"].nunique()
    retained = df[
        (df["event"] == "active") &
        (df["days_since_signup"] == day)
    ]["user_id"].nunique()
    return retained / total if total else 0.0

# -----------------------------
# DAY-LEVEL RETENTION (Overall)
# -----------------------------
d1 = day_retention(1)
d7 = day_retention(7)

print("\n----- DAY-LEVEL RETENTION -----")
print(f"D1 Retention: {round(d1 * 100, 2)}%")
print(f"D7 Retention: {round(d7 * 100, 2)}%")

# -----------------------------
# A/B D1 Retention + Lift
# -----------------------------
variants = sorted(signup["variant"].unique())
rows = []

for v in variants:
    cohort_users = signup[signup["variant"] == v]["user_id"]
    total_v = cohort_users.nunique()

    retained_v = df[
        (df["event"] == "active") &
        (df["days_since_signup"] == 1) &
        (df["user_id"].isin(cohort_users))
    ]["user_id"].nunique()

    retention_pct = round((retained_v / total_v) * 100, 2) if total_v else 0.0
    rows.append([v, int(total_v), int(retained_v), retention_pct])

ab = pd.DataFrame(rows, columns=["variant", "total_users", "retained_d1", "d1_retention_pct"])

print("\n----- A/B D1 RETENTION -----")
print(ab.to_string(index=False))

lift = None
p = None

if set(["A", "B"]).issubset(set(ab["variant"].values)):
    a = ab[ab["variant"] == "A"].iloc[0]
    b = ab[ab["variant"] == "B"].iloc[0]
    lift = round(b["d1_retention_pct"] - a["d1_retention_pct"], 2)
    print(f"\nVariant B Lift over A (D1): {lift}%")

    # Chi-square test on D1 retention (A vs B)
    contingency = [
        [int(a["retained_d1"]), int(a["total_users"] - a["retained_d1"])],
        [int(b["retained_d1"]), int(b["total_users"] - b["retained_d1"])],
    ]
    chi2, p, _, _ = chi2_contingency(contingency)
    print(f"Chi-square p-value (D1): {round(p, 4)}")
    print("Statistically significant" if p < 0.05 else "Not statistically significant")

# Save A/B artifact
ab_csv = os.path.join(OUTPUT_DIR, "ab_d1_retention.csv")
ab.to_csv(ab_csv, index=False)
print(f"\n✅ Saved: {ab_csv}")

# -----------------------------
# Retention Curve (D0–D7) Overall + by Variant
# -----------------------------
days = list(range(0, 8))

# D0 retention is 100% by definition (signup day)
overall_curve = [1.0] + [day_retention(d) for d in range(1, 8)]

# Variant curves
variant_curves = {}
for v in variants:
    cohort_users = signup[signup["variant"] == v]["user_id"]
    total_v = cohort_users.nunique()

    curve = [1.0]
    for d in range(1, 8):
        retained_v = df[
            (df["event"] == "active") &
            (df["days_since_signup"] == d) &
            (df["user_id"].isin(cohort_users))
        ]["user_id"].nunique()
        curve.append(retained_v / total_v if total_v else 0.0)

    variant_curves[v] = curve

# Save curve data
curve_df = pd.DataFrame({"day": days, "overall_retention": overall_curve})
for v in variants:
    curve_df[f"retention_{v}"] = variant_curves[v]

curve_csv = os.path.join(OUTPUT_DIR, "retention_curve.csv")
curve_df.to_csv(curve_csv, index=False)
print(f"✅ Saved: {curve_csv}")

# Plot curve
plt.figure()
plt.plot(curve_df["day"], curve_df["overall_retention"] * 100, marker="o", label="Overall")

for v in variants:
    plt.plot(curve_df["day"], curve_df[f"retention_{v}"] * 100, marker="o", label=f"Variant {v}")

plt.title("Retention Curve (D0–D7)")
plt.xlabel("Days Since Signup")
plt.ylabel("Retention (%)")
plt.xticks(days)
plt.grid(True, alpha=0.3)
plt.legend()

plot_path = os.path.join(OUTPUT_DIR, "retention_curve.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Saved: {plot_path}")

# -----------------------------
# Executive Summary Artifact
# -----------------------------
decision = "No significant difference yet"
if p is not None and p < 0.05:
    decision = "Variant B is better (statistically significant)"
elif lift is not None:
    decision = "Variant B shows lift, but not statistically significant"

summary_text = f"""
SUMMARY
Dataset: {DATA_PATH}
Users: {signup["user_id"].nunique()}
D1 retention: {round(d1*100, 2)}%
D7 retention: {round(d7*100, 2)}%
Lift (B vs A) on D1: {lift if lift is not None else "N/A"}%
p-value (D1): {round(p, 4) if p is not None else "N/A"}
Decision: {decision}

Artifacts:
- {ab_csv}
- {curve_csv}
- {plot_path}
""".strip()

summary_path = os.path.join(OUTPUT_DIR, "summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_text)

print(f"✅ Saved: {summary_path}")
