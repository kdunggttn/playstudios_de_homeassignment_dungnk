import streamlit as st


# streamlit run Home.py --server.port 8500 --server.runOnSave true


def main():
    ##############################
    # Title
    ##############################
    title = "Home | PlayStudios - DE Home Assignment - Daniel Nguyen"
    st.set_page_config(
        page_title=title,
        page_icon="🎲",
    )
    st.title(title)
    st.sidebar.info(title)

    st.write(
        """
    Hello. I am Daniel Nguyen (kdunggttn@gmail.com). 

    This is my submission for the PlayStudios DE Home Assignment. I've chosen to use Streamlit to build this web app.

    Use the .xlsx file **supplied with the Home Assignment** (or the file named `ORIGINAL_DATASET.xlsx` included with 
    the repo, which is the original xlsx file given to me, for easier access) in `Step 1 - Upload data` of the 
    Streamlit web app to come along with me, as we validate, clean and ultimately insert the processed data into PostgreSQL.
    """
    )

    st.info(
        """
    The web app is designed to handle repeated requests, meaning you can go from Step 1 -> Step 2 and back to Step 1 without any problems.
    """
    )

    st.warning(
        """
    **IMPORTANT**: Please do not skip any steps (if this is your first time here), and try to follow the steps in order, 
    as well as read carefully the notes I left in them. You can skip the steps once you have gone through them at least once.

    If you accidentally skip a step, you will be greeted with a warning message. 
    Please follow the instructions in the warning message.
    """
    )

    st.write(
        """
        Have fun! And please feel free to reach out to me if you have any questions.
        """
    )


if __name__ == "__main__":
    main()
