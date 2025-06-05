from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..models.candle import Candle


class BaseExchange(ABC):
    """Base class for cryptocurrency exchanges."""

    def __init__(self):
        """Initialize exchange."""
        self._client = None

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """
        Get candles from the exchange.

        Args:
            symbol: Trading pair symbol (e.g., "BTC-BRL")
            timeframe: Candle timeframe (e.g., "1h", "1d")
            start_date: Start date for fetching candles
            end_date: End date for fetching candles

        Returns:
            List of Candle objects
        """
        pass

    @abstractmethod
    def get_supported_pairs(self) -> List[str]:
        """
        Get list of supported trading pairs.

        Returns:
            List of supported trading pair symbols
        """
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """
        Get list of supported timeframes.

        Returns:
            List of supported timeframe strings
        """
        pass

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if the symbol is supported by the exchange.

        Args:
            symbol: Trading pair symbol to validate

        Returns:
            True if symbol is supported, False otherwise
        """
        return symbol in self.get_supported_pairs()

    def validate_timeframe(self, timeframe: str) -> bool:
        """
        Validate if the timeframe is supported by the exchange.

        Args:
            timeframe: Timeframe to validate

        Returns:
            True if timeframe is supported, False otherwise
        """
        return timeframe in self.get_supported_timeframes() 