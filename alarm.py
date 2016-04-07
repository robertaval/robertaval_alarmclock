import configparser
import datetime
import time
import ledenet_api
import webcolors
import os

class alarmset:

    def __init__(self):
        self.list = []

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def __getitem__(self,index):
        if isinstance (index, int):
            return self.list[index]
        elif isinstance (index, str):
            return self[tuple(a.name for a in self).index(index)]
        else:
            return None

    def add(self, alarm):
        if self.exists(alarm.name):
            raise DuplicateNameError(alarm.name, ': this name allready exists')
        self.list.append(alarm)

    def remove(self, alarm):
        if self.exists(alarm.name):
            self.list.remove(alarm)

    def exists(self, name):
        return name in (a.name for a in self)

    def generate_name(self):
        # .generate_name() generates a name in the format alarm# with the first
        # integer available
        alarm_exists = True
        i = 0
        while alarm_exists:
            i += 1
            name ='alarm' + str(i)
            alarm_exists = self.exists(name)
        return name

    def run(self):
        ''' run checks the time every 10 secs and starts the alarm and the wake-up light
        if the current time matches the alarm time'''
        format = "%Y-%m-%d %H:%M"
        while True:
            now = datetime.datetime.now()
            nowstring = now.strftime(format)
            for a in self:
                next = a.next_alarm(now)
                if next != None:
                   # correct the time of the next alarm for the onset time of the color
                   #led strip
                   next -= datetime.timedelta(seconds=a.color_onset)
                   if next.strftime(format) == nowstring:
                       a.wakeup_light()
                       a.play_from_list()
            time.sleep(10)

    def gettrack(self):
        ''' gettrack()  return the name of the track that is currently playing'''
        track = None
        for a in self:
            if a.track != None:
                track = a.track
        return track

    def next_alarm(self, now):
        ''' next(now) returns the alarm object that is the
        nearest next alarm time'''
        newlist = []
        for a in self:
            if a.next_alarm(now) != None:
               newlist.append(a)
        newlist.sort(key= lambda a: a.next_alarm(now))
        return newlist[0] if len(newlist) >0 else None

    def load_alarms (self, filename = 'alarms.conf'):
        '''load all the alarms in an ini file
        '''
        # first open the file alarms using the module configparser
        # and collects a set of calendar recurrences
        file = configparser.ConfigParser()
        file.read(filename)

        # now loop through each section and determine what the next alarm is based
        # on the recurrences set (if any). Note that a recurrence set in the past
        # returns a date in the past.

        for section in file.sections():
            name = section
            time = datetime.datetime.strptime(file.get(section, 'time'),'%H:%M').time()

            days = tuple(file.get(section, 'days').replace(' ', '').upper().split(','))
            path = file.get(section, 'path')
            if file.has_option(section, 'date'):
                date = datetime.datetime.strptime(file.get(section, 'date'),'%d-%b-%Y').date()
            else:
                date = None
            active = file.getboolean(section, 'active')
            self.add(alarm(section, time, days, date, path, active))


    def save_alarms (self, filename):
        '''save all the alarms to the ini file'''

        file = configparser.ConfigParser()

        for a in self:
            file.add_section(a.name)
            file.set(a.name,'time', a.time.strftime('%H:%M'))
            file.set(a.name,'days', ', '.join(a.days))
            if a.date != None: file.set(a.name,'date', a.date.strftime('%d-%b-%Y'))
            active = 'True' if a.active else 'False'
            file.set(a.name,'active', active)
            file.set(a.name,'path', a.path)


        with open(filename,'w', encoding='utf-8') as fileout:
            file.write(fileout)

    def stop(self):
        for alarm in self:
            alarm.stop()




class alarm:

    dowlist = 'MO,TU,WE,TH,FR,SA,SU'.split(',')
    dow = {d:i for i,d in enumerate(dowlist)}
    def  __init__(self, name, time, days = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'), date = None, path = './playlist/',
                  active = True, color_onset = 300, duration = -1, color = 'FFFFFF' ):
        '''define an alarm. at the time of the alarm, a media file is played
        required parameters is time (datetime.time)
        optional parameters days, the days of the week for the alarm.
                            days is one or more of 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'
                            date is the date for a specific alarm. date overrides the days parameter
                            path is the path to media files
                            if active is True, the alarm will play otherwise it will not.  '''

        self.name =           name
        self.time =           time
        self.days =           days
        self.date =           date
        self.repeating =      True if date == None else False
        self.active =         active
        self.path =           path +'/'if path[-1] != '/' else path # add a / to the end of the path if not present
        self.color_onset =    color_onset # onset is the time before the alarm for sunrise
        self.duration = duration # duration of the alarm. -1 is manual off only
        self.color =          color
        self.bulb_ip =        '192.168.1.162'



        # these variables are not passed when initiating the alarm, but are used for housekeeping

        self.chkbox =         {d:b for b,d in zip(('checked' if t in self.days else '' for t in self.dowlist),self.dowlist)}
        # used by the module web.py to format the ceckboxes for the recurrence
        self.playing =        False
        self.track =          None
        self.blocking =       False # blocking is used to check if the player can


    def update_alarm(self, **kwargs):
        '''update the the alarm. the function takes 0 or more inputs from the list
           name, time, days, date, path and repeating
        '''
        self.name = kwargs.get('name', self.name)
        self.time = kwargs.get('time', self.time)
        self.days = kwargs.get('days', self.days)
        self.date = kwargs.get('date', self.date)
        self.repeating = kwargs.get('repeating', self.repeating)
        self.path = kwargs.get('path', self.path)
        self.active = kwargs.get ('active', self.active)
        self.color = kwargs.get('color', self.color)
        self.color_onset = kwargs.get('color_onset', self.color_onset)
        self.duration = kwargs.get('duration', self.duration)

        # housekeeping
        if self.path[-1] != '/':
            self.path += '/'
        self.chkbox =    {d:b for b,d in zip(('checked' if t in self.days else '' for t in self.dowlist),self.dowlist)}


    def next_alarm(self, now):
        '''alarm.next(now) returns the next occurence of an alarm after the input
        eg alarm(time(10,0,0)).next(datetime(2015,1,1,11,0,0))
        -> the next alarm at 10am if today is 11:00AM on Jan 1st 2015
        will return
        datetime(2015,1,2,10,0,0) -> 10:00 AM on Jan 2nd 2015'''

        #offset now by 60 seconds so that next(now) = now
        now += datetime.timedelta(0,-60)

        # first determine the start date...
        # which is either a specific date (ie self.date != None
        # tomorrow (if now.time is past alarm.time
        # or today (in all other cases)
        if not self.active:
            return None
        if not self.repeating:
            date = self.date
            if self.date == None or datetime.datetime.combine(date, self.time) < now:
                return None
        elif now.time() > self.time:
            date = now.date() + datetime.timedelta(1)
        else:
            date = now.date()

        next_date = datetime.datetime.combine(date, self.time)

        #map the weekday numbers to the days in alarm.days, so that 'MO' = 0, TU = 1
        #then increment the current date until the current dow matches a day in alarm.days

        wkdays = set(alarm.dow[x] for x in self.days)
        while next_date.weekday() not in wkdays:
            next_date += datetime.timedelta(1)
        return next_date

    def generate_playlist(self, path=None, ext = ('.mp3','.wav','.flac')):
        '''generates a list of files in path
        that ends with extension ext (default = .mp3, .wav and .flac'''
        if path == None:
            path = self.path
        return sorted(list(filter(lambda x: x.endswith(ext), os.listdir(path))))

    def play(self, track):

        from mplayer import Player, CmdPrefix
        if not self.playing:
            self.playing = True
            self.track = track
            # initiate the player
            Player.cmd_prefix = CmdPrefix.PAUSING_KEEP
            self.player = Player()

        self.player.loadfile(self.path + track)
        self.player.volume = 1 # set volume really low. default = max = 100
        time.sleep(0.2) # to allow the player to initialise properly

    def play_from_list(self):
        if not self.playing:
            self.blocking = True
            playlist = self.generate_playlist()
            while playlist != [] and self.blocking:
                  track = playlist.pop(0)
                  self.play(track)
                  while self.player_active():
                      time.sleep(1)
        self.turn_off_light()


    def wakeup_light(self):
        r, g, b = webcolors.hex_to_rgb('#'+self.color)
        bulb = ledenet_api.bulb(self.bulb_ip)
        bulb.gradual(r,g,b,self.color_onset)


    def player_active(self):
        if self.playing:
            return self.player.time_pos != None
        else:
            return False


    def stop(self):
        self.turn_off_light()
        self.track = None
        self.blocking = False
        if self.playing:
            self.playing = False
            self.player.quit()
        time.sleep(1)

    def turn_off_light(self):
        bulb = ledenet_api.bulb(self.bulb_ip)
        bulb.turn_off()


class DuplicateNameError(LookupError):
    pass
