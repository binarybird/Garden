# Garden
A REST api using Flask for managing/recording/polling i2c sensors and data on my Raspberry pi

Prereq:
1) Get a raspi
2) Enable i2c
3) Stick an i2c muxer on bus 1 (I used a TCA9548A)
4) Stick a SHT20 and others on the muxer!

To run the server:
1) Install your db of choice (postgres used here). Create a DATABASE
2) vi ~/.bashrc (or .bash_profile)
3) add envars:   
```
export FLASK_ENV=development   
export DATABASE_URL=postgres://USER:PASS5@HOST:PORT/DATABASE   
export JWT_SECRET_KEY=somesupersecretkeyshhhdontshare   
export PORT=8080   
```
4) cd Garden
5) python3 manage.py db init
6) python3 manage.py db migrate
7) python3 manage.py db upgrade
8) python3 run.py
   
Ill document the API and i2c device interface later!   
   
Janky API docs so far:    
---
POST /garden/v1/users - create a user (auto assigned role = 1). api-token returned.     
Expected Body:   
```
{
    "name": "Some Name",
    "email": "email@google.com",
    "password": "pAs5woRd",
}
```
---   
GET /garden/v1/users - gets all users (only if role = 0)   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
---   
GET /garden/v1/users/{INT} - Get user by id. Only own user accessable if role != 0   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
---   
PUT /garden/v1/users/{INT} - Update user by id. Only own user accessable if role != 0   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
Expected Body:   
```
{
    "name": "Some Name",
    "email": "email@google.com",
    "password": "pAs5woRd",
}
```
---    
DELETE /garden/v1/users/{INT} - Delete user by id. Only own user accessable if role != 0   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
``` 
---   
GET /garden/v1/users/me - Get current user info.    
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
---  
POST /garden/v1/login - Login. api-token returned.   
Expected Body:   
```
{
    "email": "email@google.com",
    "password": "pAs5woRd",
}
```
   
---   
   
POST /garden/v1/devices - Add i2c device
Expected Headers:
```
api-token <your-token-here>
Content-Type application/json
```
Expected Body:   
```
{
	"name": "Air Sensor",
	"device_clazz": "SHT20",
	"address": 64,
	"bus": "1",
	"mux_address": 112,
	"mux_channel": 16
}
```
---   
GET /garden/v1/devices/ -  Get a list of all devices   
Expected Headers:  
```
api-token <your-token-here>
Content-Type application/json
```
---   
GET /garden/v1/devices/{INT} - Get single device   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
---   
PUT /garden/v1/devices/{INT} - Update device   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
Expected Body:   
```
{
	"name": "Air Sensor",
	"device_clazz": "SHT20",
	"address": 64,
	"bus": "1",
	"mux_address": 112,
	"mux_channel": 16
}
```
---   
DELETE /garden/v1/devices/{INT} - Delete device   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```
---   
GET /garden/v1/devices/{INT}/poll - Poll device   
Expected Headers:   
```
api-token <your-token-here>
Content-Type application/json
```

