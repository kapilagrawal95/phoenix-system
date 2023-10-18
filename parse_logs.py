from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_success_rate(total_requests, successful_requests, total_utility, success_utility):

    # Create a new figure
    fig = go.Figure()

    # Calculate the success rate
    # success_rate = successful_requests / total_requests
    success_rate = {}
    for key in total_requests.keys():
        success_rate[key] = 100 * successful_requests[key] / total_requests[key]
    
    line_trace = go.Scatter(
        x=list(successful_requests.keys()),
        y=list(success_rate.values()),
        mode='lines',
        name='Success Rate (%)'
    )
    # Create a line trace for the success rate
    fig.add_trace(line_trace)
    
    utility_rate = {}
    for key in total_utility.keys():
        utility_rate[key] = 100 * success_utility[key] / total_utility[key]
        
    utility_trace = go.Scatter(
        x=list(success_utility.keys()),
        y=list(utility_rate.values()),
        mode='lines',
        name='Utility Rate (%)'
    )
    
    fig.add_trace(utility_trace)
    
    # Add text annotations to hover over the points
    for date, total_count, successful_count, percentage in zip(list(total_requests.keys()), list(total_requests.values()), list(successful_requests.values()), list(success_rate.values())):
        fig.add_trace(go.Scatter(
            x=[date],
            y=[success_rate[date]],
            # mode='markers',
            text=f'Total Requests: {total_count}\nSuccessful Requests: {successful_count}\nPercentage: {percentage}',
            hoverinfo='text',
            showlegend=False,
            marker=dict(
                color="blue",
                size=0
            )
        ))

    # Update the layout of the figure
    fig.update_layout(
        title='Success Rate of Requests',
        xaxis_title='Date and Time',
        yaxis_title='Success Rate (%)'
    )

    # Plot the figure
    fig.show()

resolution = 15 #Club every 15 seconds

request_counts = defaultdict(int)
success_counts = defaultdict(int)
total_utility = defaultdict(float)
utility = defaultdict(float)

logfile = "logs/second.log"
# Define resolution intervals (1s, 2s, 15s)

def assign_utility(wrk_name):
    UTILITIES = {"login": 10,
                 "get_settings": 0.1,
                 "update_settings": 0.1,
                 "get_project_list": 100,
                 "logout": 10,
                 "tag": 0.0001,
                 "socket.io/connect": 10,
                 "history": 1,
                 "document_diff": 1,
                 "update_text": 0.000001, # too frequently so need to sum it up
                 "spell_check": 0.000000001,
                 "file_upload": 10,
                 "compile": 0.1,
                 "get_compile_pdf": 10,
                 "get_contacts": 0.001,
                 "share_project": 10,
                 "update_cursor_position": 0.000001,
                 "create_tag": 0.0001
                 
                 }
    return UTILITIES[wrk_name]



# Convert log entries into datetime objects and extract success information
with open(logfile, "r") as logs:
    for line in logs:
        if "[Phoenix]" not in line:
            continue
        entry = line.replace("\n", "")
        parts = entry.split(" ")
        timestamp_str = " ".join(parts[0:2])
        success = parts[-2] == "True"
        workload = parts[-3]
        util_score = assign_utility(workload)
        timestamp = datetime.strptime(timestamp_str, "[%Y-%m-%d %H:%M:%S,%f]")
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        # Calculate the timestamp for 15-second intervals
        interval_timestamp = timestamp - timedelta(seconds=timestamp.second % resolution)
        # Convert the interval timestamp to a string
        interval_str = interval_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        # Increment the count for the corresponding second
        request_counts[interval_str] += 1
        if interval_str in total_utility:
            total_utility[interval_str] += util_score
        else:
            total_utility[interval_str] = 0
        
        if success:
            success_counts[interval_str] += 1
            if interval_str in utility:
                utility[interval_str] += util_score
            else:
                utility[interval_str] = 0
        # print(timestamp)
        # Iterate over resolutions and update counts
        # for resolution in resolutions:
        #     key = timestamp.replace(microsecond=0, second=(timestamp.second // resolution) * resolution)
        #     request_counts[key] += 1
        #     if success:
        #         success_counts[key] += 1
# print(request_counts)
# print(len(request_counts))
# print(success_counts)


assert len(request_counts) == len(success_counts)

plot_success_rate(request_counts, success_counts, total_utility, utility)
# utility_normalized = {}
# success_normalized = {}
# for key in request_counts.keys():
#     success_normalized[key] = 100 * success_counts[key] / request_counts[key]
    
# assert len(request_counts) == len(success_normalized)

# utility_normalized = {}
# for key in total_utility.keys():
#     utility_normalized[key] = 100 * utility[key] / total_utility[key]

# # df = pd.DataFrame(list(success_normalized.items()), columns=['Date', 'Success Normalized'])
# # df2 = pd.DataFrame(list(utility_normalized.items()), columns=['Date', 'Utility Normalized'])

# df = pd.DataFrame({'Date': list(success_normalized.keys()),
#                      'Total Requests': list(request_counts.values()),
#                      'Successful Requests': list(success_counts.values()),
#                      'Percentage Success': list(success_normalized.values())})


# # print(df)
# # Convert the 'Date' column to a datetime format
# df['Date'] = pd.to_datetime(df['Date'])
# # df2['Date'] = pd.to_datetime(df2['Date'])
# print(df.head())
# # Create an interactive time-series plot
# fig = px.line(df, x='Date', y='Percentage Success',
#               title='Interactive Time-Series Plot', color_discrete_sequence=['red'], 
#               labels={'Percentage Success': 'Success Percentage (%)'})
# # fig.add_trace(px.line(df2, x='Date', y='Utility Normalized', labels={'y': "Y2"}, color_discrete_sequence=['blue']).data[0])

# # fig.update_xaxes(title_text='Date')
# # fig.update_yaxes(title_text='Y-axes', range=[0, 100])

# # fig.update_traces(texttemplate='%{y:.2f}%<br>Total Requests: %{text}')

# # fig.update_traces(customdata=['Total Requests', 'Successful Requests'])

# # fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
# # for i, row in df.iterrows():
# #     fig.add_annotation(
# #         x=row['Date'],
# #         y=row['Total Requests'],
# #         text=row['Total Requests'],
# #         showarrow=False,
# #     )
# #     fig.add_annotation(
# #         x=row['Date'],
# #         y=row['Successful Requests'],
# #         text=row['Successful Requests'],
# #         showarrow=False,
# #     )

# # fig.update_layout(legend_title_text='Datasets')
# # fig.data[0].name = 'Dataset 1'
# # fig.data[1].name = 'Dataset 2'

# # fig.data[0].name = 'Dataset 1'
# # fig.data[1].name = 'Dataset 2'
# # Show the interactive plot in a web browser
# # fig.show()



