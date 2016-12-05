from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

import json

class CephEndpoint(CommandPlugin):
    """Modeler plugin for Ceph devices"""
    
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
                    health = monitor['health']
                )))
        
        mon_index = 0
        for monitor in mon_map:
            monitors[mon_index]['rank'] = monitor['rank']
            monitors[mon_index]['host'] = monitor['addr'].split(':')[0]
            monitors[mon_index]['port'] = monitor['addr'].split(':')[1]
            
            mon_index += 1
        
        relmaps = []
        
        # Monitors
        relmaps.append(RelationshipMap(
            relname='cephMonitors',
            modname='ZenPacks.itri.Ceph.CephMonitor',
            objmaps=monitors
            ))
        
        return relmaps
