import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import socket
import time
from threading import Thread
import json
import pickle
import numpy as np

HOST = '192.168.4.65'
PORT = 65431
weather_data = []

start_time = time.time()
title_fontsize = 25
title_color = 'orange'
# Seconds ago:
X = 4
classification = 'Normal'
classifications = []

with open('weather_model.pkl', 'rb') as file:
    bst = pickle.load(file)

# Dash app setup
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='humidity-graph', style={'height': '425px'}),
    dcc.Graph(id='windspeed-graph', style={'height': '425px'}),
    dcc.Graph(id='temperature-graph', style={'height': '425px'}),
    html.Div(
        children=[
            html.Br(),
            html.H1(id='result_output', style={'color': '#18c429', 'font-size': 60})
        ],
        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'} ),

    dcc.Interval(
            id='interval-component',
            interval=500, # in milliseconds
            n_intervals=0
    )
])

@app.callback(
    [Output('humidity-graph', 'figure'),
     Output('windspeed-graph', 'figure'),
     Output('temperature-graph', 'figure'),
     Output('result_output', component_property='children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    global title_fontsize
    global title_color
    global weather_data
    global classification
    times = [entry[0] for entry in weather_data[-200:]]
    #temperatures = [entry[1] for entry in weather_data[-100:]]
    humidities = [entry[1] for entry in weather_data[-200:]]
    windspeeds = [entry[2] for entry in weather_data[-200:]]
    temperatures = [entry[3] for entry in weather_data[-200:]]

    # temperature_figure = {
    #     'data': [
    #         go.Scatter(x=times, y=temperatures, mode='lines+markers')
    #     ],
    #     'layout': {
    #         'title': 'Temperature over Time',
    #         # 'yaxis': {
    #         #     'range': [min(temperatures) - 0.35, max(temperatures) + 0.35]  # Adjusting the y-axis range for temperature
    #         # }
    #     }
    #}

    humidity_figure = {
        'data': [go.Scatter(x=times, y=humidities, mode='lines+markers')],
        'layout': {'title': {'text': 'Himidity over Time', 'font': {'size': title_fontsize, 'color': title_color}}}
    }

    windspeed_figure = {
       'data': [go.Scatter(x=times, y=windspeeds, mode='lines+markers')],
        'layout': {'title': {'text': 'Windspeed over Time', 'font': {'size': title_fontsize, 'color': title_color}}}
    }

    temperature_figure = {
       'data': [go.Scatter(x=times, y=temperatures, mode='lines+markers')],
        'layout': {'title': {'text': 'Temperature over Time', 'font': {'size': title_fontsize, 'color': title_color}}}
    }

    return humidity_figure, windspeed_figure, temperature_figure, classification

# def process_data_from_server(x):
#     a,b,c,d = x.split(",")
#     return a,b,c,d
def process_data_from_server(x):
    a, b, c = x.split(",")
    # if len(values) != 4:
    #     print("Unexpected data format:", x)
    #     return None, None, None, None
    # a, b, c, d = values
    return a, b, c

   


def my_client():
    global weather_data
    global classification
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # Start the Dash app in a separate thread
        dash_thread = Thread(target=app.run_server, args=(), kwargs={'debug': True, 'use_reloader': False})
        dash_thread.start()

        while True:
            current_time = time.time()
            local_time = time.localtime(current_time)
            human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            time_elapsed = current_time - start_time   

            data = s.recv(1024).decode('utf-8')
            print(data)
            if data == 'error,error,error':
                print('error data')
                continue


            try:
                humidity, windspeed, temperature = process_data_from_server(data)
            except:
                continue

            if ")" in windspeed:
                continue
            # print("Temperature {}".format(temperature))
            print("Humidity {}".format(humidity))
            print("Windspeed {}".format(windspeed))
            print("Temperature2 {}".format(temperature))
            current_time = time.time()
            local_time = time.localtime(current_time)
            human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            weather_data.append((human_readable_time, float(humidity), float(windspeed), float(temperature)))
            # float(windspeed)
            if len(weather_data) > X:
                #slopes = (np.array([weather_data[-X][1:2] + weather_data[-X][3]]) - np.array([weather_data[-1][1:2] + weather_data[-1][3]])) / X

                old_humidity, old_temperature = weather_data[-X][1], weather_data[-X][3]
                new_humidity, new_temperature = weather_data[-1][1], weather_data[-1][3]

                # Calculate the slopes
                humidity_slope = (new_humidity - old_humidity) / X
                temperature_slope = (new_temperature - old_temperature) / X

                # Combine the slopes into an array
                slopes = np.array([humidity_slope, temperature_slope])

                print(slopes)
                prediction_array = np.insert(slopes, [0,1,1], [float(humidity), float(windspeed), float(temperature)])
                prediction_array = prediction_array.reshape(1, -1)
                print(prediction_array)
                print(prediction_array.shape)
                prediction = bst.predict(prediction_array)
                condition_key = {0: 'Normal', 1: 'Cold blow', 2: 'Hot Blow', 3: 'Cold Object', 4: 'Humidifier'}
                classification = condition_key.get(list(prediction)[0])
                classifications.append(classification)
                print('---------------')
                print("**** Predicted class: ", prediction)
                print("**** Predicted condition: ", classification)
                print('---------------')
            
            if 0 < time_elapsed %  25 < 1 and time_elapsed > 10:
                with open('weather_data11.json', 'w') as json_file:
                    json.dump(weather_data, json_file, indent=4)
                print('===== saved ======')

if __name__ == '__main__':
    my_client()
