import datetime


from stravalib.client import Client

import pickle
import time
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

client = Client()
MY_STRAVA_CLIENT_ID, MY_STRAVA_CLIENT_SECRET = open('client.secret').read().strip().split(',')
print(F'Client ID and secret read from file {MY_STRAVA_CLIENT_ID} {MY_STRAVA_CLIENT_SECRET}')
def runAuth():



    url = client.authorization_url(client_id=MY_STRAVA_CLIENT_ID,
                                   redirect_uri='http://127.0.0.1:5000/authorization',
                                   scope=['read_all', 'profile:read_all', 'activity:read_all']
                                   )
    print(url)

    CODE = input("GetCode: ")
    print(CODE)
    # %% raw
    # from stravalib import Client
    access_token = client.exchange_code_for_token(client_id=MY_STRAVA_CLIENT_ID,
                                                  client_secret=MY_STRAVA_CLIENT_SECRET,
                                                  code=CODE)

    print(access_token)


    # %% raw
    with open('../access_token.pickle', 'wb') as f:
        pickle.dump(access_token, f)


def existingToken():
    with open('../access_token.pickle', 'rb') as f:
        access_token = pickle.load(f)

    print('Latest access token read from file:')
    access_token

    if time.time() > access_token['expires_at']:
        print('Token has expired, will refresh')
        refresh_response = client.refresh_access_token(client_id=MY_STRAVA_CLIENT_ID,
                                                       client_secret=MY_STRAVA_CLIENT_SECRET,
                                                       refresh_token=access_token['refresh_token'])
        access_token = refresh_response
        with open('../access_token.pickle', 'wb') as f:
            pickle.dump(refresh_response, f)
        print('Refreshed token saved to file')

        client.access_token = refresh_response['access_token']
        client.refresh_token = refresh_response['refresh_token']
        client.token_expires_at = refresh_response['expires_at']

    else:
        print('Token still valid, expires at {}'
              .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))

        client.access_token = access_token['access_token']
        client.refresh_token = access_token['refresh_token']
        client.token_expires_at = access_token['expires_at']

    athlete = client.get_athlete()
    print("Athlete's name is {} {}, based in {}, {}"
          .format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))



def getData():
    #activities = client.get_activities(limit=10)
    activities = client.get_activities(after='2022-06-05')
    print(list(activities))
    my_cols = ['name',
               'start_date_local',
               'type',
               'distance',
               'moving_time',
               'elapsed_time',
               'total_elevation_gain',
               'elev_high',
               'elev_low',
               'average_speed',
               'max_speed',
               'average_heartrate',
               'max_heartrate',
               'start_latitude',
               'start_longitude']
    data = []
    for activity in activities:
        my_dict = activity.to_dict()
        data.append([activity.id] + [my_dict.get(x) for x in my_cols])

    print(data)
    totalDistance = 0
    totalElevation = 0
    totalMovingTime = 0
    tAverageHeartRate = 0
    maxHeartRate = 0

    last7Distance = 0
    last7Elevation = 0
    last7MovingTime = 0

    last7maxHeartRate = 0
    thisWeeksCount = 0
    tlast7AverageHeartRate = 0

    last1maxHeartRate = 0
    thisdayCount = 0

    last1averageHeartRate = 0
    tlast1Distance = 0
    last1Elevation = 0

    last1MovingTime = 0

    for x in data:
        print(x)

        d1 = datetime.datetime.strptime(x[2], "%Y-%m-%dT%H:%M:%S")
        print(d1)
        d2 = d1.replace(hour=0,minute=0,second=0)
        print(d2)
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        if(d2.date() > week_ago):
            thisWeeksCount = thisWeeksCount + 1
            print("this weeks data")
            last7Distance = last7Distance + x[4]
            last7MovingTime = last7MovingTime + x[5]
            last7Elevation = last7Elevation + x[7]
            tlast7AverageHeartRate = tlast7AverageHeartRate + x[12]
            if x[13] > last7maxHeartRate:
                last7maxHeartRate = x[13]




        totalDistance = totalDistance + x[4]
        totalMovingTime = totalMovingTime + x[5]
        totalElevation = totalElevation +x[7]
        tAverageHeartRate = tAverageHeartRate + x[12]
        print(x[12])

        if x[13] > maxHeartRate:
            maxHeartRate = x[13]
    print(len(data))
    averageHeartRate = tAverageHeartRate / len(data)
    last7averageHeartRate  = tlast7AverageHeartRate / thisWeeksCount

    today = datetime.date.today()

    if (d2.date() == today):
        #thisWeeksCount = thisWeeksCount + 1
        print("todays weeks data")
        tlast1Distance = tlast1Distance + x[4]
        last1MovingTime = last1MovingTime + x[5]
        last1Elevation = last1Elevation + x[7]
        last1averageHeartRate = last1averageHeartRate + x[12]
        if x[13] > last1maxHeartRate:
            last1maxHeartRate = x[13]

    print(f"td:{totalDistance/1000} totalElevation:{totalElevation} totalMovingTime:{totalMovingTime/60} maxHR:{maxHeartRate} avgHR:{averageHeartRate}")
    print(
        f"7td:{last7Distance / 1000} 7totalElevation:{last7Elevation} 7totalMovingTime:{last7MovingTime / 60} 7maxHR:{last7maxHeartRate} 7avgHR:{last7averageHeartRate}")
    print(
        f"7td:{tlast1Distance / 1000} 1totalElevation:{last1Elevation} 1totalMovingTime:{last1MovingTime / 60} 1maxHR:{last1maxHeartRate} 1avgHR:{last1averageHeartRate}")
    DrawTodayStats(tlast1Distance / 1000,last1Elevation,last1MovingTime / 60, last1maxHeartRate, last1averageHeartRate)

def DrawTodayStats(distance, elevation, movingtime, maxbpm, avgbpm):
    #img = Image.new('RGBA', (1920, 1080), color = (0, 100, 0, 128))
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))

    d = ImageDraw.Draw(img)
    margin = 100
    margin2 = 5
    margin3 = 1620
    margin4 = 300
    tmargin1 = 600

   
    tDistance = "%.2f" % distance + "k"
    tElevation = f"{round(elevation)}" + "m"
    tMovingtime = str(datetime.timedelta(minutes=movingtime))
    tMaxbpm = f"{round(maxbpm)}"
    tAvgbpm = f"{round(avgbpm)}"

    print(tDistance)
    print(tElevation)
    print(tMovingtime)
    print(tMaxbpm)
    print(tAvgbpm)
    

    fnt = ImageFont.truetype('/Users/johnmcmanus/Documents/TidyDocs/CodeProjects/Archive/BMFRE/BMFRE/Fonts/Montserrat-Bold.ttf', 36)
    fnt2 = ImageFont.truetype(
        '/Users/johnmcmanus/Documents/TidyDocs/CodeProjects/Archive/BMFRE/BMFRE/Fonts/Montserrat-Bold.ttf', 72)
    fnt3 = ImageFont.truetype(
        '/Users/johnmcmanus/Documents/TidyDocs/CodeProjects/Archive/BMFRE/BMFRE/Fonts/Montserrat-Bold.ttf', 58)
    d.text((margin, 950), "Distance",  font=fnt, fill=(255, 255, 255))
    d.text((margin + 300, 950), "Elevation",  font=fnt, fill=(255, 255, 255))
    d.text((margin + 700, 950), "Max BPM",  font=fnt, fill=(255, 255, 255))
    d.text((margin + 1100, 950), "Avg BPM",  font=fnt, fill=(255, 255, 255))
    d.text((margin + 1500, 950), "Moving Time", font=fnt, fill=(255, 255, 255))

    d.text((margin, 1000), tDistance, font=fnt2, fill=(255, 255, 255))
    d.text((margin + 300, 1000), tElevation, font=fnt2, fill=(255, 255, 255))
    d.text((margin + 700, 1000), tMaxbpm, font=fnt2, fill=(255, 255, 255))
    d.text((margin + 1100, 1000), tAvgbpm, font=fnt2, fill=(255, 255, 255))
    d.text((margin + 1500, 1000), tMovingtime, font=fnt2, fill=(255, 255, 255))

    d.text((margin2, tmargin1), "How it Started", font=fnt, fill=(255, 255, 255))
    d.text((margin3, tmargin1), "How it's Going", font=fnt, fill=(255, 255, 255))

    d.text((margin2, tmargin1 + 40), "Weight", font=fnt, fill=(255, 255, 255))
    d.text((margin2, tmargin1 + 80), "14st 11lb", font=fnt2, fill=(255, 255, 255))
    d.text((margin2, tmargin1 + 160), "BodyFat", font=fnt, fill=(255, 255, 255))
    d.text((margin2, tmargin1 + 200), "30.2%", font=fnt2, fill=(255, 255, 255))

    d.text((margin3, tmargin1 + 40), "Weight", font=fnt, fill=(255, 255, 255))
    d.text((margin3, tmargin1 + 80), "14st 3lb", font=fnt2, fill=(255, 255, 255))
    d.text((margin3, tmargin1 + 160), "BodyFat", font=fnt, fill=(255, 255, 255))
    d.text((margin3, tmargin1 + 200), "29%", font=fnt2, fill=(255, 255, 255))

   # d.text((20, 0), "https://www.justgiving.com/fundraising/John-McManusPwC", font=fnt3, fill=(255, 255, 255))
   # d.text((400, 80), "Raising funds for SAMH (Mental Health) via PwC Foundation", font=fnt, fill=(255, 255, 255))


    img.save('backdrop.png')

    pass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #runAuth()
    existingToken()
    getData()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
