from lib import vk_api
import json
import sys
import time
from django.core.management.base import BaseCommand


from pymongo import MongoClient
mclient = MongoClient('localhost', 27017)
mdb = mclient['Tmp']
mcollection = mdb.FilteredMembers


def cache_driver(name):
    if name == 'mongo':
        from services.cache_driver import MongoCacheDriver
        return MongoCacheDriver()
    elif name == 'memcached':
        from services.cache_driver import MemcachedCacheDriver
        return MemcachedCacheDriver()
    raise NameError('Cache driver with name `'+name+'` not found')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('group_id', nargs='+', type=str)

    def get_group_members(self, group_id):
        mem_key = 'get_group_members__' + str(group_id)
        cdrv = cache_driver('mongo')
        cdrv.expiration = 60*60
        cache = cdrv.get(mem_key)
        if cache is not None:
            return cache
            pass

        request = vk_api.request('groups.getMembers')
        request.set_param('group_id', group_id)
        request.set_param('offset', 0)
        request.set_param('count', 1000)
        request.set_param('fields', 'sex,deactivated,bdate,city,country,online,online_mobile,connections,last_seen')

        list = vk_api.list(request)
        list.exec()
        items = list.get_items()
        #print(sys.getsizeof(items))
        cdrv.set(mem_key, json.dumps(items))
        return items

    def get_filtered_members(self, group_id):
        members = self.get_group_members(group_id)
        ctyme = time.time() - (3600 * 24 * 15)
        members_list = []
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
            members_list.append(member)
        return members_list

    def handle(self, *args, **options):

        group_id = options['group_id'][0]

        groups = ['freshwindspahotel', 'moreonru', 'zdorove_zhenshhin']

        members_list = []
        for group_id in groups:
            members_list += self.get_filtered_members(group_id)
