import alarm
import time
import datetime
import threading
from bottle import route, request, run, template, static_file

format = "%a %d-%b-%Y %H:%M"
timeformat = "%H:%M"
dateformat = "%Y-%m-%d"
alarms = alarm.alarmset()

def render_topbar(alarms):
    '''renders the top bar od the alarm from a template '''
    topbar = 'content/topbar.tpl'
    now = datetime.datetime.now()
    msg = ""
    track = alarms.gettrack()
    next_alarm = alarms.next_alarm(now).next_alarm(now)
    if track != None:
        msg = track
    elif next_alarm != None:
        msg = "next alarm set for " + next_alarm.strftime(format)
    else:
        msg = "no alarm set"
    return template(topbar, current_time = now.strftime(timeformat), extra_info = msg)


def render_alarm(alarm):
    alarm_template = 'content/alarm.tpl'
    mindate = datetime.datetime.now().strftime(dateformat)
    if alarm.date == None:
        formdate = ""
    else :
        formdate = alarm.date.strftime(dateformat)

    return template(alarm_template,
                          alarm_id  = alarm.name,
                          name      = alarm.name,
                          time      = alarm.time.strftime(timeformat),
                          days      = ', '.join(alarm.days) if alarm.repeating else formdate,
                          MO        = alarm.chkbox['MO'],
                          TU        = alarm.chkbox['TU'],
                          WE        = alarm.chkbox['WE'],
                          TH        = alarm.chkbox['TH'],
                          FR        = alarm.chkbox['FR'],
                          SA        = alarm.chkbox['SA'],
                          SU        = alarm.chkbox['SU'],
                          date      = formdate,
                          color     = alarm.color,
                          active    = 'checked' if alarm.active else '',
                          repeating = 'checked' if alarm.repeating else '',
                          min_date  = mindate)


def render_page(alarms):
    alarm_page = 'content/alarm_page.tpl'
    alarms_content = ""
    top_bar = '<div id="topbar">'+render_topbar(alarms)+'</div>'
    for alarm in alarms:
        alarms_content += '<div class="alarm" id="' + alarm.name + '">'
        alarms_content += render_alarm(alarm)
        alarms_content += '</div>'
    return template(alarm_page, topbar = top_bar, alarms = alarms_content)


@route('/alarm')
def page_get():
    print ('returning main page')
    return render_page(alarms)

@route('/alarm/<parameters>')
def parse_api_string(parameters):
    error_returnstring = '''
       format for parameters is
       alarm_id=<name>
       action=stop|play|add|delete|update|list|info|exists|gen_name|wakeup_light

       eg <url>/alarm_id=alarm1&action=info

       aditional parameters for the action update
       time=hh:mm
       name=<name> -> updating name will update alarm_id. It must be unique
       days=MO,TU,WE,TH,FR,SA,SU -> one or more of the previous, comma seperated
       color=rrggbb -> where rrggbb is the hexcolorcode for the color
       color_onset=<secs>  -> seconds before the daylight effect starts
       date=YYYY-MM-DD
       active=true|false
       repeating=true|false
    '''

    print (parameters)
    response = ""
    params = {}
    web_response = "nothing"

    try:
        params = dict(a.split('=') for a in parameters.split('&'))
        action = params['action'].lower()
    except:
        return error_returnstring

    if 'alarm_id'in params:
        name = params['alarm_id']
    id_present = 'alarm_id' in params and alarms.exists(params['alarm_id'])

    if action == 'stop':
        response +='stopping all playing alarms'
        alarms.stop()
    elif action == 'add' and 'alarm_id' in params:
        response +='adding alarm '+ name
        time = datetime.datetime.now()
        alarms.add(alarm.alarm(name, time, active = False))
        response += name +' at ' + time.strftime(format)
        web_response = render_alarm(alarms[name])
    elif action == 'play' and id_present:
        play_button_pressed(name)
        response += 'playing '+ name +' '+  alarms[name].track
    elif action == 'delete' and id_present:
        delete_alarm_web(name)
    elif action == 'update' and id_present:
        if 'name' in params:
            newName = params['name']
        else:
            newName = params['alarm_id']
        update_alarm_web(params)
        response += 'updated ' + name
        response += ' new id =' + newName
        web_response = render_alarm(alarms[newName])
    elif action == 'update_time':
        response += 'updating_time'
        web_response = render_topbar(alarms)
    elif action == 'list':
        response += 'listing alarms'
        web_response = alarm_list_web(alarms)
    elif action == 'info' and id_present:
        response += 'info on alarm ' + name
        web_response = alarm_info_web(alarms[name])
    elif action == 'exists' and alarm_id in params:
        response += 'exists '+ alarm_id
        web_response = 'true' if alarms.exists(params[alarm_id]) else 'false'   
    elif action == 'gen_name':
        name = alarms.generate_name()
        response += 'name ' +name
        web_response = name
    elif action == 'wakeup_light' and id_present:
        wakeup_button_pressed(name)
        response += 'wakeup light ' + name + ' color ' + alarms[name].color
        response += ' duration ' + str(alarms[name].color_onset)

    else:
        response += 'arguments not recognized'
        web_response = error_returnstring
    print (response)
    return web_response

@route('/<filename:re:.*\.(html|css|js)$>')
def static_file_return(filename):
    return static_file(filename, root='content')

def update_alarm_web(params):
    alarm_vars = {}
    for k in params:
        if k == 'name' and not alarms.exists(params[k]): #prevent overwriting an existing name
            alarm_vars['name'] = params['name']
        elif k == 'time':
            try:
                alarm_vars['time'] = datetime.datetime.strptime(params['time'],timeformat).time()
            except ValueError:
                continue
        elif k == 'date':
            if params['date'] == "":
                alarm_vars['date'] = None
            else:
                try:
                    alarm_vars['date'] = datetime.datetime.strptime(params['date'],dateformat).date()
                except ValueError:
                    continue
        #days is a list of weekdays. Loop through the list and check if it
        #matches MO,TU,etc. if it does, add to the dict alarm_vars
        #otherwise ignore it.
        elif k == 'days':
            dayslst= 'MO,TU,WE,TH,FR,SA,SU'.split(',')
            params_days = params['days'].upper().split(',')
            for d in params_days:
                if d not in dayslst:
                    params_days.remove(d)
            alarm_vars['days'] = tuple(params_days)
        elif k == 'color':
            alarm_vars['color'] = params['color']
        elif k=='color_onset':
            alarm_vars['color_onset'] = int(params['color_onset'])
        elif k == 'active':
            alarm_vars['active'] = params['active'].lower() in ('true','t','1')
        elif k == 'repeating':
            alarm_vars['repeating'] = params['repeating'].lower() in ('true','t','1')

#    for k in alarm_vars:
#        print (k, ':', alarm_vars[k])

    # check if alarm_id exists and update that alarm
    if alarms.exists(params['alarm_id']):
        alarms[params['alarm_id']].update_alarm(**alarm_vars)
        alarms.save_alarms('alarms.conf')


def alarm_info_web(alarm):

    response = "<name={name}><time={time}><days={days}><date={date}><repeating={rept}><active={act}>"
    return response.format(name = alarm.name,
                           time = alarm.time.strftime(timeformat),
                           date = alarm.date.stftime(dateformat) if alarm.date != None else 'none',
                           days = ','.join(alarm.days),
                           rept = 'true' if alarm.repeating else 'false',
                           act  = 'true' if alarm.active else 'false')

def alarm_list_web(alarms):
    response = ""
    for a in alarms:
        response +='<' + a.name + '>'
    return response


def delete_alarm_web(name):
    if alarms.exists(name):
        alarms.remove(alarms[name])
        print('deleted', name)

def play_button_pressed(id):
    alarmthread = threading.Thread(target=alarms[id].play_from_list, args=())
    alarmthread.daemon = True
    alarmthread.start()

def wakeup_button_pressed(id):
    alarmthread = threading.Thread(target=alarms[id].wakeup_light, args=())
    alarmthread.daemon = True
    alarmthread.start()




def alarm_main():
    alarms.load_alarms('alarms.conf')
    alarmthread = threading.Thread(target=alarms.run, args=())
    alarmthread.daemon = True
    alarmthread.start()
    print('starting alarm')
    run (host='0.0.0.0', port=8080, debug=True)
    return print ('exiting')

alarm_main()

