from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Candle:
    """Represents a single OHLCV candle."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    exchange: str
    timeframe: str
    quote_volume: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert candle to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "timeframe": self.timeframe,
            "quote_volume": self.quote_volume,
        } 