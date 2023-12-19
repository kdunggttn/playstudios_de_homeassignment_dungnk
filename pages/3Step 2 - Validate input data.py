import streamlit as st
import pandas as pd
from price_parser.parser import Price


##############################
# Helper functions
##############################
@st.cache_data
def parse_datetime(column: pd.Series):
    """
    Firstly, try to parse the datetime column with the format `YYYY-MM-DD HH:MM:SS`.

    Secondly, try to parse it with the format `YYYY/MM/DD HH:MM:SS`.

    Finally, try to infer the datetime format.

    Usage:
    ```
    df[date_column] = parse_datetime(df[date_column])
    ```
    """
    column = pd.to_datetime(column, format="%Y-%m-%d %H:%M:%S", errors="coerce").fillna(
        pd.to_datetime(column, format="%Y/%m/%d %H:%M:%S", errors="coerce")
    )
    return column


@st.cache_data
def parse_currency(revenue_str: str):
    return Price.fromstring(revenue_str).currency


@st.cache_data
def parse_revenue(revenue_str: str):
    return Price.fromstring(revenue_str).amount_float


@st.cache_data
def strip_whitespace(df: pd.DataFrame):
    """
    Only strip whitespaces for columns that are of type `object` and not the `date` column,
    i.e. the column contains string values.
    """
    for column in df.columns:
        if column != "date" and df[column].dtype == "object":
            df[column] = df[column].str.strip()
    return df


def main():
    ##############################
    # Page config
    ##############################
    title = (
        "Step 2: Validate input data | PlayStudios - DE Home Assignment - Daniel Nguyen"
    )
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Step 2: Validate and clean input data")

    if "spins_hourly" and "purchases" not in st.session_state:
        st.error(
            """
        You need to have uploaded the XLSX file in Step 1 first.   
        """
        )
        st.stop()

    st.write("Here we have the tables containing the raw data we uploaded in Step 1:")

    spins_hourly_df: pd.DataFrame = st.session_state.spins_hourly
    purchases_df: pd.DataFrame = st.session_state.purchases

    with st.expander("See raw data"):
        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_df)
        st.write("Count: ", spins_hourly_df.shape[0])
        st.write(spins_hourly_df.dtypes)
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_df)
        st.write("Count: ", purchases_df.shape[0])
        st.write(purchases_df.dtypes)

    st.subheader("1. Deduplicate")
    st.write("First, we need to deduplicate the data on both tables:")
    with st.expander("""See tables after deduplication"""):
        # Deduplicate the data
        spins_hourly_df["total_spins"] = spins_hourly_df["total_spins"].astype(float)
        spins_hourly_df = spins_hourly_df.groupby(
            ["date", "userId", "country"], as_index=False
        ).sum()
        purchases_df.drop_duplicates("transaction_id", inplace=True)

        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_df)
        st.write("Count: ", spins_hourly_df.shape[0])
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_df)
        st.write("Count: ", purchases_df.shape[0])

        st.write(
            """
            We can see that both tables have duplicates. 
            
            For `Spins Hourly` table, there are 2 duplicates with the same `date`, `userId`, and `country` values.
            Since the duplicates have different `total_spins` values, and these 2 events may have happened during the same
            timeframe (albeit at different times), I just summed them up to get the total spins for that user during that hour.

            For `Purchases` table, there are 2 duplicates with the same `transaction_id` values. I have removed the duplicates
            using the unique ID key `transaction_id`.
        """
        )

    st.subheader("2. Validate dates")
    st.write(
        "Next, we have to conform the `date` columns to the chosen standard format `YYYY-MM-DD HH:MM:SS`:"
    )
    with st.expander("""See `date` columns after parsing"""):
        # Parse the date column
        spins_hourly_df["date"] = parse_datetime(spins_hourly_df["date"])
        purchases_df["date"] = parse_datetime(purchases_df["date"])

        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_df)
        st.write(spins_hourly_df.dtypes)
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_df)
        st.write(purchases_df.dtypes)

        st.write(
            """
            We can see that the `date` column is now in the correct format, with the data type
            `datetime64[ns]`.   
        """
        )

    st.subheader("3. Cast total_spins to int")
    st.write(
        "For the `total_spins` column of the `Spins Hourly` table, we need to round the values to the nearest integer:"
    )
    with st.expander("""See `total_spins` column after validating"""):
        # Round the total_spins column
        spins_hourly_df["total_spins"] = (
            spins_hourly_df["total_spins"].astype(float).round(0).astype(int)
        )

        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_df)
        st.write(spins_hourly_df.dtypes)

        st.write(
            """
            We can see that the `total_spins` column is now of type `int`.   
        """
        )

    st.subheader("4. Extract revenue amount and currency")
    st.write(
        "For the `revenue` column of the `Purchases` table, we need to extract the price and currency:"
    )
    with st.expander("""See `revenue` column after validating"""):
        # Extract the price and currency
        purchases_df["currency"] = purchases_df.apply(
            lambda row: parse_currency(row["revenue"]), axis=1
        )
        purchases_df["amount"] = purchases_df.apply(
            lambda row: parse_revenue(row["revenue"]), axis=1
        )

        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_df)
        st.write(purchases_df.dtypes)

        st.write(
            """
            We can see that the `price` column is now of type `float64` and the `currency` column
            is of type `object`, with the correct values in both of these columns.   
        """
        )

    st.subheader("5. Strip whitespaces and rename columns")
    st.write(
        "Lastly, we need to strip all whitespaces (for precaution), and change the column names to prepare the data for Step 3:"
    )
    with st.expander("""See column names after validating"""):
        # Strip whitespaces
        spins_hourly_df = strip_whitespace(spins_hourly_df)
        purchases_df = strip_whitespace(purchases_df)

        # Rename the columns
        spins_hourly_df.rename(
            columns={"userId": "user_id"},
            inplace=True,
        )
        del purchases_df["revenue"]
        purchases_df.rename(
            columns={"userId": "user_id", "amount": "revenue"}, inplace=True
        )

        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_df)
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_df)

        st.write(
            """
            We can see that the column names are now in sync with the table schemas on PSQL.   
        """
        )

    st.write(
        "Before concluding this step, we need to save the validated data to st.session_state:"
    )
    # Save spins_hourly_df
    st.session_state.spins_hourly_validated: pd.DataFrame = spins_hourly_df
    # Compare the two DataFrames to ensure they are the same
    if st.session_state.spins_hourly_validated.compare(spins_hourly_df).empty:
        st.success(
            "Saved `spins_hourly_df` to st.session_state.spins_hourly_validated successfully!"
        )
    # Save purchases_df
    st.session_state.purchases_validated = purchases_df
    # Compare the two DataFrames to ensure they are the same
    if st.session_state.purchases_validated.compare(purchases_df).empty:
        st.success(
            "Saved `purchases_df` to st.session_state.purchases_validated successfully!"
        )

    st.write(
        """
        We have now validated and cleaned the data. In the next step, we will save the data to a PostgreSQL database.
        
        Let's move on to Step 3 when you're ready.
        """
    )


if __name__ == "__main__":
    main()
