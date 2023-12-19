FROM python:3.11-slim

WORKDIR /app

# env
# prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# dependencies
COPY requirements.txt .
ADD prisma prisma
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y curl wget

# project
COPY . .
COPY .env.production .env

# run
CMD prisma migrate reset --schema=prisma/schema.prisma --force; streamlit run Home.py