import json

import datetime

from db_repository import create_client, basic_query

client = create_client()


def get_bus_schedules():
    with open('./bus_schedules.json', encoding='utf-8') as json_file:
        return json.load(json_file)


week_days = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}


def get_bus_stops_by_day(cur_day, schedule_data):
    weekday_schedules = schedule_data['WeekdaySchedules']
    for weekdaySchedule in weekday_schedules:
        from_day = week_days[weekdaySchedule['FromDay'].lower()]
        to_day = week_days[weekdaySchedule['ToDay'].lower()]
        if from_day <= cur_day <= to_day:
            return weekdaySchedule['Stops']


def get_current_time_arrival_times(stops, stop_id):
    for stop in stops:
        if stop['StopId'] == str(stop_id):
            return stop['ArriveTimes']


def get_current_time_by_arrival(arrival_times_string):
    current_date = datetime.datetime.now()

    arrival_times = arrival_times_string.split(',')

    closest_date = None

    for tm in arrival_times:

        tm_date = datetime.datetime(current_date.year, current_date.month, current_date.day,
                                    hour=int(tm.split(':')[0]) % 24,
                                    minute=int(tm.split(':')[1]) % 60
                                    )
        if closest_date is None:
            closest_date = tm_date
        else:
            if current_date < tm_date < closest_date:
                closest_date = tm_date

    return closest_date


def get_bus_stop_time(current_bus_data, stop_id):
    curr_day = datetime.datetime.today().weekday()
    forward_stops = get_bus_stops_by_day(curr_day, current_bus_data['forward'])
    backward_stops = get_bus_stops_by_day(curr_day, current_bus_data['backward'])

    arrival_times = ''

    if forward_stops is not None:
        res_arrival_times = get_current_time_arrival_times(forward_stops, stop_id)
        if res_arrival_times is not None:
            arrival_times = res_arrival_times

    if backward_stops is not None:
        res_arrival_times = get_current_time_arrival_times(backward_stops, stop_id)
        if res_arrival_times is not None:
            arrival_times = res_arrival_times

    if arrival_times is not None:
        return get_current_time_by_arrival(arrival_times)
    else:
        return None


def get_live_schedule_data(request):
    # bus_id = 137
    #
    # live_bus_stops = ['1472', '2738', '2736', '3156', '1483']
    #
    # schedule_bus_stops = ['1472', '2738']

    bus_id = request.args.get('bus_id')
    schedule_bus_stops = json.loads(request.args.get('schedule_bus_stops'))
    live_bus_stops = json.loads(request.args.get('live_bus_stops'))

    bus_schedules = get_bus_schedules()

    bus_data = bus_schedules[str(bus_id)]

    schedule_bus_stop_time_1 = get_bus_stop_time(bus_data, schedule_bus_stops[0])
    schedule_bus_stop_time_2 = get_bus_stop_time(bus_data, schedule_bus_stops[1])

    live_bus_stops_results = {}

    for live_stop_id in live_bus_stops:
        result = basic_query(client, bus_id, live_stop_id)[0]
        live_bus_stops_results[live_stop_id] = {
            'bus_number': result.get('bus_number'),
            "stop_id": result.get('stop_id'),
            "created": result.get('created').timestamp()
        }

    final_result = {
        'schedule_bus_stop_times': {
            schedule_bus_stops[0]: schedule_bus_stop_time_1.timestamp(),
            schedule_bus_stops[1]: schedule_bus_stop_time_2.timestamp()
        },
        'live_bus_stops_results': live_bus_stops_results
    }

    print(json.dumps(final_result))

    return json.dumps(final_result)


# get_live_schedule_data(1)
