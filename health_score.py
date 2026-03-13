"""
Client Health Score Calculator
================================
Reads BPO client account data from a CSV, computes a weighted health score
for each account, and flags at-risk clients for CSM follow-up.

Built from experience managing multi-industry BPO accounts. The scoring model
reflects what actually matters in day-to-day CSM: are they using the product,
are we talking to them, are they happy, and is there room to grow the account?

Usage:
    python health_score.py
    python health_score.py --input data/clients.csv --output outputs/report.csv
    python health_score.py --threshold 60
"""

import csv
import os
import argparse
from datetime import datetime, date


# ---------------------------------------------------------------------------
# SCORING WEIGHTS  (must sum to 100)
# ---------------------------------------------------------------------------
# These weights reflect what I've found most predictive of churn risk in BPO.
# Usage and engagement are the early warning signals — when a client goes quiet
# or stops using the platform, something is usually wrong before they say it.
# AI interest was added to capture expansion potential, not just risk.
WEIGHTS = {
    "usage":       25,   # % of contracted capacity/features actually being used
    "engagement":  25,   # how recently we had a meaningful touchpoint
    "support":     20,   # open tickets + escalations in the last 90 days
    "nps":         15,   # net promoter score (0-10)
    "onboarding":   5,   # whether the client completed the onboarding process
    "ai_interest": 10,   # interest level in AI products we offer
}

RISK_THRESHOLDS = {
    "green":  75,   # healthy — monitor normally
    "yellow": 50,   # needs attention — schedule a check-in
    # below 50 = red — escalate to account review
}

# Maps ai_interest text values to a 0-100 score
AI_INTEREST_SCORES = {
    "adopted":    100,   # already using one of our AI products
    "in_pilot":    75,   # currently testing/piloting
    "interested":  50,   # had a discovery call or demo, showed interest
    "none":         0,   # no interest expressed yet
}


# ---------------------------------------------------------------------------
# INDIVIDUAL METRIC SCORERS  (each returns 0-100)
# ---------------------------------------------------------------------------

def score_usage(monthly_usage_pct):
    """Higher usage = healthier. A client not using what they're paying for is a churn risk."""
    pct = float(monthly_usage_pct)
    if pct >= 80:
        return 100
    elif pct >= 60:
        return 75
    elif pct >= 40:
        return 50
    elif pct >= 20:
        return 25
    else:
        return 0


def score_engagement(days_since_last_contact):
    """Fewer days since last contact = healthier. Silent clients are risky clients."""
    days = int(days_since_last_contact)
    if days <= 7:
        return 100
    elif days <= 14:
        return 80
    elif days <= 30:
        return 55
    elif days <= 60:
        return 25
    else:
        return 0


def score_support(open_tickets, escalations_last_90d):
    """Fewer tickets and escalations = healthier. Heavy support load usually signals product or ops issues."""
    tickets = int(open_tickets)
    escalations = int(escalations_last_90d)

    ticket_score = max(0, 100 - (tickets * 10))
    escalation_score = max(0, 100 - (escalations * 20))

    return (ticket_score + escalation_score) / 2


def score_nps(nps_score):
    """NPS is 0-10. Multiply by 10 to normalize to 0-100."""
    return float(nps_score) * 10


def score_onboarding(onboarding_complete):
    """Binary check. If onboarding never finished, the account started on shaky ground."""
    return 100 if str(onboarding_complete).strip().lower() == "yes" else 0


def score_ai_interest(ai_interest):
    """
    Measures interest or adoption of our AI product offerings.
    This is both a health signal (engaged clients explore new products)
    and an expansion indicator for upsell conversations.
    """
    key = str(ai_interest).strip().lower()
    return AI_INTEREST_SCORES.get(key, 0)


# ---------------------------------------------------------------------------
# COMPOSITE SCORE
# ---------------------------------------------------------------------------

def calculate_health_score(client):
    """
    Takes a dict (one CSV row) and returns a weighted health score (0-100)
    plus a breakdown of each individual dimension score.
    """
    scores = {
        "usage":       score_usage(client["monthly_usage_pct"]),
        "engagement":  score_engagement(client["days_since_last_contact"]),
        "support":     score_support(client["open_tickets"], client["escalations_last_90d"]),
        "nps":         score_nps(client["nps_score"]),
        "onboarding":  score_onboarding(client["onboarding_complete"]),
        "ai_interest": score_ai_interest(client["ai_interest"]),
    }

    weighted_total = sum(
        scores[metric] * (WEIGHTS[metric] / 100)
        for metric in scores
    )

    return round(weighted_total, 1), scores


def get_risk_label(score):
    if score >= RISK_THRESHOLDS["green"]:
        return "Green"
    elif score >= RISK_THRESHOLDS["yellow"]:
        return "Yellow"
    else:
        return "Red"


def days_until_renewal(contract_end_date):
    """Returns how many days until the contract end date."""
    end = datetime.strptime(contract_end_date, "%Y-%m-%d").date()
    return (end - date.today()).days


# ---------------------------------------------------------------------------
# REPORT GENERATION
# ---------------------------------------------------------------------------

def generate_report(input_path, output_path, risk_threshold):
    """
    Reads the client CSV, scores every account, prints a terminal summary,
    and saves a full scored report to CSV.
    """
    clients = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            score, breakdown = calculate_health_score(row)
            risk = get_risk_label(score)
            renewal_in = days_until_renewal(row["contract_end_date"])

            clients.append({
                "client_id":        row["client_id"],
                "client_name":      row["client_name"],
                "industry":         row["industry"],
                "contract_value":   row["contract_value"],
                "renewal_in_days":  renewal_in,
                "health_score":     score,
                "risk_label":       risk,
                "score_usage":      breakdown["usage"],
                "score_engagement": breakdown["engagement"],
                "score_support":    breakdown["support"],
                "score_nps":        breakdown["nps"],
                "score_onboarding": breakdown["onboarding"],
                "score_ai_interest":breakdown["ai_interest"],
                "ai_interest":      row["ai_interest"],
            })

    clients.sort(key=lambda x: x["health_score"])

    print_summary(clients, risk_threshold)

    save_report(clients, output_path)
    print(f"\nReport saved to: {output_path}")


def print_summary(clients, threshold):
    """Prints an at-a-glance summary to the terminal."""
    total = len(clients)
    at_risk = [c for c in clients if c["health_score"] < threshold]
    red    = [c for c in clients if c["risk_label"] == "Red"]
    yellow = [c for c in clients if c["risk_label"] == "Yellow"]
    green  = [c for c in clients if c["risk_label"] == "Green"]
    upsell = [c for c in clients if c["ai_interest"] in ("interested", "in_pilot")]

    print("\n" + "=" * 55)
    print("  CLIENT HEALTH SCORE REPORT")
    print(f"  Generated: {date.today()}")
    print("=" * 55)
    print(f"  Total accounts:   {total}")
    print(f"  Green  (>=75):    {len(green)}")
    print(f"  Yellow (50-74):   {len(yellow)}")
    print(f"  Red    (<50):     {len(red)}")
    print("=" * 55)

    if at_risk:
        print(f"\n  ACTION REQUIRED — {len(at_risk)} account(s) below {threshold}:\n")
        for c in at_risk:
            print(
                f"  [{c['risk_label']:6}] {c['client_name']:<25} "
                f"Score: {c['health_score']:5.1f}  "
                f"Renewal: {c['renewal_in_days']}d"
            )
    else:
        print("\n  All accounts are above threshold. No immediate action needed.")

    if upsell:
        print(f"\n  AI UPSELL PIPELINE — {len(upsell)} account(s) to follow up:\n")
        for c in upsell:
            print(
                f"  {c['client_name']:<25} "
                f"Status: {c['ai_interest']:<12} "
                f"Health: {c['health_score']:5.1f}"
            )

    print("\n  Full scores:\n")
    for c in clients:
        print(
            f"  {c['client_name']:<25} "
            f"{c['risk_label']:6}  "
            f"{c['health_score']:5.1f}"
        )
    print()


def save_report(clients, output_path):
    """Saves the full scored report to a CSV file."""
    if not clients:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = clients[0].keys()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clients)


# ---------------------------------------------------------------------------
# CLI ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="Calculate client health scores from a BPO account CSV export."
    )
    parser.add_argument(
        "--input",
        default=os.path.join(base_dir, "data", "clients.csv"),
        help="Path to the input CSV file (default: data/clients.csv)"
    )
    parser.add_argument(
        "--output",
        default=os.path.join(base_dir, "outputs", "health_report.csv"),
        help="Path for the output report CSV (default: outputs/health_report.csv)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=60.0,
        help="Score below which accounts are flagged for action (default: 60)"
    )

    args = parser.parse_args()
    generate_report(args.input, args.output, args.threshold)


if __name__ == "__main__":
    main()
