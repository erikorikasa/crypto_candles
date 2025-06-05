from datetime import datetime
from typing import List, Optional
import requests

from .base import BaseExchange
from ..models.candle import Candle
import pandas as pd


class MercadoBitcoinAPIError(Exception):
    """Custom exception for Mercado Bitcoin API errors."""
    pass


class MercadoBitcoinExchange(BaseExchange):
    """Mercado Bitcoin exchange implementation using requests."""

    BASE_URL = "https://api.mercadobitcoin.net/api/v4"

    def __init__(self):
        """Initialize Mercado Bitcoin client."""
        super().__init__()
        self._supported_timeframes = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make HTTP request to Mercado Bitcoin API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            MercadoBitcoinAPIError: If API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        if params is None:
            params = {}

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise MercadoBitcoinAPIError(f"API request failed: {str(e)}")

    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert timeframe to Mercado Bitcoin format."""
        # Mercado Bitcoin uses the same timeframe format as our standard
        return timeframe

    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol to Mercado Bitcoin format."""
        # Convert from BTC-BRL to BTC
        return symbol

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Candle]:
        """Get candles from Mercado Bitcoin."""
        try:
            # Convert timeframe to Mercado Bitcoin format
            mb_timeframe = self._convert_timeframe(timeframe)
            
            # Convert symbol to Mercado Bitcoin format
            mb_symbol = self._convert_symbol(symbol)
            
            # Convert datetime to Unix timestamp
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            # Make request to Mercado Bitcoin API
            response = self._make_request(
                "GET",
                f"candles",
                params={
                    "from": start_ts,
                    "to": end_ts,
                    "resolution": mb_timeframe,
                    "symbol": mb_symbol,
                },
            )
            
            # Parse response
            candles = []
            timestamps = response.get("t", [])
            opens = response.get("o", [])
            highs = response.get("h", [])
            lows = response.get("l", [])
            closes = response.get("c", [])
            volumes = response.get("v", [])
            
            for i in range(len(timestamps)):
                candle = Candle(
                    timestamp=datetime.fromtimestamp(int(timestamps[i])),
                    open=float(opens[i]),
                    high=float(highs[i]),
                    low=float(lows[i]),
                    close=float(closes[i]),
                    volume=float(volumes[i]),
                    quote_volume=float(volumes[i]),  # Using volume as quote_volume
                    symbol=symbol,
                    exchange="mercado_bitcoin",
                    timeframe=timeframe,
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            raise MercadoBitcoinAPIError(f"Error getting candles from Mercado Bitcoin: {str(e)}")

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported trading pairs as quote currency."""
        try:
            response = self._make_request("GET", "symbols")
            response_df = pd.DataFrame.from_records(response)
            pairs = response_df[(response_df['type'] == 'CRYPTO')]['symbol'].tolist()
            return sorted(pairs)
        except Exception as e:
            raise MercadoBitcoinAPIError(f"Failed to fetch supported pairs: {str(e)}")

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self._supported_timeframes.keys()) 