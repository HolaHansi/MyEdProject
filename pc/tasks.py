from .table import get_pc_data


def get_data():
    # note you'll need to populate the buildings database through rooms.tasks get_data() first
    get_pc_data()
    return 'successfully got pc data'
