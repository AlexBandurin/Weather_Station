# Weather_Station

## Project Overview
Created an analytical platform for detecting various room conditions using a raspberry pi, weather sensors, and machine learning for multiclass classification.
Output is plotted and the prediction is displayed in a Plotly Dash application in real-time.

Variables used: Humidity, Windspeed, Temperature
Conditions evaluated: Cold Object (cold object placed next to the sensors), Humidifier (humidifier turned on in close proximity to the sensors), 
Cold blow (cold wind on the sensors), and Hot Blow (hot wind on the sensors).

## Hardware

- Rasberry Pi 3
- 5V Power source
- Ethernet cable: For connecting the Raspberry Pi to the network. 
- Breadboard & wires: To wire all the components together. 
- BME280: An environmental sensor with temperature, barometric pressure and humidity. For the purposes of this project, it was used for humidity measurement only.
- Wind Sensor Rev. C (by Modern Device): A thermal anemometer with an analog output. Used for wind speed and temperature measurements.

<p align="center">
<img src="https://github.com/AlexBandurin/Weather_Station/blob/master/Setup.PNG"  width="100%" height="80%">
  
## Data Collection and Feature Engineering
To acquire the data, the system has been subjected to all the above conditions, with the sensor readings recorded. The time-series data was then manually labeled such that
the appropriate condition is indicated for a given time interval. 

For a better prediction, a feature indicating the rate of change of each variable has been added to the dataset, totalling 3 additional features. These are a good indicator 
of any disturbance to the system. This rate of change (slope) feature was calculated as follows: 

(Note: shown below is calculation for humidity, but the approach was used for windspeed and temperature also.)

H: Current Humidity reading
H: Humidity reading from X seconds ago. Note: X has been set to 4.
HS: Humidity slope or rate of change

HS = (H - H_old) / X
or (from code):
df['Humidity_slope'] = (df['Humidity'] - df['Humidity_Xs_ago']) / X

[View notebook](https://github.com/AlexBandurin/Weather_Station/blob/master/weather_data.ipynb)

Shown below is a visualization of a part of the dataset. 
Description: 
- 8:38:53 - I blow cold air (hair fan) at the sensors
- 8:39:30 - I Stop
- 8:42:10 - I blow hot air, high setting (hair fan) at the sensors
- 8:42:45 - I Stop

<p align="center">
<img src="https://github.com/AlexBandurin/Weather_Station/blob/master/plots.png"  width="100%" height="80%">

Target variable: 'Label' , indicates current system state as one of 5 classes:

0: Normal state
1: Cold Blow
2: Hot Blow
3: Cold Object
4: Humidifier
  
## Model Building

XGBoost Regressor is the model used to make a classification (R^2 = 0.932)
After some testing, it has been decided that the following features are the most suitable for making the predictions: 'Humidity','Humidity_slope','Windspeed','Temperature','Temperature_slope'

