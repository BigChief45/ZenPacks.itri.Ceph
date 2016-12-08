"""Collets Ceph Endpoint cluster and monitor information"""

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

import json

class CephEndpoint(CommandPlugin):
    """Modeler plugin for Ceph endpoints"""
    
    # The essential variable that a CommandPlugin must provide is the COMMAND. This can
    # be anything that will run in a bash shell, so includes other language scripts if
    # they have an appropriate shebang.
    #
    # The output will be delivered into a RESULTS variable, to be processed by the
    # PROCESS method.
    command = 'sudo ceph -s -f json'

    def process(self, device, results, log):
        results = json.loads(results)
    
        log.info('Modeler {0} processing data for device {1}'.format(self.name(), device.id))
        log.debug('Results: \n {0}'.format(results))

        ## Cluster ##
        clusters = []
        clusters.append(ObjectMap(
            modname='ZenPacks.itri.Ceph.CephCluster',
            data=dict(
                id = prepId(results['fsid']),
                version = results['pgmap']['version'],
                fsid = results['fsid'],
                bytes_used = results['pgmap']['bytes_used'],
                bytes_avail = results['pgmap']['bytes_avail'],
                bytes_total = results['pgmap']['bytes_total'],
                status = results['health']['summary'][0]['severity'],
                summary = results['health']['summary'][0]['summary']
            )))
        

        ## Monitors ##
        mons_health = results['health']['health']['health_services'][0]['mons']
        mon_map = results['monmap']['mons']
        
        monitors = []
        for monitor in mons_health:
            log.debug('name: {0} | kb_total: {1} | kb_used: {2} | kb_avail: {3} | avail_percent: {4} | health: {5}'.format(monitor['name'], monitor['kb_total'], monitor['kb_used'], monitor['kb_avail'], monitor['avail_percent'], monitor['health']))
            
            monitors.append(ObjectMap(
                modname='ZenPacks.itri.Ceph.CephMonitor',
                data=dict(
                    id = prepId(monitor['name']),
                    title = monitor['name'],
                    kb_total = monitor['kb_total'],
                    kb_used = monitor['kb_used'],
                    kb_avail = monitor['kb_avail'],
                    avail_percent = monitor['avail_percent'] / 100.00,
                    in_quorum = monitor['name'] in results['quorum_names'],
                    health = monitor['health']
                )))
        
        # For Host Address and Port
        for i, monitor in enumerate(mon_map):
            monitors[i].rank = monitor['rank']
            monitors[i].host = monitor['addr'].split(':')[0]
            monitors[i].port = monitor['addr'].split(':')[1].split('/')[0]
            
        relmaps = []
        
        relmaps.append(RelationshipMap(
            relname='cephClusters',
            modname='ZenPacks.itri.Ceph.CephCluster',
            objmaps=clusters
            ))
        
        relmaps.append(RelationshipMap(
            relname='cephMonitors',
            modname='ZenPacks.itri.Ceph.CephMonitor',
            objmaps=monitors
            ))
        
        return relmaps
