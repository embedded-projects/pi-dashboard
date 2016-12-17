#!/usr/bin/env python

"""
Code mostly adopted from: http://blog.jacobean.net/?p=1016
"""

from signal import alarm, signal, SIGALRM, SIGKILL
import sys 
import pygame
import os 
import pygameui as ui
import logging
import pywapi
import string
import time 
from time import localtime, strftime
import daemon

# location for Highland Park, NJ
weatherDotComLocationCode = 'USNJ0215'
# convert mph = kpd / kphToMph
kphToMph = 1.60934400061

# font colors
colourWhite = (255,255,255)
colourBlack = (0,0,0)

# update interval
updateRate = 60  # seconds

class pitft:
        screen = None;
        colourBlack = (0,0,0)

        def __init__(self):
		class Alarm(Exception):
			pass
		def alarm_handler(signum, frame):
			raise Alarm

                disp_no = os.getenv("DISPLAY")
                if disp_no:
                        print "I'm running under X display = {0}".format(disp_no)

                os.putenv('SDL_FBDEV', '/dev/fb1')
                
                drivers = ['fbcon', 'directfb', 'svgalib']
                found = False
                for driver in drivers:
                        if not os.getenv('SDL_VIDEODRIVER'):
                                os.putenv('SDL_VIDEODRIVER', driver)
                        try:
                                pygame.display.init()
                        except pygame.error:
                                print 'Driver: {0} failed.'.format(driver)
                                continue
                        found = True
                        break
                if not found:
                        raise Exception('No suitable video driver found')

	    	signal(SIGALRM, alarm_handler)
		alarm(3)
		try:
		        pygame.init()
		        DISPLAYSURFACE = pygame.display.set_mode((320, 240)) 
		        alarm(0)
	        except Alarm:
		        raise KeyboardInterrupt                

                size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
                #Clear the screen to start
                self.screen.fill((0,0,0))
                # Initlialize font support
                pygame.font.init()
                # Render the screen
                pygame.display.update()

        def __del__(self):
                "Destructor to make sure py game shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

fontpath = pygame.font.match_font('dejavusansmono')

font = pygame.font.Font(fontpath, 20)
fontSm = pygame.font.Font(fontpath, 18)

def task_weather():
        while True:
                # retrieve data from weather.com
                weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode)

                # extract current data for today
                location = weather_com_result['location']['name']
                today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                        + weather_com_result['forecasts'][0]['date'][4:] + " " \
                        + weather_com_result['forecasts'][0]['date'][:3]
                #windSpeed = int(weather_com_result['current_conditions']['wind']['speed']) / kphToMph
                #currWind = "{:.0f}mph ".format(windSpeed) + weather_com_result['current_conditions']['wind']['text']
                currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "C"
                currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + "mb"
                uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
                humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
                
                # extract forecast data
                forecastDays = {}
                forecaseHighs = {}
                forecaseLows = {}
                forecastPrecips = {}
                forecastWinds = {}
                
                start = 0
                try:
                        test = float(weather_com_result['forecasts'][0]['day']['wind']['speed'])
                except ValueError:
                        start = 1
                
                for i in range(start, 5):
                
                        if not(weather_com_result['forecasts'][i]):
                                break
                        forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
                        forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
                        forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
                        forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                        forecastWinds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])  / kphToMph) + \
                                           weather_com_result['forecasts'][i]['day']['wind']['text']        

                # blank the screen
                mytft.screen.fill(colourBlack)
                
                # render the weather logo at 0,0
                icon = "./" + "%02d" % int(weather_com_result['current_conditions']['icon']) + ".png"
                logo = pygame.image.load(icon).convert()
                mytft.screen.blit(logo, (0,0))
                
                # set the anchor for the current weather data text
                textAnchorX = 140
                textAnchorY = 5
                textYoffset = 20
                
                # add current weather data text artifacts to the screen
                text_surface = font.render(location, True, (0,255,0))
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset

                x = strftime("%H:%M:%S", localtime())
                text_surface = font.render(x , True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset

                text_surface = font.render(today, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset

                text_surface = font.render(currTemp, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                
                text_surface = font.render(currPress, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset

                # text_surface = font.render(uv, True, colourWhite)
                # mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                # textAnchorY+=textYoffset

                text_surface = font.render(humid, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))

                # set X axis text anchor for the forecast text
                textAnchorX = 0
                textXoffset = 80
        
                # add each days forecast text
                for i in forecastDays:
                        textAnchorY = 130
                        text_surface = fontSm.render(forecastDays[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecaseHighs[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecaseLows[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecastPrecips[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorY+=textYoffset
                        text_surface = fontSm.render(forecastWinds[int(i)], True, colourWhite)
                        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                        textAnchorX+=textXoffset
                
                # refresh the screen with all the changes
                pygame.display.update()
                        
                # Wait
                time.sleep(updateRate)

if __name__ == "__main__":
	task_weather()        
