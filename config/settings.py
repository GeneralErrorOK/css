"""
Global settings for the Cybernet Scoring System.

For markup, refer to style/css.tcss stylesheet.
"""

"""
URL to GET
"""
SCOREBOARD_URL = "http://127.0.0.1:8000/api/scoreboard"

"""
Interval to (try to) refresh the scores in seconds.
"""
REFRESH_INTERVAL_S = 10

"""
Filename to use for the database (sqlite). This will be stored in ./db.

Warning: using DEV_SERVER_MODE (see below) the database will be wiped
at startup!
"""
DB_FILENAME = "scores.sqlite3"

"""
How many rounds to measure score trends for coloring the
service-score digits.
"""
TREND_LENGTH_ROUNDS = 5

"""
Thresholds for coloring the offensive scores.

During the last round, how much has
the score increased compared to average last <TREND_LENGTH_ROUNDS>?
Low means red, medium is orange, high is green!
"""
OFFENSIVE_SCORE_THRESHOLDS = {
    "low": 0,
    "medium": 75,
    "high": 95,
}

"""
Thresholds for coloring the defensive scores.

During the last round, how much has
the score increased compared to average last <TREND_LENGTH_ROUNDS>?
Low means green, medium is orange, high is red!
"""
DEFENSIVE_SCORE_THRESHOLDS = {
    "low": 0,
    "medium": 25,
    "high": 50,
}

"""
Development server mode

This appends /{num_samples}/{index_counter} to the SCOREBOARD_URL
to let the (development) server generate fake scores.

NUM_SAMPLES is the amount of subdevisions you would like the scores from the last
round of 2024 be interpolated by. Less samples means you go faster through the rounds.
The original game consisted of 158 rounds, so 158 is a good starting point.
"""
DEV_SERVER_MODE = True
NUM_SAMPLES = 158
