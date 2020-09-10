import datetime
import json

from databases.elasticsearch import ElasticSearch
from databases.mysql import MYSQL
from settings.constants import STATIC_DATA_ELASTIC_SEARCH, INVENTORY_DEPTH_ES_INDEX
from utils.utils import Utils


def create_persuasions(args):
    query = {"_source": ["hotelId", "scores.score", "scores.roomsToRequest", "scores.bucketedScore",
                         "scores.activeRoomCount", "scores.roomCode", "scores.roomName", "params.inventoryWindow",
                         "params.transactionWindow", "avgBucketed", "eventDate"], "size": 1,
             "sort": [{"createdOn": {"order": "desc"}}],
             "query": {"bool": {
                 "must": [{"term": {"hotelId": args.get("hotel_id", "")}},
                          {"term": {"eventDate": args.get("event_date")}},
                          {"range": {"bucketedScore": {"lt": args.get("bucketed_score_threshold")}}}]}}}
    es = ElasticSearch(STATIC_DATA_ELASTIC_SEARCH["host"], STATIC_DATA_ELASTIC_SEARCH["protocol"],
                       STATIC_DATA_ELASTIC_SEARCH["port"])
    response = es.get_response(INVENTORY_DEPTH_ES_INDEX, query)

    window = 30  # Default window size
    new_persuasions = []
    for value in response:
        rooms = value.pop("scores")
        windows = value.pop("params")
        window = windows.get("inventoryWindow", window)
        for room in rooms:
            data = dict(value)
            data.update(room)
            data.update(windows)
            new_persuasions.append(data)
    return new_persuasions, window


def get_inventory_rooms(ex_persuasions, window):
    today = datetime.datetime.now().date()
    window_end = today + datetime.timedelta(days=window)
    persuasion_room_map = {persuasion['roomCode']: persuasion for persuasion in ex_persuasions}
    room_codes = persuasion_room_map.keys()

    query = "select a.available, a.booked, a.blocked, a.room_code " \
            "from hotels_inventorymanager3 a join hotels_roomdetail b on (a.room_code = b.roomtypecode) " \
            "where room_code in ({room_codes}) and idate between '{today}' and '{window_end}'"

    inventory_query = Utils.format_data(query,
                                        dict(room_codes=",".join(room_codes), today=today, window_end=window_end))
    inventory_manager_qs = json.loads(MYSQL.fetch_data(inventory_query))
    inventory_manager_qs = [['1', '0', '0', '45000405199'],
                            ['0', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['0', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['0', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405199'], ['0', '0', '0', '45000405199'],
                            ['0', '0', '0', '45000405199'], ['1', '0', '0', '45000405199'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['0', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405201'],
                            ['1', '0', '0', '45000405201'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['0', '0', '0', '45000405204'], ['0', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204'],
                            ['1', '0', '0', '45000405204'], ['1', '0', '0', '45000405204']]

    return inventory_manager_qs, persuasion_room_map


def update_persuasions(ex_persuasions, window):
    # Checking for refresh persuasions if any
    persuasions = []
    inventory_qs, persuasion_room_map = get_inventory_rooms(ex_persuasions, window)

    for inventory in inventory_qs:
        # current_room_code = inventory["room_code"]
        # if persuasion_room_map.get(current_room_code, None) and \
        #         (not inventory["blocked"] or
        #          ((inventory["booked"] + inventory["available"]) > persuasion_room_map[current_room_code][
        #              "roomsToRequest"])):
        #     persuasions.append(persuasion_room_map[current_room_code])
        #     persuasion_room_map.pop(current_room_code, None)
        # ['available', 'booked', 'blocked', 'room_code'],
        current_room_code = inventory[3]
        if persuasion_room_map.get(current_room_code, None) and (not int(inventory[2]) or (
                (int(inventory[1]) + int(inventory[0])) > persuasion_room_map[current_room_code]["roomsToRequest"])):
            persuasions.append(persuasion_room_map[current_room_code])
            persuasion_room_map.pop(current_room_code, None)

    return persuasions


def fetch_persuasions(request_data, args):
    new_persuasions, window = create_persuasions(args)

    # Returning all the new persuasion
    if not request_data.get("p_id"):
        return new_persuasions
    final_persuasions = update_persuasions(new_persuasions, window)

    return final_persuasions
