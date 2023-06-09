# Guide by David

0. Connect Polar-OH1 via Windows Bluetooth settings
1. Run .../HRMonitor/HeartRate.exe in File Explorer
2. Run these following command for first time configuration:(Powershell recommended)
```bash
cd .\Python_Data_Monitor\
python -m venv .\3104venv\
.\3104venv\Scripts\activate
python -m pip install -r .\PyScripts\requirements.txt
```
3. Go to ...\HeartRate_Python_OBS-main and Run
```bash
.\Start.bat
```
5. Open http://127.0.0.1:8919 in your browser to see if the server is running
6. Run 
```bash
Python Heartrate.py
```



## Initial Guide 

[简体中文文档](Readme.Zh_cn.md)

Thanks to [jlennox/Heartrate](https://github.com/jlennox/HeartRate).

## Running

0. Install Python 3.10 at [python.org](python.org) if you don't have Python installed.
1. Clone this repo or Download Zip.
1. Open /HRMonitor/HeartRate.exe.
2. Right click, Edit settings xml.
3. Find `<UDP>` Things. Fill it with "127.0.0.1:8909", like this:
```xml
...
  <HeartRateFile />
  <UDP>127.0.0.1:8909</UDP>
</HeartRateSettingsProtocol>
```
4. Run these following command for first time configuration:(Powershell recommended)
```bash
cd .\Python_Data_Monitor\
python -m venv .\3104venv\
.\3104venv\Scripts\activate
python -m pip install -r .\PyScripts\requirements.txt
```
4. Run Start.bat.
5. Open http://127.0.0.1:8919.

** Recommend using WebSocket than Js API. **

All Right.

## How to make your own visualble html:

Write your html in `Pyscripts/www`. 

Recommend to use websocket, which is ws://127.0.0.1/ws/hr_json.

If you use legacy api mode, The api is http://127.0.0.1:8919/api/hr_json.

You can add js files in `Pyscripts/js`.

These file will be automatically mounted while the server runs.

Open http://127.0.0.1:8919/{yourhtmlname}.html to see it.

## How can I test the web if I don't have a compatible Heartrate device?

Easy. 

Instead of running `Heartrate.exe`, just run `test.bat`.

It will send random data to UDP port, then run `start.bat` and open the url.

Gif:

![5wec2-ge0kv](https://user-images.githubusercontent.com/36123081/189464877-2ba3af54-a36d-4c26-b3f0-7f31150c8aa6.gif)


## Asking for help

<s>Maybe we can use websocket?</s>

Finished...?

## Open Source Software used in this software:

1. [HighCharts](https://github.com/highcharts/highcharts)
2. [jlennox/Heartrate](https://github.com/jlennox/HeartRate)
3. [Reconnecting-websocket](https://github.com/joewalnes/reconnecting-websocket)
