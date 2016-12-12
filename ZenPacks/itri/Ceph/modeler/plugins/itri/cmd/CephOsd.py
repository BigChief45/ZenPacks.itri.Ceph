"""Collects a Ceph endpoint's OSD information."""

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

import json

class CephOsd(CommandPlugin):
    """Modeler plugin for Ceph Object Storage Daemons"""
    
    command = 'sudo ceph osd dump -f json'

    def process(self, device, results, log):
        results = json.loads(results)
    
        log.info('Modeler {0} processing data for device {1}'.format(self.name(), device.id))
        log.debug('Results: \n {0}'.format(results))

        ## OSDs ##
        osds = []
        for osd in results['osds']:
            osds.append(ObjectMap(
                modname='ZenPacks.itri.Ceph.CephOsd',
                data=dict(
                    id = prepId(osd['uuid']),
                    title = osd['uuid'],
                    up = osd['up'],
                    inn = osd['in'],
                    weight = osd['weight'],
                    public_addr = osd['public_addr'],
                    cluster_addr = osd['cluster_addr']
                )))
        
        relmaps = []
        
        relmaps.append(RelationshipMap(
            relname='cephOsds',
            modname='ZenPacks.itri.Ceph.CephOsd',
            objmaps=osds
            ))
        
        return relmaps
