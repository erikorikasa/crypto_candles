from datetime import datetime, timedelta
from typing import Dict, Optional

# Common timeframe mappings
TIMEFRAME_MAPPINGS: Dict[str, Dict[str, int]] = {
    "1m": {"minutes": 1},
    "3m": {"minutes": 3},
    "5m": {"minutes": 5},
    "15m": {"minutes": 15},
    "30m": {"minutes": 30},
    "1h": {"hours": 1},
    "2h": {"hours": 2},
    "4h": {"hours": 4},
    "6h": {"hours": 6},
    "8h": {"hours": 8},
    "12h": {"hours": 12},
    "1d": {"days": 1},
    "3d": {"days": 3},
    "1w": {"weeks": 1},
    "1M": {"days": 30},  # Approximate month
}


def get_timeframe_delta(timeframe: str) -> timedelta:
    """
    Convert timeframe string to timedelta.

    Args:
        timeframe: Timeframe string (e.g., "1h", "1d")

    Returns:
        timedelta object representing the timeframe

    Raises:
        ValueError: If timeframe is not supported
    """
    if timeframe not in TIMEFRAME_MAPPINGS:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    return timedelta(**TIMEFRAME_MAPPINGS[timeframe])


def calculate_start_time(
    end_time: datetime, timeframe: str, num_candles: int
) -> datetime:
    """
    Calculate start time based on end time, timeframe, and number of candles.

    Args:
        end_time: End time for the calculation
        timeframe: Timeframe string (e.g., "1h", "1d")
        num_candles: Number of candles to calculate for

    Returns:
        Start time datetime
    """
    delta = get_timeframe_delta(timeframe)
    return end_time - (delta * num_candles)


def validate_timeframe(timeframe: str) -> bool:
    """
    Validate if the timeframe is supported.

    Args:
        timeframe: Timeframe string to validate

    Returns:
        True if timeframe is supported, False otherwise
    """
    return timeframe in TIMEFRAME_MAPPINGS 