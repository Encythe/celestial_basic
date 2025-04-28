try:
    import sys
    import astral # pip install astral
    import astral.sun as sun # same dependency here
    import pickle
    import os
    import traceback
    import asyncio
    import datetime
    import signal
    import requests
    import math
    import random
except ImportError as e:
    print(f"An error occurred while importing packages, please double check to see what modules you're missing!\n{e}\n\nHit enter to terminate the program.")
    input()
    sys.exit(0)

data = {}
interrupted = False
tick = 0

async def prep():
    if "lastsunset" not in data:
        data['lastsunset'] = 1e12
    if "retry_in" not in data:
        data['retry_in'] = 0

async def load_main():
    try:
        print("Getting data...")
        with open("vars", 'rb') as file:
            global data
            tempdata = pickle.load(file)
            if tempdata:
                data = tempdata
            else:
                print("Data not loaded, let's just keep going")
            file.close()
    except BaseException as e:
        print(e, traceback.format_exc())

async def save_main():
    try:
        print("Saving data...")
        with open("vars", 'wb') as file:
            global data
            pickle.dump(data, file)
            file.close()
            print("nice")
    except BaseException as e:
        print(e, traceback.format_exc())

def formatTime(input : int, style : int, trailing : bool, comma : bool):
    years = math.floor(input/(3600*24*365))
    days = math.floor(input/(3600*24))%365
    hour = math.floor(input/3600)%24
    min = math.floor(input%3600/60)
    sec = math.floor(input%60)
    str = ""
    
    if input >= 3600*24*365 or style >= 5:
        str = f"{str}{years} year{years == 1 and '' or 's'}{comma and ',' or ''} "
    if input >= 3600*24 or style >= 4:
        str = f"{str}{days} day{days == 1 and '' or 's'}{comma and ',' or ''} "
    if input >= 3600 or style >= 3:
        str = f"{str}{(hour < 10 and (input >= 3600*24 or style >= 4 or trailing)) and '0' or ''}{hour}:"
    if input >= 60 or style >= 2: 
        str = f"{str}{(min < 10 and (input >= 3600 or style >= 3 or trailing)) and '0' or ''}{min}:"
    if (input >= 1 or style >= 1) and style < 6:
        str = f"{str}{(sec < 10 and (input >= 60 or style >= 2 or trailing)) and '0' or ''}{sec}"
    if input < 60:
        str = f"{str}s"
        
    return str

def get_format(t : float, text : bool):
    t = float("{:.02f}".format(t))
    if t < 0:
        return f"{text and "was " or ""}{formatTime(t*-1, 1, False, True)}{text and " ago" or ""}"
    else:
        return f"{text and "is in " or ""}{formatTime(t, 1, False, True)}"

async def exit():
    global interrupted
    print("\x1B[13B")
    print("Closing session")
    interrupted = True
    await save_main()
    sys.exit(0)

def sigint_handler(signal, frame):
    asyncio.create_task(exit())

async def main():
    global tick
    city = None
    location = None
    
    await load_main()
    await prep()
    
    try:
        r = requests.get(
            url="https://apip.cc/json"
        )
        # print(r)
        location = r.json()
        # print(location)
        if r.status_code != 200:
            raise requests.HTTPError(f"Fetching from the api failed: {r.json()}")
        else:
            data['cached_json'] = location
            print("Data cached!")
    except BaseException:
        print(f"An error occurred while trying to fetch location! Attempting to use cached data...")
        try:
            location = data['cached_json']
            print("We found cached data! Let's use that instead.")
        except BaseException:
            print(f"Cached data was not found, exiting!")
            await exit()
                   
    city = astral.LocationInfo(location["Capital"], location['CountryName'], location['TimeZone'], location['Latitude'], location["Longitude"])
    
    signal.signal(signal.SIGINT, sigint_handler)
    os.system("cls")
    while not interrupted:
        datetimenow = datetime.datetime.now(tz=city.tzinfo)
        now = datetimenow.timestamp()
        timestamp = data['lastsunset'] < now and datetime.datetime.fromtimestamp(data['lastsunset']).day == datetime.datetime.fromtimestamp(now).day and now + 86400 or now
        tempnow = datetime.datetime.fromtimestamp(timestamp)
        last = datetime.datetime.fromtimestamp(timestamp - 86400)
        s = sun.sun(city.observer, date=datetime.date(tempnow.year, tempnow.month, tempnow.day), tzinfo=city.tzinfo)
        s2 = sun.sun(city.observer, date=datetime.date(last.year, last.month, last.day), tzinfo=city.tzinfo)
        sunrise = s['sunrise'].timestamp()
        sunset = s['sunset'].timestamp()
        sunrise2 = s2['sunrise'].timestamp()
        sunset2 = s2['sunset'].timestamp()
        diff = (sunset-sunrise)-(sunset2-sunrise2)
        
        dl = f"{get_format(sunset-sunrise, False)} [{diff >= 0 and "+" or "-"}{get_format(abs(diff), False)} to {last.year}-{last.month < 10 and "0" or ""}{last.month}-{last.day < 10 and "0" or ""}{last.day}]"
        dls = " "*(30-len(dl))
        nsr = get_format(sunrise-now, True)
        nsrs = " "*(30-len(nsr))
        nss = get_format(sunset-now, True)
        nsss = " "*(30-len(nss))
        pre = str(datetime.datetime.fromtimestamp(sunrise, tz=city.tzinfo))
        tz = pre[len(pre)-6:len(pre)]
        rg = f"[{location["Capital"]}]"
        rgs = " "*(23-len(rg))
        dtsr = pre[0:-6]
        dtss = str(datetime.datetime.fromtimestamp(sunset, tz=city.tzinfo))[0:-6]
        dtn = str(datetime.datetime.fromtimestamp(now, tz=city.tzinfo))[0:-6]
        tps = f'{"{:.06f}".format(now-tick)} // {(now-tick != 0 and "{:.02f}".format(1/(now-tick)) or "Infinity")} TPS'
        tpss = " " *(20-len(tps.split(" // ")[-1]))
        tpsls = " " * (19-len(tps.split(" // ")[0]))
        date = f"{tempnow.year}-{tempnow.month < 10 and "0" or ""}{tempnow.month}-{tempnow.day < 10 and "0" or ""}{tempnow.day}"
        datespace = " "*(20-len(date))
        # os.system("cls")
        st = (
            f'┌───────────────────────────────────────────┐\n'
            f'│          schedule for {date}{datespace}│\n'
            f'├───────────────────────────────────────────┤\n'
            f'│   timezone: {tz} {rg}{rgs}│\n'
            f'│    sunrise: {dtsr}    │\n'
            f'│     sunset: {dtss}    │\n'
            f'│        now: {dtn}    │\n'
            f'│ day length: {dl}{dls}│\n'
            f'│     sunrise {nsr}{nsrs}│\n'
            f'│      sunset {nss}{nsss}│\n'
            f'├───────────────────────────────────────────┤\n'
            f'│{tpsls}{tps}{tpss}│\n'
            f'└───────────────────────────────────────────┘'
        )
        print(st)
        print("\x1B[14A")
        
        if data['retry_in'] > 0:
            data['retry_in'] -= now-tick
            
        tick = now
        
        if sunset < now:
            data['lastsunset'] = sunset
        
        await asyncio.sleep(0.01)

asyncio.run(main())