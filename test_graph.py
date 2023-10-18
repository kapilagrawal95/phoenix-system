import plotly.graph_objects as go

def plot_success_rate(total_requests, successful_requests):

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

    # Add text annotations to hover over the points
    for date, total_count, successful_count in zip(list(total_requests.keys()), list(total_requests.values()), list(successful_requests.values())):
        fig.add_trace(go.Scatter(
            x=[date],
            y=[success_rate[date]],
            # mode='markers',
            text=f'Total Requests: {total_count}\nSuccessful Requests: {successful_count}',
            hoverinfo='text',
            showlegend=False,
            marker=dict(
                color="blue"
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

if __name__ == '__main__':

    # Create two sample dictionaries
    total_requests = {
        '2023-10-17 23:00:00': 100,
        '2023-10-17 23:01:00': 90,
        '2023-10-17 23:02:00': 80
    }

    successful_requests = {
        '2023-10-17 23:00:00': 90,
        '2023-10-17 23:01:00': 85,
        '2023-10-17 23:02:00': 75
    }

    # Plot the success rate
    plot_success_rate(total_requests, successful_requests)