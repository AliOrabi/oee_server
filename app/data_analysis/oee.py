from app.default.models import Activity, ActivityCode, ScheduledActivity

from config import Config


def get_machine_runtime(machine_id, time_start, time_end):
    """ Takes a machine id and two times, and returns the amount of time the machine was running """
    # Get all of the activities for the machine between the two given times, where the machine is up
    activities = Activity.query \
        .filter(Activity.machine_id == machine_id) \
        .filter(Activity.machine_state == Config.MACHINE_STATE_RUNNING) \
        .filter(Activity.timestamp_end >= time_start) \
        .filter(Activity.timestamp_start <= time_end).all()

    run_time = 0
    for act in activities:
        run_time += (act.timestamp_end - act.timestamp_start)
    return run_time


def get_activity_dict(time_start, time_end, machine_id=None, user_id=None, use_description_as_key=False):
    """ Returns a dict containing the total duration of each activity_code between two timestamps in the format:
    activity_code_id: duration(seconds) e.g. 1: 600
    If use_code_description is passed, the activity_code_id is replaced with its description e.g. uptime: 600"""
    if user_id:
        # Get all of the activities for a user
        activities = Activity.query \
            .filter(Activity.user_id == user_id) \
            .filter(Activity.timestamp_end >= time_start) \
            .filter(Activity.timestamp_start <= time_end).all()
    elif machine_id:
        # Get all of the activities for a machine
        activities = Activity.query \
            .filter(Activity.machine_id == machine_id) \
            .filter(Activity.timestamp_end >= time_start) \
            .filter(Activity.timestamp_start <= time_end).all()
    else:
        # Get all the activities
        activities = Activity.query \
            .filter(Activity.timestamp_end >= time_start) \
            .filter(Activity.timestamp_start <= time_end).all()

    # Initialise the dictionary that will hold the totals
    activities_dict = {}
    act_codes = ActivityCode.query.all()
    for code in act_codes:
        if use_description_as_key:
            activities_dict[code.short_description] = 0
        else:
            activities_dict[code.id] = 0

    for act in activities:
        # If the activity extends past the  start or end, crop it short
        if act.timestamp_start < time_start:
            start = time_start
        else:
            start = act.timestamp_start
        if act.timestamp_end > time_end:
            end = time_end
        else:
            end = act.timestamp_end

        # Add the time to the dict
        if use_description_as_key:
            activities_dict[act.activity_code.short_description] += (end - start)
        else:
            activities_dict[act.activity_code_id] += (end - start)
    return activities_dict


def get_schedule_dict(machine_id, time_start, time_end):
    """ Takes a machine id and two times, and returns a dict with:
    scheduled_run_time
    scheduled_down_time
    unscheduled_time"""
    # Get all the scheduled activities
    activities = ScheduledActivity.query \
        .filter(ScheduledActivity.machine_id == machine_id) \
        .filter(ScheduledActivity.timestamp_end >= time_start) \
        .filter(ScheduledActivity.timestamp_start <= time_end).all()

    total_time = time_end - time_start
    scheduled_run_time = 0
    scheduled_down_time = 0
    unscheduled_time = 0
    for act in activities:
        # If the activity extends past the  start or end, crop it short
        if act.timestamp_start < time_start:
            start = time_start
        else:
            start = act.timestamp_start
        if act.timestamp_end > time_end:
            end = time_end
        else:
            end = act.timestamp_end

        if act.scheduled_machine_state == Config.MACHINE_STATE_RUNNING:
            scheduled_run_time += (end - start)
        elif act.scheduled_machine_state == Config.MACHINE_STATE_OFF:
            scheduled_down_time += (end - start)
        else:
            unscheduled_time += (end - start)

    # Add any time unaccounted for
    unscheduled_time += (total_time - (scheduled_down_time + scheduled_run_time))

    return {"scheduled_run_time": scheduled_run_time,
            "scheduled_down_time": scheduled_down_time,
            "unscheduled_time": unscheduled_time}


def calculate_activity_percent(machine_id, activity_code_id, time_start, time_end):
    """ Returns the percent of time a certain activity code takes up for a certain machine over two timestamps"""
    activities = Activity.query \
        .filter(Activity.machine_id == machine_id) \
        .filter(Activity.activity_code_id == activity_code_id) \
        .filter(Activity.timestamp_end >= time_start) \
        .filter(Activity.timestamp_start <= time_end).all()

    total_time = time_end - time_start
    activity_code_time = 0
    for act in activities:
        activity_code_time += (act.timestamp_end - act.timestamp_start)

    if activity_code_time == 0:
        return 0
    else:
        return (total_time / activity_code_time) * 100


def get_oee(machine_id, time_start, time_end):
    """ Takes a machine id and two times, and returns the machine's OEE figure as a percent
    Note: currently only calculates availability, not performance and quality which are part of the oee calculation"""
    runtime = get_machine_runtime(machine_id, time_start, time_end)
    scheduled_uptime = get_schedule_dict(machine_id, time_start, time_end)["scheduled_run_time"]

    availability = runtime / scheduled_uptime
    return availability * 100