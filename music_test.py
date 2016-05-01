import alarm

alarms = alarm.alarmset()
alarms.load_alarms('alarms.conf')

alarms[0].play('playlist/engeltjes.mp3')
