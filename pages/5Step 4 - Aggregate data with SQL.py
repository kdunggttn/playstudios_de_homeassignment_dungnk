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
    title = "Step 4 - Aggregate data with SQL (Task #1) | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Step 4: Aggregate data on PSQL using SQL (Task #1)")

    if "spins_hourly_from_db" and "purchases_from_db" not in st.session_state:
        st.error(
            """
        You need to have uploaded the XLSX file in Step 1, processed them in Step 2, and inserted them to PSQL in Step 3 first.   
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

    st.write("Here we have the tables containing the data pulled from PSQL in Step 3:")

    spins_hourly_from_db_df: pd.DataFrame = st.session_state.spins_hourly_from_db
    purchases_from_db_df: pd.DataFrame = st.session_state.purchases_from_db

    with st.expander("See data from DB"):
        # Table 1: Spins Hourly
        st.caption("Table: Spins Hourly")
        st.write(spins_hourly_from_db_df)
        # Table 2: Purchases
        st.caption("Table: Purchases")
        st.write(purchases_from_db_df)

    st.write(
        """
    To calculate Total Daily Revenue per user, we need to find the hour of the day
    when the user made the purchase. For example, with the following purchase timestamp:
    `2022-04-01 10:16:26`, we need to transform it to `2022-04-01 10:00:00`, in order to join
    this purchase with the spins_hourly table. We can do this with the following SQL query:
    """
    )
    await prisma.query_raw("DROP TABLE IF EXISTS cte_purchases;")
    cte_purchases_query = """
        -- Truncate `date` column by "hour" to transform `2022-04-01 0:10:39` to `2022-04-01 00:00:00`
        -- Truncate `date` column by "day" to transform `2022-04-01 07:19:01` to `2022-04-01 00:00:00`
        SELECT * INTO TEMP TABLE cte_purchases FROM (
            SELECT 
                DATE_TRUNC('hour', date) AS date_trunc,
                DATE_TRUNC('day', date) AS day_trunc,
                p.user_id,
                p.revenue
            FROM purchases p
        );
    """
    st.code(cte_purchases_query, "sql")
    await prisma.query_raw(cte_purchases_query)
    cte_purchases = await prisma.query_raw("SELECT * FROM cte_purchases;")
    st.caption("Table: cte_purchases")
    st.write(pd.DataFrame(cte_purchases))

    st.write(
        """
    Right now, if we join the `spins_hourly` table with the `purchases` table, we will get
    lots of [null] values, as a user might not make a purchase in the same hour as when they spin. You can see
    this problem in the following query:
    """
    )
    join_query = """
        SELECT *
        FROM spins_hourly sh
        FULL JOIN cte_purchases p
        ON sh.date = p.date_trunc AND sh.user_id = p.user_id;
    """
    st.code(join_query, "sql")
    join_df = await prisma.query_raw(join_query)
    st.caption("Table: spins_hourly FULL JOIN cte_purchases")
    st.write(pd.DataFrame(join_df))
    st.write(
        """
    This problem also means we cannot insert data into `aggregated` table, since its primary keys are `[date, user_id]`, meaning
    [null] values are not allowed in these columns.
    """
    )

    st.write(
        """
    In order to solve this problem, we need to UNION (distinct) the `spins_hourly` table with the `purchases` table
    to get all the possible combinations of `date` and `user_id`, and to see all of a user's spins and purchases in a day. We
    can do this with the following query:
    """
    )
    await prisma.query_raw("DROP TABLE IF EXISTS cte_union_spins_purchases;")
    cte_union_spins_purchases_query = """
        SELECT * INTO TEMP TABLE cte_union_spins_purchases FROM (
            SELECT
                sh.date,
                sh.user_id
            FROM spins_hourly sh
            UNION
            SELECT
                p.date_trunc,
                p.user_id
            FROM cte_purchases p
        );
    """
    st.code(cte_union_spins_purchases_query, "sql")
    await prisma.query_raw(cte_union_spins_purchases_query)
    cte_union_spins_purchases = await prisma.query_raw(
        "SELECT * FROM cte_union_spins_purchases;"
    )
    st.caption("Table: cte_union_spins_purchases")
    st.write(pd.DataFrame(cte_union_spins_purchases))

    st.write(
        """
    Now we have a good basis to left join other tables with. In order to get spins and revenue data, we left join
    `cte_union_spins_purchases` with `spins_hourly` and `cte_purchases` tables. We can do this with the following query:
    """
    )
    await prisma.query_raw("DROP TABLE IF EXISTS cte_joined;")
    cte_joined_query = """
        SELECT * INTO TEMP TABLE cte_joined FROM (
            SELECT
                u.date,
                u.user_id,
                sh.country,
                sh.total_spins,
                p.revenue
            FROM cte_union_spins_purchases u
            LEFT JOIN spins_hourly sh
            ON u.date = sh.date AND u.user_id = sh.user_id
            LEFT JOIN cte_purchases p
            ON u.date = p.date_trunc AND u.user_id = p.user_id
        );
    """
    st.code(cte_joined_query, "sql")
    await prisma.query_raw(cte_joined_query)
    cte_joined = await prisma.query_raw("SELECT * FROM cte_joined;")
    st.caption("Table: cte_joined")
    st.write(pd.DataFrame(cte_joined))

    st.write(
        """
    We want to calculate ***Total Daily Revenue*** per user separately, so we can join the results to the `cte_joined` table
    later. We can do this with the following query:
    """
    )
    await prisma.query_raw("DROP TABLE IF EXISTS cte_total_daily_revenue;")
    cte_total_daily_revenue_query = """
        SELECT * INTO TEMP TABLE cte_total_daily_revenue FROM (
            SELECT 
                p.day_trunc,
                p.user_id,
                SUM(p.revenue) AS total_daily_revenue
            FROM cte_purchases p
            GROUP BY
                p.day_trunc,
                p.user_id
        );
    """
    st.code(cte_total_daily_revenue_query, "sql")
    await prisma.query_raw(cte_total_daily_revenue_query)
    cte_total_daily_revenue = await prisma.query_raw(
        """
        SELECT * FROM cte_total_daily_revenue
        ORDER BY user_id ASC, day_trunc ASC;
        """
    )
    st.caption("Table: cte_total_daily_revenue")
    st.write(pd.DataFrame(cte_total_daily_revenue))

    st.write(
        """
    With everything in place, we can finally aggregate to get to our final table. We can do this with the following query:
    """
    )
    await prisma.query_raw("DROP TABLE IF EXISTS cte_aggregated;")
    cte_aggregated_query = """
        SELECT * INTO TEMP TABLE cte_aggregated FROM (
            SELECT
                cte_joined.date,
                cte_joined.user_id,
                cte_joined.country AS country,
                COALESCE(SUM(cte_joined.total_spins), 0) AS total_spins,
                COALESCE(SUM(cte_joined.revenue), 0) AS total_revenue,
                COUNT(cte_joined.revenue) AS total_purchases,
                COALESCE(SUM(cte_joined.revenue) / COUNT(cte_joined.revenue), 0) AS avg_revenue_per_purchase,
                cte_total_daily_revenue.total_daily_revenue
            FROM cte_joined
            LEFT JOIN cte_total_daily_revenue
            ON DATE_TRUNC('day', cte_joined.date) = cte_total_daily_revenue.day_trunc 
            AND cte_joined.user_id = cte_total_daily_revenue.user_id
            GROUP BY
                cte_joined.date,
                cte_joined.user_id,
                cte_joined.country,
                cte_total_daily_revenue.total_daily_revenue
            ORDER BY cte_joined.user_id ASC
        );
    """
    st.code(cte_aggregated_query, "sql")
    await prisma.query_raw(cte_aggregated_query)
    cte_aggregated = await prisma.query_raw("SELECT * FROM cte_aggregated;")
    st.caption("Table: cte_aggregated")
    st.write(pd.DataFrame(cte_aggregated))

    st.write(
        """
    As you can see, we have successfully aggregated the data. We can now insert this data into the `aggregated` table:
    """
    )
    await prisma.query_raw("DELETE FROM aggregated WHERE true;")
    insert_intro_aggregated_query = """
        INSERT INTO aggregated
        (
            date,
            user_id,
            country,
            total_spins,
            total_revenue,
            total_purchases,
            avg_revenue_per_purchase,
            total_daily_revenue
        )
        SELECT
            date,
            user_id,
            country,
            total_spins,
            total_revenue,
            total_purchases,
            avg_revenue_per_purchase,
            total_daily_revenue
        FROM cte_aggregated;
    """
    st.code(insert_intro_aggregated_query, "sql")
    await prisma.query_raw(insert_intro_aggregated_query)
    aggregated = await prisma.query_raw("SELECT * FROM aggregated;")
    st.caption("Table: aggregated")
    aggregated_df = pd.DataFrame(aggregated)
    aggregated_expect_failure_df = pd.DataFrame(aggregated)
    aggregated_df["date"] = pd.to_datetime(
        aggregated_df["date"], format="ISO8601", utc=True
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.write(aggregated_df)

    st.write(
        """
    We can see that the data is successfully inserted into the `aggregated` table. We will continue to write tests to further
    validate the output of the `aggregated` table in the next step.
    """
    )

    st.write(
        "Before concluding this step, we need to save the aggregated to st.session_state:"
    )
    # Save aggregated_df
    st.session_state.aggregated: pd.DataFrame = aggregated_df
    st.session_state.aggregated_expect_failure: pd.DataFrame = (
        aggregated_expect_failure_df
    )
    # Compare the two DataFrames to ensure they are the same
    if st.session_state.aggregated.compare(aggregated_df).empty:
        st.success("Saved `aggregated_df` to st.session_state.aggregated successfully!")

    with st.expander("See all of the above queries in one single SQL query"):
        st.code(
            """
        -- Truncate `date` column by "hour" to transform `2022-04-01 0:10:39` to `2022-04-01 00:00:00`
        -- Truncate `date` column by "day" to transform `2022-04-01 07:19:01` to `2022-04-01 00:00:00`
        DROP TABLE IF EXISTS cte_purchases;
        SELECT * INTO TEMP TABLE cte_purchases FROM (
            SELECT 
                DATE_TRUNC('hour', date) AS date_trunc,
                DATE_TRUNC('day', date) AS day_trunc,
                p.user_id,
                p.revenue
            FROM purchases p
        );

        -- Union (distinct) the values of `spins_hourly` table with `cte_purchases` to get
        -- the list of all possible values of the 2 tables, ready for LEFT JOIN.
        DROP TABLE IF EXISTS cte_union_spins_purchases;
        SELECT * INTO TEMP TABLE cte_union_spins_purchases FROM (
            SELECT
                sh.date,
                sh.user_id
            FROM spins_hourly sh
            UNION
            SELECT
                p.date_trunc,
                p.user_id
            FROM cte_purchases p
        );

        -- Left join the unioned table above with `spins_hourly` and `cte_purchases` tables
        -- to get spins and revenue data.
        DROP TABLE IF EXISTS cte_joined;
        SELECT * INTO TEMP TABLE cte_joined FROM (
            SELECT
                u.date,
                u.user_id,
                sh.country,
                sh.total_spins,
                p.revenue
            FROM cte_union_spins_purchases u
            LEFT JOIN spins_hourly sh
            ON u.date = sh.date AND u.user_id = sh.user_id
            LEFT JOIN cte_purchases p
            ON u.date = p.date_trunc AND u.user_id = p.user_id
        );

        -- Calculate Total Daily Revenue per user from cte_purchases
        DROP TABLE IF EXISTS cte_total_daily_revenue;
        SELECT * INTO TEMP TABLE cte_total_daily_revenue FROM (
            SELECT 
                p.day_trunc,
                p.user_id,
                SUM(p.revenue) AS total_daily_revenue
            FROM cte_purchases p
            GROUP BY
                p.day_trunc,
                p.user_id
        );

        -- Aggregate
        DROP TABLE IF EXISTS cte_aggregated;
        SELECT * INTO TEMP TABLE cte_aggregated FROM (
            SELECT
                cte_joined.date,
                cte_joined.user_id,
                cte_joined.country AS country,
                SUM(cte_joined.total_spins) AS total_spins,
                SUM(cte_joined.revenue) AS total_revenue,
                COUNT(cte_joined.revenue) AS total_purchases,
                SUM(cte_joined.revenue) / COUNT(cte_joined.revenue) AS avg_revenue_per_purchase,
                cte_total_daily_revenue.total_daily_revenue
            FROM cte_joined
            LEFT JOIN cte_total_daily_revenue
            ON DATE_TRUNC('day', cte_joined.date) = cte_total_daily_revenue.day_trunc AND cte_joined.user_id = cte_total_daily_revenue.user_id
            GROUP BY
                cte_joined.date,
                cte_joined.user_id,
                cte_joined.country,
                cte_total_daily_revenue.total_daily_revenue
            ORDER BY cte_joined.user_id ASC
        );

        -- Insert into table `aggregated`
        DELETE FROM aggregated WHERE true;
        INSERT INTO aggregated
        (
            date,
            user_id,
            country,
            total_spins,
            total_revenue,
            total_purchases,
            avg_revenue_per_purchase,
            total_daily_revenue
        )
        SELECT
            date,
            user_id,
            country,
            total_spins,
            total_revenue,
            total_purchases,
            avg_revenue_per_purchase,
            total_daily_revenue
        FROM cte_aggregated;

        SELECT * FROM aggregated;
        """,
            "sql",
        )

    st.write("""Let's move on to Step 5 when you're ready.""")


if __name__ == "__main__":
    asyncio.run(main())
