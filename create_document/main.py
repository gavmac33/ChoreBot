import firebase_admin
from firebase_admin import firestore

fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()


def add_group_document(request):
    request_json = request.get_json(silent=True)
    if request_json:
        group_name = request_json["GROUP_NAME"]
        collection_name = request_json["COLLECTION_NAME"]
    else:
        raise Exception("No group name was given")

    data = {'Suite': group_name}

    daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in daysOfWeek:
        for i in range(4):
            data[day + str(i+1)] = False

    DATABASE.collection(collection_name).document(group_name).set(data)