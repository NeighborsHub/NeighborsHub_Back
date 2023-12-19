FROM postgres:latest
LABEL authors="milad"

# Set environment variables
ENV POSTGRES_DB neighbors_hub_db
ENV POSTGRES_USER root
ENV POSTGRES_PASSWORD 12345
RUN apt-get update \
    && apt-get install -y postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
    && rm -rf /var/lib/apt/lists/*

# Expose port 9876 for PostgreSQL
EXPOSE 9876

# Optionally, you can include initialization scripts
# COPY ./init.sql /docker-entrypoint-initdb.d/

# Define a health check to verify the container's health
HEALTHCHECK --interval=5s --timeout=3s \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1
