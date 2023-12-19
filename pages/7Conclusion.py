import asyncio
import streamlit as st


async def main():
    ##############################
    # Page config
    ##############################
    title = "Conclusion | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.sidebar.info(title)

    ##############################
    # Main content
    ##############################
    st.header("Conclusion")

    if "conclusion_ready" not in st.session_state:
        st.error(
            """
        You need to have uploaded the XLSX file in Step 1, 
        processed them in Step 2, 
        inserted them to PSQL in Step 3, 
        aggregated them in Step 4,
        and ran them through test cases in Step 5 first.
        """
        )
        st.stop()

    st.write(
        """
        Throughout this project, we have done the following:

        1. Uploaded the XLSX file containing the raw data.
        2. Validated and cleaned the raw data.
        3. Inserted the validated data into PostgreSQL.
        4. Aggregated the data using SQL.
        5. Ran the data through test cases.
        6. Defined a guideline for handling test case failures, as well as went through a mock scenario where 
        we had to handle a test case failure regarding datetime format mismatch.

        ...all while using Streamlit to build a web app to showcase the results.

        #### Possible improvements:
        - Add more test cases. Or rather, more suitable test cases to fit the business logic and requirements. (Check
        if country codes are valid, check if user_ids are valid...)
        - Add more data validation and cleaning. Or again, more suitable validation and cleaning as above.
        - More concise code regarding writing test cases, data validation and aggregation.

        Hope you had a great time going through this project with me, as much as I did while working on it.

        Again, please feel free to reach out to me if you have any questions.

        End.
        """
    )


if __name__ == "__main__":
    asyncio.run(main())
