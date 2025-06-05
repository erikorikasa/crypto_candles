from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle


class MEXCAPIError(Exception):
    """Custom exception for MEXC API errors."""
    pass


class MEXCExchange(BaseExchange):
    """MEXC exchange implementation using requests."""

    BASE_URL = "https://api.mexc.com/api/v3"

    def __init__(self):
        """Initialize MEXC client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "60m",
            "4h": "4h",
            "1d": "1d",
            "1w": "1W",
            "1M": "1M",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to MEXC API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            MEXCAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise MEXCAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert standard timeframe to MEXC format."""
        if timeframe not in self._supported_timeframes:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return self._supported_timeframes[timeframe]

    def _convert_symbol(self, symbol: str) -> str:
        """Convert standard symbol format to MEXC format."""
        # Convert from BTC-BRL to BTCBRL
        return symbol.replace("-", "").upper()

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from MEXC."""
        try:
            # Convert timeframe to MEXC format
            mexc_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to MEXC format
            mexc_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            # Make request to MEXC API
            response = self._make_request(
                "GET",
                "klines",
                params={
                    "symbol": mexc_symbol,
                    "interval": mexc_timeframe,
                    "startTime": start_ms,
                    "endTime": end_ms,
                },
            )
            
            # Parse response
            candles = []
            for candle_data in response:
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(candle_data[0]) / 1000),
                    open=float(candle_data[1]),
                    high=float(candle_data[2]),
                    low=float(candle_data[3]),
                    close=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    quote_volume=float(candle_data[7]),
                    symbol=symbol,
                    exchange="mexc",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise MEXCAPIError(f"Error getting candles from MEXC: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs with BRL as quote currency."""
        try:
            response = self._make_request("GET", "exchangeInfo")
            # print(response)
            pairs = []
            for symbol_data in response["symbols"]:
                
                if symbol_data["status"] == "1" and symbol_data["quoteAsset"] == "BRL":
                    
                    # Convert from BTCBRL to BTC-BRL format
                    symbol = f"{symbol_data['baseAsset']}-{symbol_data['quoteAsset']}"
                    pairs.append(symbol)
            return sorted(pairs)
        except Exception as e:
            raise MEXCAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 