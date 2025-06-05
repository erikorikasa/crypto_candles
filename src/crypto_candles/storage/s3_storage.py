import os
from datetime import datetime
from typing import Optional

import boto3
import pandas as pd
from botocore.exceptions import ClientError


class S3Storage:
    """Class to handle S3 storage operations for candle data."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        partition_by_day: bool = False,
    ):
        """
        Initialize S3 storage handler.

        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key_id: AWS access key ID (optional, can use environment variables)
            aws_secret_access_key: AWS secret access key (optional, can use environment variables)
            region_name: AWS region name
            partition_by_day: Whether to partition data by day (default: False)
        """
        self.bucket_name = bucket_name
        self.partition_by_day = partition_by_day
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def _get_s3_key(self, df: pd.DataFrame, exchange: str, symbol: str) -> str:
        """
        Generate S3 key based on the data and partitioning strategy.

        Args:
            df: DataFrame containing candle data
            exchange: Exchange name
            symbol: Trading pair symbol

        Returns:
            S3 key string
        """
        # Get the first timestamp to determine year, month, and day
        first_timestamp = df["timestamp"].min()
        year = first_timestamp.strftime("%Y")
        month = first_timestamp.strftime("%m")
        
        if self.partition_by_day:
            day = first_timestamp.strftime("%d")
            return f"candles/year={year}/month={month}/day={day}/exchange={exchange}/symbol={symbol}/data.parquet"
        else:
            return f"candles/year={year}/month={month}/exchange={exchange}/symbol={symbol}/data.parquet"

    def store_candles(
        self,
        df: pd.DataFrame,
        exchange: str,
        symbol: str,
        overwrite: bool = False,
    ) -> bool:
        """
        Store candle data in S3 as Parquet file.

        Args:
            df: DataFrame containing candle data
            exchange: Exchange name
            symbol: Trading pair symbol
            overwrite: Whether to overwrite existing file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate S3 key
            s3_key = self._get_s3_key(df, exchange, symbol)

            # Check if file exists
            if not overwrite:
                try:
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                    print(f"File already exists: {s3_key}")
                    return False
                except ClientError:
                    pass  # File doesn't exist, proceed with upload

            # Convert DataFrame to Parquet
            parquet_buffer = df.to_parquet(index=False)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=parquet_buffer,
            )

            print(f"Successfully stored data in S3: {s3_key}")
            return True

        except Exception as e:
            print(f"Error storing data in S3: {str(e)}")
            return False

    def store_multiple_exchanges(
        self,
        dfs: dict[str, pd.DataFrame],
        symbol: str,
        overwrite: bool = False,
    ) -> dict[str, bool]:
        """
        Store candle data from multiple exchanges in S3.

        Args:
            dfs: Dictionary mapping exchange names to DataFrames
            symbol: Trading pair symbol
            overwrite: Whether to overwrite existing files

        Returns:
            Dictionary mapping exchange names to success status
        """
        results = {}
        for exchange, df in dfs.items():
            success = self.store_candles(df, exchange, symbol, overwrite)
            results[exchange] = success
        return results