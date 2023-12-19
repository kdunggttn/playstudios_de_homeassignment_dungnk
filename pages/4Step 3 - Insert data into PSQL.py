import streamlit as st
import pandas as pd
import asyncio
from prisma import Prisma


@st.cache_data
def read_prisma_schema():
    f = open("prisma/schema.prisma", "r")
    return f.read()


async def main():
    ##############################
    # Page config
    ##############################
    title = "Step 3 - Insert data into PSQL | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Step 3: Insert data into PostgreSQL with Prisma ORM")

    if "spins_hourly_validated" and "purchases_validated" not in st.session_state:
        st.error(
            """
        You need to have uploaded the XLSX file in Step 1, and processed them in Step 2 first.   
        """
        )
        st.stop()

    # Connect to PSQL using Prisma ORM
    prisma = Prisma()
    await prisma.connect()
    if prisma.is_connected():
        st.success("Connected to PostgreSQL database.")

    with st.expander("See Prisma ORM schema"):
        st.code(read_prisma_schema())

    st.write("Here we have the tables containing the validated data in Step 2:")

    spins_hourly_validated_df: pd.DataFrame = st.session_state.spins_hourly_validated
    purchases_validated_df: pd.DataFrame = st.session_state.purchases_validated

    with st.expander("See validated data"):
        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_validated_df)
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_validated_df)

    st.subheader("1. Insert data into spins_hourly table")
    st.write("Firstly, we insert data into table `spins_hourly`:")
    # Insert data into spins_hourly table
    await prisma.spins_hourly.delete_many()
    res1 = await prisma.spins_hourly.create_many(
        spins_hourly_validated_df.to_dict("records")
    )
    st.success(f"Inserted {res1} rows into `spins_hourly` table.")

    st.subheader("2. Insert data into purchases table")
    st.write("Next, we insert data into table `purchases`:")
    # Insert data into purchases table
    await prisma.purchases.delete_many()
    res2 = await prisma.purchases.create_many(purchases_validated_df.to_dict("records"))
    st.success(f"Inserted {res2} rows into `purchases` table.")

    st.subheader("3. Verify if data is inserted successfully via SQL")
    spins_hourly_get_all_sql = """SELECT * FROM spins_hourly;"""
    st.code(spins_hourly_get_all_sql)
    with st.expander("See spins_hourly table from DB"):
        spins_hourly_from_db_df = await prisma.query_raw(spins_hourly_get_all_sql)
        spins_hourly_from_db_df = pd.DataFrame(spins_hourly_from_db_df)
        st.write(spins_hourly_from_db_df)
    purchases_get_all_sql = """SELECT * FROM purchases;"""
    st.code(purchases_get_all_sql)
    with st.expander("See purchases table from DB"):
        purchases_from_db_df = await prisma.query_raw(purchases_get_all_sql)
        purchases_from_db_df = pd.DataFrame(purchases_from_db_df)
        st.write(purchases_from_db_df)

    st.write(
        "Before concluding this step, we need to save the data pulled from PSQL to st.session_state:"
    )
    # Save spins_hourly_df
    st.session_state.spins_hourly_from_db: pd.DataFrame = spins_hourly_from_db_df
    # Compare the two DataFrames to ensure they are the same
    if st.session_state.spins_hourly_from_db.compare(spins_hourly_from_db_df).empty:
        st.success(
            "Saved `spins_hourly_from_db_df` to st.session_state.spins_hourly_from_db successfully!"
        )
    # Save purchases_df
    st.session_state.purchases_from_db = purchases_from_db_df
    # Compare the two DataFrames to ensure they are the same
    if st.session_state.purchases_from_db.compare(purchases_from_db_df).empty:
        st.success(
            "Saved `purchases_from_db_df` to st.session_state.purchases_from_db successfully!"
        )

    st.write(
        """
        We have successfully inserted data into the database. From now on, we will only use the data pulled from PSQL.
        For the next step, we will aggregate the data, and save it to the `aggregated` table.

        Let's move on to Step 4 when you're ready.
        """
    )


if __name__ == "__main__":
    asyncio.run(main())
