"""
Global settings for the Cybernet Scoring System.

For markup, refer to style/css.tcss stylesheet.
"""

"""
How many rounds to measure score trends for coloring the
service-score digits.
"""
TREND_LENGTH_ROUNDS = 3

"""
Thresholds for coloring the offensive scores.

During the last <TREND_LENGTH_ROUNDS> rounds, how much has
the score increased? Low means red, medium is orange, high is green!
"""
OFFENSIVE_SCORE_THRESHOLDS = {
    "low": 0,
    "medium": 2,
    "high": 5,
}

"""
Thresholds for coloring the defensive scores.

During the last <TREND_LENGTH_ROUNDS> rounds, how much has
the score increased? Low means green, medium is orange, high is red!
"""
DEFENSIVE_SCORE_THRESHOLDS = {
    "low": 0,
    "medium": 2,
    "high": 5,
}
