# import os

from google.cloud import datastore

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/abo/Downloads/tbilisi-routing-e1310482f20a.json"


def create_client():
    return datastore.Client('tbilisi-routing')


def basic_query(client, bus_number, stop_id):
    query = client.query(kind='Task')
    query.add_filter('bus_number', '=', str(bus_number))
    query.add_filter('stop_id', '=', str(stop_id))
    query.order = ['-created']
    return list(query.fetch(limit=1))

