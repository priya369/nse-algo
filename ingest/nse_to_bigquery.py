from nselib import capital_market
from google.cloud import bigquery
import pandas as pd
import os


def fetch_nse_data(symbol: str, from_date: str, to_date: str) -> pd.DataFrame:

    df = capital_market.price_volume_and_deliverable_position_data(
        symbol=symbol,
        from_date=from_date,
        to_date=to_date
    )

    # Keep only EQ series
    df = df[df["Series"] == "EQ"].copy()

    # Select and rename required columns
    df = df[
        [
            "Symbol",
            "Date",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "TotalTradedQuantity",
            "%DlyQttoTradedQty"
        ]
    ].copy()

    df = df.rename(
        columns={
            "OpenPrice": "open",
            "HighPrice": "high",
            "LowPrice": "low",
            "ClosePrice": "close",
            "TotalTradedQuantity": "volume",
            "%DlyQttoTradedQty": "delivery_percentage"
        }
    )

    # Data types
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d-%b-%Y"
    ).dt.date

    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="coerce"
    ).astype("Int64")

    df["delivery_percentage"] = pd.to_numeric(
        df["delivery_percentage"],
        errors="coerce"
    )

    return df


def load_to_bigquery(df: pd.DataFrame):

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

    print(f"Loaded {len(df)} rows into {table_ref}")


def main():

    symbol = os.environ.get("SYMBOL", "KFINTECH")
    from_date = os.environ.get("FROM_DATE", "01-01-2023")
    to_date = os.environ.get("TO_DATE", "31-01-2026")

    print(
        f"Fetching {symbol} data "
        f"from {from_date} to {to_date}"
    )

    df = fetch_nse_data(
        symbol=symbol,
        from_date=from_date,
        to_date=to_date
    )

    print(f"EQ records found: {len(df)}")

    if df.empty:
        print("No EQ records found.")
        return

    print(df.head())

    load_to_bigquery(df)


if __name__ == "__main__":
    main()
