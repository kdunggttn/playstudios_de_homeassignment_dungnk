import streamlit as st
import pandas as pd
import asyncio
from prisma import Prisma
import unittest
import pandas as pd
import sys
import inspect
from unittest import IsolatedAsyncioTestCase

sys.tracebacklimit = 0


@st.cache_data
def read_prisma_schema():
    f = open("prisma/schema.prisma", "r")
    return f.read()


##############################
# Unit tests for data validation
##############################
class TestDataValidation(unittest.TestCase):
    """
    A collection of unit tests for validating the data in the aggregated table.
    """

    def setUp(self):
        # Load the aggregated table from Step 4
        self.df: pd.DataFrame = st.session_state.aggregated
        self.df_expect_failure: pd.DataFrame = (
            st.session_state.aggregated_expect_failure
        )

    def test_date_formats(self):
        """
        Test if the date column values are in the format "YYYY-MM-DD HH:MM:SS"
        """
        date_format = "%Y-%m-%d %H:%M:%S"
        try:
            pd.to_datetime(self.df["date"], format=date_format)
        except ValueError as e:
            self.fail(f"Date format test failed: {e}")

    def test_date_formats_expect_failure(self):
        """
        Test if the date column values are in the format "YYYY-MM-DD HH:MM:SS".

        Expect failure, as the date column values are in the format
        "YYYY-MM-DDTHH:MM:SSZ" (as returned by PSQL).
        """
        date_format = "%Y-%m-%d %H:%M:%S"
        try:
            pd.to_datetime(self.df_expect_failure["date"], format=date_format)
        except ValueError as e:
            self.fail(f"Date format test failed: {e}")

    def test_non_null_values_in_required_columns(self):
        """
        Test if the required columns [date, user_id] have non-null values
        """
        required_columns = ["date", "user_id"]
        for column in required_columns:
            if self.df[column].isnull().values.any():
                self.fail(f"Required column {column} has null values.")

    def test_positive_values_for_numeric_columns(self):
        """
        Test if the numeric columns
        [
            "total_spins",
            "total_revenue",
            "total_purchases",
            "avg_revenue_per_purchase",
            "total_daily_revenue",
        ] have negative values, since these are revenue-related columns.
        """
        numeric_columns = [
            "total_spins",
            "total_revenue",
            "total_purchases",
            "avg_revenue_per_purchase",
            "total_daily_revenue",
        ]
        for column in numeric_columns:
            if (self.df[column] < 0).any():
                self.fail(f"Numeric column {column} has negative values.")

    def test_string_field_lengths(self):
        """
        Test if [date, user_id] fields have lengths within expected limits
        """
        max_lengths = {
            "user_id": 7,
            "country": 2,
        }
        for column, max_length in max_lengths.items():
            if self.df[column].str.len().max() > max_length:
                self.fail(f"Column {column} has value with length > {max_length}.")

    def test_revenue_purchase_relationship(self):
        """
        Ensure 'total_revenue' is greater than 0 only when 'total_purchases' is also greater than 0
        """
        valid_relationship = (
            (self.df["total_revenue"] > 0) & (self.df["total_purchases"] > 0)
        ) | ((self.df["total_revenue"] == 0) & (self.df["total_purchases"] == 0))
        self.assertTrue(
            valid_relationship.all(),
            "Invalid relationship between 'total_revenue' and 'total_purchases'",
        )

    def test_consistency_total_daily_revenue_by_user_id(self):
        """
        Test if the sum of "total_revenue" for each "user_id" each day is equal to "total_daily_revenue"
        """
        # Load purchases_from_db_df from st.session_state from Step 3
        purchases_from_db_df: pd.DataFrame = st.session_state.purchases_from_db
        purchases_from_db_df["day"] = pd.to_datetime(
            purchases_from_db_df["date"]
        ).dt.date
        agg_purchases_from_db_df = (
            purchases_from_db_df.groupby(["day", "user_id"], as_index=False)
            .sum()[["day", "user_id", "revenue"]]
            .rename(columns={"revenue": "total_daily_revenue"})
        )

        # Get distinct values of "date" and "user_id" and "total_daily_revenue" from aggregated table
        agg_total_daily_revenue_df = self.df[["date", "user_id", "total_daily_revenue"]]
        agg_total_daily_revenue_df["day"] = pd.to_datetime(
            agg_total_daily_revenue_df["date"]
        ).dt.date
        del agg_total_daily_revenue_df["date"]
        agg_total_daily_revenue_df = (
            agg_total_daily_revenue_df[
                [
                    "day",
                    "user_id",
                    "total_daily_revenue",
                ]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Compare if total_daily_revenue columns of the two DataFrames are equal
        self.assertTrue(
            not agg_total_daily_revenue_df.compare(agg_purchases_from_db_df).empty,
            "Inconsistent total_daily_revenue by user_id",
        )


def run_single_test(test_name: str):
    singletest = unittest.TestSuite()
    singletest.addTest(TestDataValidation(test_name))
    run = unittest.TextTestRunner().run(singletest)
    # Return test result
    return {
        "successful": run.wasSuccessful(),
        "errors": run.errors,
        "failures": run.failures,
    }


async def main():
    ##############################
    # Page config
    ##############################
    title = "Step 5 - Validate table output (Task #2) | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Step 5: Write tests to validate table output (Task #2)")

    if "aggregated" not in st.session_state:
        st.error(
            """
        You need to have uploaded the XLSX file in Step 1, 
        processed them in Step 2, 
        inserted them to PSQL in Step 3, 
        and aggregated them in Step 4 first.   
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

    st.write("Here we have the aggregated table from Step 4:")

    aggregated_df: pd.DataFrame = st.session_state.aggregated

    with st.expander("See aggregated data from DB"):
        st.caption("Table: aggregated")
        st.write(aggregated_df)

    st.subheader("List of possible output data validation tests:")
    with st.expander("See the whole unittest suite"):
        st.code(
            inspect.getsource(TestDataValidation),
            "python",
        )

    st.checkbox(
        "Test 1: Check the dates are in the correct format `YYYY-MM-DD HH:MM:SS`",
        value=True,
    )
    st.code(
        inspect.getsource(TestDataValidation.test_date_formats),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_date_formats"))

    st.checkbox(
        "Test 2: Testing if the primary keys `[date, user_id]` have `null` values",
        value=True,
    )
    st.code(
        inspect.getsource(TestDataValidation.test_non_null_values_in_required_columns),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_non_null_values_in_required_columns"))

    st.checkbox(
        "Test 3: Testing positive values for numeric fields `[total_spins, revenue]`",
        value=True,
    )
    st.info(
        """
        Although we have already defined constraints on the `total_spins` and `revenue` 
        fields when we created the tables `spins_hourly` and `purchases` respectively in PSQL
        (to ensure these values are always positive integers), we can write test for them as follows.

        See `prisma/migrations/20231219081237_add_constraints/migration.sql` for details.
        """
    )
    st.code(
        inspect.getsource(TestDataValidation.test_positive_values_for_numeric_columns),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_positive_values_for_numeric_columns"))

    st.checkbox(
        "Test 4: Testing values in string fields `[user_id, country]` are within expected limits",
        value=True,
    )
    st.info(
        """
        Although we have already defined constraints on the `user_id` and `country` 
        fields when we created the tables in PSQL, we can write test for them as follows.

        See `prisma/schema.prisma` for details.
        """
    )
    st.code(
        inspect.getsource(TestDataValidation.test_string_field_lengths),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_string_field_lengths"))

    st.checkbox(
        "Test 5: Testing relationship between `total_revenue` and `total_purchases`",
        value=True,
    )
    st.code(
        inspect.getsource(TestDataValidation.test_revenue_purchase_relationship),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_revenue_purchase_relationship"))

    st.checkbox(
        "Test 6: Test if the sum of `total_revenue` for each `user_id` each day is equal to `total_daily_revenue`",
        value=True,
    )
    st.code(
        inspect.getsource(
            TestDataValidation.test_consistency_total_daily_revenue_by_user_id
        ),
        "python",
    )
    st.write("Example of this test running on `aggregated_df`:")
    st.write(run_single_test("test_consistency_total_daily_revenue_by_user_id"))

    st.write(
        """
        All tests passed.
         
        We have successfully written tests to validate the data in the aggregated table. Next, we will
        handle test case failures.
        """
    )

    st.subheader("In case of test case failures")
    st.write(
        """
        In case of test failures, there are a number of steps we can take to identify and fix the problem:
        """
    )
    st.write(
        """
        ##### 1. Identify the cause of failure
        - Inspect the Failed Test: Understand which specific test case failed. For example, `test_consistency_total_daily_revenue_by_user_id`
        may fail because the data was handled incorrectly while transforming (wrong joins, incorrect use of transformers).
        - Examine Data: Look at the input data associated with the failed test case to understand the issue.

        ##### 2. Debug the Test
        - Check Assumptions: Review the assumptions made in the test. Ensure they align with the data and intended validations.
        - Inspect Data: Verify if the data deviates from the expected format, range, or constraints defined by the test.
        
        ##### 3. Validate and Rectify
        - Correct Data or Test: If the data is incorrect, rectify it to meet the expectations set by the test. 
        If the test logic is faulty, update the test to correctly validate the data.
        
        ##### 4. Rerun the Tests
        - Re-run Tests: Once changes are made, rerun the test suite to confirm if the issue has been resolved and all tests pass.
        
        ##### 5. Iterate and Document
        - Iterate: Repeat this process iteratively, focusing on one test at a time until all tests pass.
        - Document Findings: Keep a record of the reasons behind the failures and the steps taken to rectify them for future reference.
        
        ##### 6. Refine and Enhance Tests
        - Refine Tests: If necessary, refine or expand your tests to cover additional scenarios or improve the validation criteria.
        
        ##### 7. Review Changes
        - Review Changes: Ensure that rectifications made to the data or tests do not introduce new issues or compromises in the validation process.
        
        ##### 8. Deployment or Use
        - Deploy Validated Data: Once all tests pass, deploy the validated data for further use or analysis.
        """
    )

    st.subheader("Example of a test case failure")
    st.write(
        """
        **Test**: Check the dates are in the correct format `YYYY-MM-DD HH:MM:SS`

        Expect failure, as the `date` column values are in the format
        `YYYY-MM-DDTHH:MM:SSZ` (ISO8601 as returned by PSQL).
        """,
    )
    st.code(
        inspect.getsource(TestDataValidation.test_date_formats_expect_failure),
        "python",
    )
    st.write(run_single_test("test_date_formats_expect_failure"))

    st.write(
        """
        We can see that the test failed because the `date` column values are in the format `YYYY-MM-DDTHH:MM:SSZ`, 
        like the value returned by the test result: `2022-04-01T00:00:00+00:00`.

        Applying the troubleshooting steps above, we can fix the problem by parsing the `date` column values to the correct format:
        """,
    )
    st.code(
        """
    aggregated_df["date"] = pd.to_datetime(
        aggregated_df["date"], 
        format="ISO8601", 
        utc=True
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    """,
        "python",
    )
    st.info(
        """
        You can actually see this fix in action in the `Step 4 - Aggregate data.py` file, line `267-269`.
        """,
    )
    st.write(
        """
        After fixing the problem, we can see that the test passes:
        """,
    )
    st.write(run_single_test("test_date_formats"))

    st.write(
        """
        We have successfully written tests to validate the data in the aggregated table, defined
        a guideline to follow on a test case failure, and handled an example test case failure.
        
        Let's move on to the Conclusion when you're ready.
        """
    )

    # Set st.session_state.conclusion_ready to True to let users know they can move on to the
    # conclusion after finishing all the steps above.
    st.session_state.conclusion_ready = True


if __name__ == "__main__":
    asyncio.run(main())
