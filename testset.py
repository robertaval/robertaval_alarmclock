import time, datetime
import unittest
import alarm


format = "%a %d-%b-%Y %H:%M"
current_time = datetime.datetime(2015,4,4,16,4,0) #april 4 2015 16:04

default     =  {'name' : 'default', 'time' : datetime.time(12,0,0), 'days' : ('MO','TU','WE','TH','FR','SA','SU'),
                'date' : None, 'path' : './', 'date' : None, 'active' : True}

alarms_list = ({'name' : 'current', 'time' : datetime.time(16,4,0)}, # the current time
               {'name' : 'alarm1',  'time' : datetime.time(11,0,0)}, # every day at 11 am
               {'name' : 'alarm2',  'time' : datetime.time(9,0,0),  'days' : ('MO','TU')},#monday and tuesday an 9 am
               {'name' : 'alarm3',  'time' : datetime.time(22,0,0), 'days' : ('WE','TU','SA')}, # tuesday, wednesday, sunday at 10 pm
               {'name' : 'christmas','time' : datetime.time(21,0,0), 'date' : datetime.date(2015,12,24)}, # 9pm on christmas eve
               {'name' : 'past',    'time' : datetime.time(12,0,0), 'date' : datetime.date(1999,12,31)}, # noon on dec 31 1999 --> in the past
               {'name' : 'path',    'time' : datetime.time(12,0,0), 'path' : '/media/music/1Kindermuziek/K3/K3-Eyo(2011)MP3 Nlt-release/'},
               {'name' : 'n_active','time' : datetime.time(12,0,0), 'active' : False},
                default)

alarm_times = {'current': datetime.datetime(2015,4,4,16,4,0),
               'alarm1':  datetime.datetime(2015,4,5,11,0,0),
               'alarm2':  datetime.datetime(2015,4,6,9,0,0),
               'alarm3':  datetime.datetime(2015,4,4,22,0,0),
               'christmas':  datetime.datetime(2015,12,24,21,0,0),
               'past':    None,
               'path':    datetime.datetime(2015,4,5,12,0,0),
               'n_active':None,
               'default': datetime.datetime(2015,4,5,12,0,0)}

root_playlist = ['engeltjes.mp3']
path_playlist = ['01 Eyo.mp3', '02 Hallo K3.mp3', '03 Willem - Alexander.mp3', '04 Smoorverliefd.mp3',
                 '05 K3 - Airlines.mp3', '06 Beroemd.mp3', '07 Meiden Van De Brandweer.mp3',
                 '08 Verstoppertje.mp3', '09 Telepathie.mp3', '10 Dubbeldekkertrein.mp3',
                 '11 Bel Me Ringeling.mp3', '12 Cowboys En Indianen.mp3']


class testcases_alarm(unittest.TestCase):
    '''test all cases of working alarms'''

    def are_all_the_vars_present(self, alarm, default, **a):
            self.assertEqual(a.get('name'),                            alarm.name)
            self.assertEqual(a.get('time'),                            alarm.time)
            self.assertEqual(a.get('date',      default['date']),      alarm.date)
            self.assertEqual(a.get('days',      default['days']),      alarm.days)
            self.assertEqual(a.get('path',      default['path']),      alarm.path)
            self.assertEqual(a.get('active',    default['active']),    alarm.active)

    def test_create_alarm(self):
        '''create a basic alarm'''
        for a in alarms_list:
            al = alarm.alarm(**a)
            self.are_all_the_vars_present(al, default, **a)

    def test_edit_alarm_correct(self):
        '''update an alarm with the parameters of another alarm'''
        if len(alarms_list) < 2: # need at least 2 alarms for this test
            return
        for i in range(len(alarms_list)-1):
           a1 = alarms_list[i]
           a2 = alarms_list[i+1]
           al = alarm.alarm(**a1)
           copy_of_default = default.copy()
           self.are_all_the_vars_present(al, copy_of_default, **a1)
           al.update_alarm(**a2)
           copy_of_default.update(a1)
           self.are_all_the_vars_present(al, copy_of_default, **a2)

    def test_is_the_next_alarm_correct(self):
        '''test next_alarm'''
        for a in alarms_list:
            myalarm = alarm.alarm(**a)
            nexttime = alarm_times[myalarm.name]
            self.assertEqual(myalarm.next_alarm(current_time), nexttime)

    def test_add_alarm_correct_alarms(self):
        '''create a set of alarms'''
        alarms = alarm.alarmset()
        for a in alarms_list:
            alarms.add(alarm.alarm(**a))
            al = alarms[-1]
            self.are_all_the_vars_present(al, default, **a)
            self.assertEqual(alarms.exists(a['name']), True)

    def test_remove_alarm(self):
        '''remove an alarm from a set'''
        alarms = alarm.alarmset()
        for a in alarms_list:
            name = a['name']
            alarms.add(alarm.alarm(**a))
            self.assertEqual(alarms.exists(name), True)
            alarms.remove(alarms[name])
            self.assertEqual(alarms.exists(name), False)

    def test_the_next_alarm_in_set(self):
        '''alarmset next_alarm'''
        alarms = alarm.alarmset()
        for a in alarms_list:
            alarms.add(alarm.alarm(**a))
        self.assertEqual(alarms.next_alarm(current_time).next_alarm(current_time), current_time)

    def test_generate_playlist(self):
        '''based on the path, generate a list of files'''
        alarm1 = alarm.alarm(**alarms_list[1])
        path = alarm.alarm(**alarms_list[6])

        self.assertEqual(alarm1.generate_playlist(), root_playlist)
        self.assertEqual(path.generate_playlist(), path_playlist)

    def test_play_a_song(self):
        '''play a song form file'''
        alarm1 = alarm.alarm(**alarms_list[1])
        self.assertEqual(alarm1.playing, False)
        self.assertEqual(alarm1.blocking, False)
        self.assertEqual(alarm1.player_active(), False)
        alarm1.play(root_playlist[0])
        time.sleep(0.2)
        self.assertEqual(alarm1.playing, True)
        self.assertEqual(alarm1.blocking, False)
        self.assertEqual(alarm1.player_active(), True)
        alarm1.stop()

    def test_save_and_load_alarms(self):
        alarms_1 = alarm.alarmset()
        alarms_2 = alarm.alarmset()
        for a in alarms_list:
            alarms_1.add(alarm.alarm(**a))
        alarms_1.save_alarms('test_config.file')
        alarms_2.load_alarms('test_config.file')
        for a_1, a_2 in zip (alarms_1, alarms_2):
            self.assertEqual(a_1.name, a_2.name)
            self.assertEqual(a_1.time, a_2.time)
            self.assertEqual(a_1.date, a_2.date)
            self.assertEqual(a_1.days, a_2.days)
            self.assertEqual(a_1.path, a_2.path)
            self.assertEqual(a_1.active, a_2.active)


    def test_player_active(self):
        pass

    def test_stop(self):
        pass



if __name__ == '__main__':
    unittest.main()
