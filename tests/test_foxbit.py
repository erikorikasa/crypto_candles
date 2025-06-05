from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock

from crypto_candles.exchanges import FoxbitExchange
from crypto_candles.models.candle import Candle


@pytest.fixture
def mock_requests():
    with patch("requests.request") as mock:
        yield mock


@pytest.fixture
def foxbit_exchange(mock_requests):
    return FoxbitExchange(api_key="test_key", api_secret="test_secret")


def test_get_candles(foxbit_exchange, mock_requests):
    # Mock response data
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "timestamp": 1625097600000,
                "open": "35000.0",
                "high": "36000.0",
                "low": "34000.0",
                "close": "35500.0",
                "volume": "100.0",
                "quoteVolume": "3500000.0"
            }
        ]
    }
    mock_requests.return_value = mock_response

    # Test get_candles
    candles = foxbit_exchange.get_candles(
        symbol="BTC-BRL",
        timeframe="1h",
        since=datetime.now() - timedelta(hours=1),
        limit=1
    )

    # Verify results
    assert len(candles) == 1
    candle = candles[0]
    assert isinstance(candle, Candle)
    assert candle.symbol == "BTC-BRL"
    assert candle.exchange == "foxbit"
    assert candle.timeframe == "1h"
    assert candle.open == 35000.0
    assert candle.high == 36000.0
    assert candle.low == 34000.0
    assert candle.close == 35500.0
    assert candle.volume == 100.0
    assert candle.quote_volume == 3500000.0

    # Verify request was made correctly
    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    assert args[0] == "GET"
    assert "candles" in args[1]
    assert kwargs["params"]["symbol"] == "btc"
    assert kwargs["params"]["interval"] == "1h"


def test_invalid_symbol(foxbit_exchange):
    with pytest.raises(ValueError, match="Unsupported symbol"):
        foxbit_exchange.get_candles("INVALID-BRL")


def test_invalid_timeframe(foxbit_exchange):
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        foxbit_exchange.get_candles("BTC-BRL", timeframe="invalid")


def test_get_supported_pairs(foxbit_exchange):
    pairs = foxbit_exchange.get_supported_pairs()
    assert isinstance(pairs, list)
    assert "BTC-BRL" in pairs
    assert "ETH-BRL" in pairs
    assert len(pairs) > 0


def test_get_supported_timeframes(foxbit_exchange):
    timeframes = foxbit_exchange.get_supported_timeframes()
    assert isinstance(timeframes, list)
    assert "1h" in timeframes
    assert "1d" in timeframes


def test_api_error_handling(foxbit_exchange, mock_requests):
    # Mock API error
    mock_requests.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="Failed to fetch candles"):
        foxbit_exchange.get_candles("BTC-BRL") 