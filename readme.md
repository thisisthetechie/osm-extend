# OSM Extend

Connect to Online Scout Manager and perform some of the tasks that are currently not available via the service.

## Functions Available:
* Create and maintain a Flexi-Record showing the completion status of Challenge Badges
* Count the number of Knots completed by Beavers from a Flexi-Record and update Challenge badges once requirements are met
* Count the number of Activity and Staged Badges completed and update Chief Scout badge requirements for a total number when requirement is met

## OSM Class
This project creates a new class (OSM) which combines some of the most useful data into one object such as:

``` python
section = OSM('scouts')
section.size
section.current_term
section.scouts
section.terms
section.name
section.id
```

## Using OSM Extend
This repo is just an example, which is in use by me and my section. It will change and grow as new items are developed. 

The idea behind this project is to host the repo and trigger main.py on a schedule to gather updates and keep on track of requirements etc.

There are sensitive values required, as such these must be stored in a file called `.env` and contain the OSM API ID and OSM API Secret (see `example.env`). You can get these values from **OSM -> Settings -> My Account Details -> Developer Tools**, simply create a new Application and copy the values you are presented with into your `.env` file.

### Requirements
The following libraries are used within this project:
```
tabulate
datetime
requests_oauth2client
os
dotenv
requests
```

### Example hosting information
To follow.