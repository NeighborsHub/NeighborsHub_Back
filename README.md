# NeighborsHub_Back

# Run
 ``python -m virtualenv venv && source venv/bin/activate``

``pip install -r requirements.txt``
# Database 
```

sudo docker run --name postgis-db \ 
                -e POSTGRES_DB=<db-name> \
                -e POSTGRES_USER=<user> \
                -e POSTGRES_PASSWORD=<password> \
                -v /var/postgress=/var/lib/postgresql/data \ 
                -p 5432:5432 \ 
                -d postgis/postgis:latest
```

# Load Fixtures

``python manage.py loaddata fixtures/*.json`` 