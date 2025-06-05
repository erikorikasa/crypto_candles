from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class BybitAPIError(Exception):
    """Custom exception for Bybit API errors."""
    pass


class BybitExchange(BaseExchange):
    """Bybit exchange implementation using requests."""

    BASE_URL = "https://api.bybit.com/v5"

    def __init__(self):
        """Initialize Bybit client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1",
            "3m": "3",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "6h": "360",
            "12h": "720",
            "1d": "D",
            "1w": "W",
            "1M": "M",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Bybit API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            BybitAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise BybitAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to Bybit format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to Bybit format."""
        # Convert from BTC-BRL to BTCBRL
        return symbol.replace("-", "").upper()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Bybit."""
        try:
            # Convert timeframe to Bybit format
            bybit_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Bybit format
            bybit_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to Bybit API
            response = self._make_request(
                "GET",
                "market/kline",
                params={
                    "category": "spot",
                    "symbol": bybit_symbol,
                    "interval": bybit_timeframe,
                    "start": start_ms,
                    "end": end_ms,
                },
            )
            
            # Parse response
            candles = []
            for candle_data in response["result"]["list"]:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data[0]) / 1000),
                    open=float(candle_data[1]),
                    high=float(candle_data[2]),
                    low=float(candle_data[3]),
                    close=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    quote_volume=float(candle_data[6]),
                    symbol=symbol,
                    exchange="bybit",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise BybitAPIError(f"Error getting candles from Bybit: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs with BRL as quote currency."""
        try:
            response = self._make_request("GET", "market/instruments-info", params={"category": "spot"})
            pairs = []
            for symbol_data in response["result"]["list"]:
                # Only include pairs where quote currency is BRL
                if symbol_data['quoteCoin'] == 'BRL':
                    # Convert from BTCBRL to BTC-BRL format
                    symbol = f"{symbol_data['baseCoin']}-{symbol_data['quoteCoin']}"
                    pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise BybitAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 