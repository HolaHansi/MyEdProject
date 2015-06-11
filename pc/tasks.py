import requests
import xml.etree.ElementTree as ET
from .table import get_building_data, get_pc_data
from celery import task

@task
def get_data():
    get_building_data()
    get_pc_data()
    return 'successfully got pc and building data (merge)'




