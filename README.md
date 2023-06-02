# NYC-Open-Data-Bootcamp
NYC Open Data Bootcamp Repository - Contains Homework and all project files

Project Scope:
The purpose of this project is to display subway entrances as plot points on a map and overlay an arrest data heatmap of all arrest data in NYC, provided by NYC Open Data's API.
The intention behind this is so that the user can access the webpage in order to see which subway entrance is the safest to use, and the user can make this decision based on the arrest data heatmap.
For example, if one entrance has many records of arrests occuring at it while the entrance two streets down has none, you would probably want to avoid the entrance that has many arrest records.

--- waitress required install with pip install waitress ---

commands to run in terminal:

cd 'C:\Users\flame\documents\School\bootcamp code'

env\Scripts\activate

waitress-serve --listen=*:42420 nypd:server


Apache controls the about-us.html, while waitress controls the python webserver. (redirects to eachother)

URL to access (main page):
flame.zapto.org:42420
flamegame.zapto.org:42420
nypdsubway.zapto.org:42420

URL to access (about us page):
[flame.zapto.org:420/about-us.html](http://flame.zapto.org:420/about-us.html)
[flamegame.zapto.org:420/about-us.html](http://flamegame.zapto.org:420/about-us.html)
[nypdsubway.zapto.org:420/about-us.html](nypdsubway.zapto.org:420/about-us.html)
