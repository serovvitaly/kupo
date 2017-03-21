from lib import vk_api
import json
import sys
import time
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from pymemcache.client.base import Client as MemClient
mem_client = MemClient(('localhost', 11211))



class Command(BaseCommand):


    def get_group_members(self, group_id):
        mem_key = 'get_group_members__' + str(group_id)
        cache = mem_client.get(mem_key)
        if cache is not None:
            #return json.loads(cache.decode('utf8'))
            pass

        request = vk_api.request('groups.getMembers')
        request.set_param('group_id', group_id)
        #request.set_param('offset', 16000)
        request.set_param('count', 1000)
        request.set_param('fields', 'sex,deactivated,bdate,city,country,online,online_mobile,connections,last_seen')

        list = vk_api.list(request)
        list.exec()
        items = list.get_items()
        #print(sys.getsizeof(items))

        #mem_client.set(mem_key,  json.dumps(items), 60*60)
        return items


    def handle(self, *args, **options):

        members = self.get_group_members('moreonru')

        ctyme = time.time() - (3600 * 24 * 15)

        members_ids = []
        for member in members:
            if 'last_seen' not in member:
                continue
            if int(member['last_seen']['time']) < ctyme:
                continue
            if member['sex'] != 1:
                continue
            if 'city' not in member:
                continue
            if member['city']['id'] != 1:
                continue
            if 'deactivated' in member:
                print(member['deactivated'])
            members_ids.append(member['id'])

        print(len(members_ids))
