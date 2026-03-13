"""
Tests for health_score.py
Run with: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from health_score import (
    score_usage,
    score_engagement,
    score_support,
    score_nps,
    score_onboarding,
    score_ai_interest,
    get_risk_label,
    calculate_health_score,
)


# ---------------------------------------------------------------------------
# Individual scorer tests
# ---------------------------------------------------------------------------

def test_score_usage_high():
    assert score_usage(90) == 100

def test_score_usage_medium():
    assert score_usage(55) == 50

def test_score_usage_low():
    assert score_usage(10) == 0

def test_score_engagement_very_recent():
    assert score_engagement(3) == 100

def test_score_engagement_stale():
    assert score_engagement(90) == 0

def test_score_support_no_issues():
    assert score_support(0, 0) == 100

def test_score_support_many_issues():
    result = score_support(10, 5)
    assert result == 0  # maxes out at 0 with heavy ticket load

def test_score_nps_perfect():
    assert score_nps(10) == 100

def test_score_nps_detractor():
    assert score_nps(2) == 20

def test_score_onboarding_complete():
    assert score_onboarding("yes") == 100

def test_score_onboarding_incomplete():
    assert score_onboarding("no") == 0

def test_score_ai_interest_adopted():
    assert score_ai_interest("adopted") == 100

def test_score_ai_interest_in_pilot():
    assert score_ai_interest("in_pilot") == 75

def test_score_ai_interest_interested():
    assert score_ai_interest("interested") == 50

def test_score_ai_interest_none():
    assert score_ai_interest("none") == 0

def test_score_ai_interest_unknown():
    assert score_ai_interest("something_random") == 0


# ---------------------------------------------------------------------------
# Risk label tests
# ---------------------------------------------------------------------------

def test_risk_green():
    assert get_risk_label(80) == "Green"

def test_risk_yellow():
    assert get_risk_label(60) == "Yellow"

def test_risk_red():
    assert get_risk_label(40) == "Red"

def test_risk_boundary_green():
    assert get_risk_label(75) == "Green"

def test_risk_boundary_yellow():
    assert get_risk_label(50) == "Yellow"


# ---------------------------------------------------------------------------
# Composite score test
# ---------------------------------------------------------------------------

def test_healthy_client_scores_high():
    client = {
        "monthly_usage_pct": "90",
        "days_since_last_contact": "3",
        "open_tickets": "0",
        "escalations_last_90d": "0",
        "nps_score": "9",
        "onboarding_complete": "yes",
        "ai_interest": "adopted",
    }
    score, _ = calculate_health_score(client)
    assert score >= 85, f"Expected score >= 85, got {score}"

def test_atrisk_client_scores_low():
    client = {
        "monthly_usage_pct": "15",
        "days_since_last_contact": "90",
        "open_tickets": "8",
        "escalations_last_90d": "5",
        "nps_score": "2",
        "onboarding_complete": "no",
        "ai_interest": "none",
    }
    score, _ = calculate_health_score(client)
    assert score <= 20, f"Expected score <= 20, got {score}"
