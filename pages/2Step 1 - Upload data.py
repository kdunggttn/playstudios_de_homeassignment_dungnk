import streamlit as st
import pandas as pd


def main():
    ##############################
    # Page config
    ##############################
    title = "Step 1: Upload data | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Step 1: Upload XLSX containing Spins Hourly and Purchases")

    uploaded_file = st.file_uploader(
        "Choose an XLSX file", type="xlsx", key="xlsx_upload"
    )
    uploaded_file = (
        uploaded_file
        if uploaded_file is not None
        else st.session_state.uploaded_file_from_storage
        if "uploaded_file_from_storage" in st.session_state
        else None
    )

    if uploaded_file is not None:
        # Save the uploaded file to st.session_state to prevent reuploading on leaving page
        st.session_state.uploaded_file_from_storage = uploaded_file

        # Read the XLSX file into DataFrames and save to st.session_state
        spins_hourly = pd.read_excel(
            uploaded_file, sheet_name="Spins Hourly", usecols="A:D", dtype=str
        ).sort_values(by=["date", "userId"], ignore_index=True)
        st.session_state.spins_hourly = spins_hourly
        purchases = pd.read_excel(
            uploaded_file, sheet_name="Purchases", dtype=str
        ).sort_values(by=["date", "userId"], ignore_index=True)
        st.session_state.purchases = purchases

        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly)
        st.write(
            """
            We can see that the `total_spins` column is supposed to be of `::int` type, but it's currently
            `::float`. This is the first input we need to validate and convert to `::int` by rounding them up or down.
            """
        )

        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases)
        st.write(
            """
            Although the `date` column in the `Purchases` sheet had the format of `YYYY/MM/DD HH:MM:SS` in the xlsx file, 
            it was imported into pandas as `YYYY-MM-DD HH:MM:SS`. However, we need to always check the datetime format to ensure
            the timestamps we save into the database are in the correct format. Here I've chosen to use `YYYY-MM-DD HH:MM:SS`
            as standard.
            """
        )
        st.write(
            """
            The next column we need to normalize is the `revenue` column. Currently, the data is in the format of
            `PriceInUSD=0.00`. We need to extract the price from this string and convert it to `::float` type, as well
            as extract the currency. I'm going to use a Python library called [price-parser](https://pypi.org/project/price-parser/)
            to do this, as we might encounter unique cases in the future. The library also separates the currency and amount from
            the string for us.
            """
        )
        st.write(
            """
            We also need to deduplicate the data on both tables if there are any.

            Let's move on to Step 2 when you're ready.
            """
        )


if __name__ == "__main__":
    main()
