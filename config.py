BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"
POLL_INTERVAL_SECS = 10
SPREAD_ARB_THRESHOLD = 93        # yes_ask + no_ask <= this
WIDE_SPREAD_MIN_CENTS = 10       # Strategy 4
OB_IMBALANCE_THRESHOLD = 0.75   # Strategy 3
MEAN_REVERSION_MOVE_CENTS = 5   # Strategy 5
THETA_DAYS_TO_CLOSE = 3         # Strategy 6
THETA_MIN_YES_PRICE = 90        # Strategy 6
MAX_MARKETS = 200
OB_SAMPLE_TOP_N = 30            # max orderbooks to fetch per cycle
DATA_STORE_WINDOW = 60          # rolling window size (polls)
LOW_VOLUME_THRESHOLD = 100      # Strategy 5: low volume cutoff
