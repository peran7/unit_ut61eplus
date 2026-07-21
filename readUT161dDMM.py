
import logging
from ut161d import UT161D

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

#dmm = UT61EPLUS()
dmm = UT161D()
name=dmm.getName()
print("name=",name)
print(f'name={dmm.getName()}')
dmm.sendCommand('lamp')
m = dmm.takeMeasurement()
log.info('measurent=%s', m)
#
for i in range(500):
    mesure=dmm.takeMeasurement()
    print(mesure.display_decimal)
#mesure=dmm.takeMeasurement()
#log.info('maasurement=%s',mesure)
