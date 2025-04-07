import os, sys
import json
import time

MAX_REQUEST_FOR_DAY = 20
SETTINGS_FILE_PATH = 'c:/AI_assis'


def is_cache_file_created() -> bool:
    return os.path.exists(SETTINGS_FILE_PATH)

def create_cache_file() -> None:
    if not is_cache_file_created():
        os.makedirs('c:/AI_assis', exist_ok=True)
        open(SETTINGS_FILE_PATH + "/cache.json", 'w').close()
        with open(SETTINGS_FILE_PATH + "/cache.json", 'w') as file:
            json.dump({'this_day_requests': MAX_REQUEST_FOR_DAY, "saved_time": 0, "requests": []}, file)
class RequestsControlleer:
    def __init__(self, requests_cout_per_day: int = MAX_REQUEST_FOR_DAY,
                       settings_file_path: str = SETTINGS_FILE_PATH) -> None:
        self.requests_cout_per_day = requests_cout_per_day
        self.cache_file_path = settings_file_path
        self.cache_file = self.cache_file_path + "/cache.json"
        self.requests_data = []

        if not is_cache_file_created():
            create_cache_file()

    def UpdateRequestsCount(self):
        info = json.load(open(self.cache_file, 'r'))
        info['this_day_requests'] -= 1
        json.dump(info, open(self.cache_file, 'w'))

    def SetRequestCount(self, count: int):
        info = json.load(open(self.cache_file, 'r'))
        info['this_day_requests'] = count
        json.dump(info, open(self.cache_file, 'w'))

    def GetRequestsCount(self):
        return json.load(open(self.cache_file, 'r'))['this_day_requests']

    def AddRequest(self, request_data: dict) -> None:
        self.requests_data.append(request_data)
        info = json.load(open(self.cache_file, 'r'))
        info['requests'].append(request_data)
        json.dump(info, open(self.cache_file, 'w'))

    def SetEndTime(self):
        t = time.time()
        info = json.load(open(self.cache_file, 'r'))
        info['saved_time'] = t
        json.dump(info, open(self.cache_file, 'w'))

    def GetWaitedTime(self):
        saved_t = json.load(open(self.cache_file, 'r'))['saved_time']
        at_t = time.time()
        delta_time = at_t - saved_t
        return 12 - time.gmtime(delta_time).tm_hour 

