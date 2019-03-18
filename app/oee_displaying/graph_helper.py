from plotly.offline import plot
from plotly.graph_objs import Layout
from datetime import datetime
from app.default.models import Activity, Machine, UPTIME_CODE, UNEXPLAINED_DOWNTIME_CODE, ERROR_1_CODE

import plotly
import plotly.figure_factory as ff


def create_machine_gantt(machine, graph_start, graph_end):
    """ Create a gantt chart of the usage of a single machine, between the two timestamps provided"""

    # todo dont rely on hardcoded codes eg "unexplained"

    # Get the machine's activities between the two times
    activities = Activity.query \
        .filter(Activity.machine_id == machine.id) \
        .filter(Activity.timestamp_end >= graph_start) \
        .filter(Activity.timestamp_start <= graph_end).all()
    if len(activities) == 0:
        return "No machine activity between these times"
    if machine is None:
        return "This machine does not exist"

    # Add each activity to a dictionary, to add to the graph
    df = []
    for activity in activities:
        # If the activity extends past the  start or end, crop it short
        if activity.timestamp_start < graph_start:
            start = graph_start
        else:
            start = activity.timestamp_start
        if activity.timestamp_end > graph_end:
            end = graph_end
        else:
            end = activity.timestamp_end
        df.append(dict(Task=activity.code.short_description,
                       Start=datetime.fromtimestamp(start),
                       Finish=datetime.fromtimestamp(end),
                       Code=activity.activity_code,
                       Activity_id=activity.id,
                       hoverinfo="test"))

    graph_title = "{machine_name} OEE".format(machine_name=machine.name)
    colours = {UNEXPLAINED_DOWNTIME_CODE: 'rgb(128, 128, 128)',
               UPTIME_CODE: 'rgb(0, 255, 128)',
               ERROR_1_CODE: 'rgb(255,64,0)',
               4: 'rgb(255,0,0)',
               5: 'rgb(255,255,0)'}
    fig = ff.create_gantt(df,
                          title=graph_title,
                          group_tasks=True,
                          colors=colours,
                          index_col='Code',
                          bar_width=0.4,
                          show_colorbar=True,
                          width=1800)

    # layout = Layout()
    # layout.xaxis.rangeselector.visible = False
    # fig['layout'] = layout

    # Hide the range selector
    fig['layout']['xaxis']['rangeselector']['visible'] = False
    return plot(fig, output_type="div", include_plotlyjs=True)


def create_all_machines_gantt(graph_start, graph_end):
    """ Creates a gantt plot of OEE for all machines in the database between given times"""
    machines = Machine.query.all()
    if len(machines) == 0:
        return "No machines found"
    df = []
    for machine in machines:
        activities = Activity.query \
            .filter(Activity.machine_id == machine.id) \
            .filter(Activity.timestamp_end >= graph_start) \
            .filter(Activity.timestamp_start <= graph_end).all()
        for activity in activities:
            # Don't show values outside of graph time range
            if activity.timestamp_start < graph_start:
                start = graph_start
            else:
                start = activity.timestamp_start
            if activity.timestamp_end > graph_end:
                end = graph_end
            else:
                end = activity.timestamp_end

            # This graph only deals with uptime and not-uptime
            if activity.activity_code == UPTIME_CODE:
                code = 1
            else:
                code = 2
            # Add the activity as a dict to the data fields list
            df.append(dict(Task=machine.name,
                           Start=datetime.fromtimestamp(start),
                           Finish=datetime.fromtimestamp(end),
                           Code=code))
    graph_title = "All machines OEE"
    colours = {1: 'rgb(0, 200, 64)', 2: 'rgb(255,32,0)'}
    fig = ff.create_gantt(df,
                          title=graph_title,
                          group_tasks=True,
                          colors=colours,
                          index_col='Code',
                          bar_width=0.4,
                          width=1800)

    # Hide the range selector
    fig['layout']['xaxis']['rangeselector']['visible'] = False
    return plot(fig, output_type="div", include_plotlyjs=True)


def create_shift_end_gantt(machine, activities):
    """ Create a gantt chart of the usage of a single machine, between the two timestamps provided"""

    # todo dont rely on hardcoded codes eg "unexplained"

    if len(activities) == 0:
        return "No machine activity between these times"
    if machine is None:
        return "This machine does not exist"


    # Add each activity to a dictionary, to add to the graph
    # Do this in two separate loops so that the entries requiring explanation are first in the dictionary,
    # putting them on the upper level in the graph
    df = []
    annotations = []
    for act in activities:
        if act.explanation_required:
            task = "Explanation<br>Required"
            start = act.timestamp_start
            end = act.timestamp_end
            df.append(dict(Task=task,
                           Start=datetime.fromtimestamp(start),
                           Finish=datetime.fromtimestamp(end),
                           Code=act.explanation_required,
                           Activity_id=act.id,
                           hoverinfo="test"))
            # Javascript relies on the first character being the ud_index, so alter the script accordingly
            text = "{start}<br>Explanation<br>Required".format(
                start=datetime.fromtimestamp(act.timestamp_start).strftime('%H:%M'))
            position = datetime.fromtimestamp((start + end) / 2)
            annotations.append(dict(x=position, y=1.7, text=text, showarrow=False, font=dict(color='black')))
    for act in activities:
        if not act.explanation_required:
            task = "Uptime"
            start = act.timestamp_start
            end = act.timestamp_end
            df.append(dict(Task=task,
                           Start=datetime.fromtimestamp(start),
                           Finish=datetime.fromtimestamp(end),
                           Code=act.explanation_required,
                           Activity_id=act.id,
                           hoverinfo="test"))



    colours = {True: 'rgb(255, 0, 0)',
               False: 'rgb(0, 255, 128)'}
    fig = ff.create_gantt(df,
                          title="",
                          group_tasks=True,
                          colors=colours,
                          index_col='Code',
                          bar_width=0.4,
                          show_colorbar=False,
                          width=1800)

    # Create a layout object using the layout automatically created
    layout = Layout(fig['layout'])

    layout.annotations = annotations
    layout.showlegend = False
    layout.yaxis.showticklabels = False
    layout.xaxis.rangeselector.visible = False
    layout.xaxis.showline = True

    layout.autosize = False
    # layout.width = 1200
    # layout.height = 300
    layout.margin = dict(l=0, r=0, b=50, t=0, pad=0)

    # Pass the changed layout back to fig
    fig['layout'] = layout

    config = {'responsive': True}




    #fig['layout'].update(responsive=True, autosize=False, width=1200, height=300, margin=dict(l=110, r=50, b=50, t=50, pad=4))
    return plot(fig, output_type="div", include_plotlyjs=True, config=config)


def sort_activities(act):
    return act.explanation_required
