"""Collects a Ceph endpoint's pool information."""

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

import json

class CephPool(CommandPlugin):
    """Modeler plugin for Ceph Pools"""

    command = 'sudo ceph df -f json'

    def process(self, device, results, log):
        results = json.loads(results)
    
        log.info('Modeler {0} processing data for device {1}'.format(self.name(), device.id))

        ## Pools ##
        pools = []
        for pool in results['pools']:
            pools.append(ObjectMap(
                modname='ZenPacks.itri.Ceph.Pool',
                data=dict(
                    id = prepId(pool['name']),
                    title = pool['name'],
                    bytes_used = pool['stats']['bytes_used'],
                    max_avail = pool['stats']['max_avail'],
                    objects = pool['stats']['objects'],
                )))
        
        relmaps = []
        
        relmaps.append(RelationshipMap(
            relname='cephPools',
            modname='ZenPacks.itri.Ceph.CephPool',
            objmaps=pools
            ))
        
        return relmaps
