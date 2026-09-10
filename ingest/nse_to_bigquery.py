from nselib import capital_market
from google.cloud import bigquery
import pandas as pd
import os
import time


SYMBOLS = [
    "CIPLA",
    "DIVISLAB",
    "ALKEM",
    "BIOCON",
    "COHANCE",
    "SYNGENE",
    "BLUEJET",
    "LUPIN",
    "AKUMS",
    "RAINBOW",
    "HIKAL",
    "FINEORG",
    "AUROPHARMA",
    "WINDLAS",
    "FDC"
]


def fetch_nse_data(
    symbol: str,
    from_date: str,
    to_date: str
) -> pd.DataFrame:

    print(
        f"Fetching {symbol} "
        f"from {from_date} to {to_date}"
    )

    df = capital_market.price_volume_and_deliverable_position_data(
        symbol=symbol,
        from_date=from_date,
        to_date=to_date
    )

    if df.empty:
        print(f"No data returned for {symbol}")
        return pd.DataFrame()

    # Keep only EQ series
    df = df[df["Series"] == "EQ"].copy()

    if df.empty:
        print(f"No EQ records found for {symbol}")
        return pd.DataFrame()

    # Select required columns
    df = df[
        [
            'ï»¿"Symbol"',
            "Date",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "TotalTradedQuantity",
            "%DlyQttoTradedQty"
        ]
    ].copy()

    # Rename columns
    df = df.rename(
        columns={
            'ï»¿"Symbol"': "Symbol",
            "OpenPrice": "open",
            "HighPrice": "high",
            "LowPrice": "low",
            "ClosePrice": "close",
            "TotalTradedQuantity": "volume",
            "%DlyQttoTradedQty": "delivery_percentage"
        }
    )

    # Date conversion
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d-%b-%Y",
        errors="coerce"
    ).dt.date

    # Numeric columns
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "delivery_percentage"
    ]

    for col in numeric_columns:

        df[col] = (
            df[col]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Volume as integer
    df["volume"] = df["volume"].astype("Int64")

    return df


def load_to_bigquery(df: pd.DataFrame):

    if df.empty:
        return

    project_id = os.environ["GCP_PROJECT_ID"]
    dataset_id = os.environ["BQ_DATASET"]
    table_id = os.environ["BQ_TABLE"]

    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(
        df,
        table_ref,
        job_config=job_config
    )

    job.result()

    print(
        f"Loaded {len(df)} rows into {table_ref}"
    )


def main():
    from_date="01-01-2023"
    to_date="31-12-2026"
    print("=" * 60)
    print("NSE STOCK DATA INGESTION")
    print("=" * 60)

    print(f"Stocks      : {len(SYMBOLS)}")
    print(f"From Date   : {from_date}")
    print(f"To Date     : {to_date}")
    print("=" * 60)

    successful = []
    failed = []

    for symbol in SYMBOLS:

        try:

            df = fetch_nse_data(
                symbol=symbol,
                from_date="01-01-2023",
                to_date="31-12-2026"
            )

            print(
                f"{symbol}: "
                f"{len(df)} EQ records found"
            )

            if df.empty:
                failed.append(symbol)
                continue

            load_to_bigquery(df)

            successful.append(symbol)

            print(
                f"{symbol}: SUCCESS"
            )

        except Exception as e:

            print(
                f"{symbol}: FAILED - {str(e)}"
            )

            failed.append(symbol)

        # Small delay between NSE requests
        time.sleep(2)

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(
        f"Total stocks      : {len(SYMBOLS)}"
    )

    print(
        f"Successful stocks : {len(successful)}"
    )

    print(
        f"Failed stocks     : {len(failed)}"
    )

    print(
        f"Successful        : {successful}"
    )

    print(
        f"Failed            : {failed}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
