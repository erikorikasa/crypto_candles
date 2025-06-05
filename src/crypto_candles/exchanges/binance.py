from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    pass


class BinanceExchange(BaseExchange):
    """Binance exchange implementation using requests."""

    BASE_URL = "https://api.binance.com"
    API_VERSION = "v3"

    def __init__(self):
        """Initialize Binance client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "6h": "6h",
            "8h": "8h",
            "12h": "12h",
            "1d": "1d",
            "3d": "3d",
            "1w": "1w",
            "1M": "1M",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Binance API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            BinanceAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/api/{self.API_VERSION}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise BinanceAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert timeframe to Binance format."""
        # Binance uses the same timeframe format as our standard
        return timeframe

    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol to Binance format."""
        # Convert from BTC-BRL to BTCBRL
        return symbol.replace("-", "").upper()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Binance."""
        try:
            # Convert timeframe to Binance format
            binance_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Binance format
            binance_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to Binance API
            response = self._make_request(
                "GET",
                "klines",
                params={
                    "symbol": binance_symbol,
                    "interval": binance_timeframe,
                    "startTime": start_ms,
                    "endTime": end_ms,
                },
            )
            
            # Parse response
            candles = []
            for candle_data in response:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(candle_data[0] / 1000),
                    open=float(candle_data[1]),
                    high=float(candle_data[2]),
                    low=float(candle_data[3]),
                    close=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    quote_volume=float(candle_data[7]),
                    symbol=symbol,
                    exchange="binance",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise BinanceAPIError(f"Error getting candles from Binance: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs."""
        try:
            exchange_info = self._make_request("GET", "exchangeInfo")
            return sorted([
                symbol["symbol"].replace("BRL", "-BRL")
                for symbol in exchange_info["symbols"]
                if symbol["symbol"].endswith("BRL") and symbol["status"] == "TRADING"
            ])
        except BinanceAPIError as e:
            raise BinanceAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 