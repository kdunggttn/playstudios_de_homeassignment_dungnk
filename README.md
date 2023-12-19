# PlayStudios - DE Home Assignment - Daniel Nguyen

Hello. I am Daniel Nguyen (kdunggttn@gmail.com).

This is my submission for the PlayStudios DE Home Assignment. I've chosen to use Streamlit to build this web app.

Clone this repo to your local machine.

To run the containers:

```
docker-compose build && docker-compose up -d
```

When starting the containers for the first time, Docker will install Prisma, and apply the migrations to create the tables in PostgreSQL. Please wait for a few minutes for the migrations to complete. Once they are done, you can check the status of the healthcheck to find out if the web app is accessible with this command:

```
docker-compose ps
```

If the web app container is healthy, go to http://localhost:8501 to see the Streamlit frontend.

Use the .xlsx file **supplied with the Home Assignment** (or the file named `ORIGINAL_DATASET.xlsx` included with the repo, which is the original xlsx file given to me, for easier access) in `Step 1 - Upload data` of the Streamlit web app to come along with me, as we validate, clean and ultimately insert the processed data into PostgreSQL.

There are notes and comments in the code to explain my thought process and decisions. Open up the `Home` page of the Streamlit web app to get started.

## Tech stacks:

### Frontend

-   `Streamlit` as frontend
-   `Prisma ORM` with separate schema file (schema.prisma)
-   `PostgreSQL` as database

### Docker

-   `docker-compose` to run the containers
