# NeighborsHub_Back

# Run
 ``python -m virtualenv venv && source venv/bin/activate``

``pip install -r requirements.txt``
# Database 
``sudo docker run --name postgis -p 5432:5432 -e POSTGRES_PASSWORD=12345 -e POSTGRES_USER=root -e POSTGRES_DB=neighbors_hub_db -d postgis/postgis``