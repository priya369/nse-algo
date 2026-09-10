from nselib import capital_market
from google.cloud import bigquery
import pandas as pd
import os
import time


SYMBOLS = [
    "SUNPHARMA",
    "DRREDDY",
    "CIPLA",
    "DIVISLAB",
    "MANKIND",
    "ALKEM",
    "BIOCON",
    "COHANCE",
    "MEDPLUS",
    "SYNGENE",
    "MAXHEALTH",
    "ABBOTINDIA",
    "APLLTD",
    "BLUEJET",
    "LUPIN",
    "PFIZER",
    "THYROCARE",
    "AKUMS",
    "ASTRAZEN",
    "ENTERO",
    "RAINBOW",
    "METROPOLIS",
    "ALIVUS",
    "MEDIASSIST",
    "HIKAL",
    "FINEORG",
    "AARTIDRUGS",
    "SANOFICONR",
    "AUROPHARMA",
    "WINDLAS",
    "LAXMIDENTL",
    "FDC",
    "MANIPALHOS",
    "INDOCO",
    "JLHL",
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
        to_date=to_date,
    )

    if df is None or df.empty:
        print(f"No data returned for {symbol}")
        return pd.DataFrame()

    # Remove accidental whitespace from column names
    df.columns = df.columns.astype(str).str.strip()

    # Handle Symbol column with BOM/encoding issue
    symbol_column = None

    for column in df.columns:
        cleaned_column = (
            str(column)
            .replace("\ufeff", "")
            .replace('"', "")
            .strip()
        )

        if cleaned_column.lower() == "symbol":
            symbol_column = column
            break

    if symbol_column is None:
        raise ValueError(
            f"Symbol column not found for {symbol}. "
            f"Available columns: {list(df.columns)}"
        )

    # Keep only EQ series
    if "Series" not in df.columns:
        raise ValueError(
            f"'Series' column not found for {symbol}. "
            f"Available columns: {list(df.columns)}"
        )

    df = df[df["Series"].astype(str).str.strip() == "EQ"].copy()

    if df.empty:
        print(f"No EQ records found for {symbol}")
        return pd.DataFrame()

    required_columns = [
        "Date",
        "OpenPrice",
        "HighPrice",
        "LowPrice",
        "ClosePrice",
        "TotalTradedQuantity",
        "%DlyQttoTradedQty",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns for {symbol}: {missing_columns}. "
            f"Available columns: {list(df.columns)}"
        )

    # Select required columns
    df = df[
        [
            symbol_column,
            "Date",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "TotalTradedQuantity",
            "%DlyQttoTradedQty",
        ]
    ].copy()

    # Rename columns
    df = df.rename(
        columns={
            symbol_column: "Symbol",
            "OpenPrice": "open",
            "HighPrice": "high",
            "LowPrice": "low",
            "ClosePrice": "close",
            "TotalTradedQuantity": "volume",
            "%DlyQttoTradedQty": "delivery_percentage",
        }
    )

    # Clean symbol
    df["Symbol"] = (
        df["Symbol"]
        .astype("string")
        .str.strip()
    )

    # Date conversion
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d-%b-%Y",
        errors="coerce",
    ).dt.date

    # Numeric columns
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "delivery_percentage",
    ]

    for column in numeric_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Volume as integer
    df["volume"] = df["volume"].astype("Int64")

    # Remove invalid dates
    df = df.dropna(subset=["Date"])

    # Remove duplicate Symbol + Date records
    df = df.drop_duplicates(
        subset=["Symbol", "Date"]
    )

    return df


def load_to_bigquery(
    df: pd.DataFrame,
    client: bigquery.Client,
    table_ref: str,
):
    if df.empty:
        return

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(
        df,
        table_ref,
        job_config=job_config,
    )

    job.result()

    print(
        f"Loaded {len(df)} rows into {table_ref}"
    )


def main():

    project_id = os.environ["GCP_PROJECT_ID"]
    dataset_id = os.environ["BQ_DATASET"]
    table_id = os.environ["BQ_TABLE"]

    from_date = os.environ.get(
        "FROM_DATE",
        "01-01-2023",
    )

    to_date = os.environ.get(
        "TO_DATE",
        "31-01-2026",
    )

    table_ref = (
        f"{project_id}."
        f"{dataset_id}."
        f"{table_id}"
    )

    client = bigquery.Client(
        project=project_id
    )

    print("=" * 60)
    print("NSE STOCK DATA INGESTION")
    print("=" * 60)

    print(f"Project     : {project_id}")
    print(f"Table       : {table_ref}")
    print(f"Stocks      : {len(SYMBOLS)}")
    print(f"From Date   : {from_date}")
    print(f"To Date     : {to_date}")
    print("=" * 60)

    all_data = []

    successful = []
    failed = []

    for symbol in SYMBOLS:

        try:

            df = fetch_nse_data(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
            )

            record_count = len(df)

            print(
                f"{symbol}: "
                f"{record_count} EQ records"
            )

            if df.empty:
                failed.append(symbol)
                continue

            all_data.append(df)
            successful.append(symbol)

            print(
                f"{symbol}: SUCCESS"
            )

        except Exception as error:

            print(f"{symbol}: FAILED")
            print(f"Error: {error}")
            failed.append(symbol)

        # Avoid hitting NSE too aggressively
        time.sleep(2)

    # Load everything in one BigQuery job
    if all_data:

        final_df = pd.concat(
            all_data,
            ignore_index=True,
        )

        # Final duplicate protection
        final_df = final_df.drop_duplicates(
            subset=["Symbol", "Date"]
        )

        print("\n" + "=" * 60)
        print("BIGQUERY LOAD")
        print("=" * 60)

        print(
            f"Total rows : {len(final_df)}"
        )

        load_to_bigquery(
            df=final_df,
            client=client,
            table_ref=table_ref,
        )

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(f"Total stocks      : {len(SYMBOLS)}")
    print(f"Successful stocks : {len(successful)}")
    print(f"Failed stocks     : {len(failed)}")
    print(f"Successful        : {successful}")
    print(f"Failed            : {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
