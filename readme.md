# Introduction to the structure of the files:

#### Configuration

The base configuration file is located on the config dir.

You can add default database using only the configuration file.

##### default database with builtin driver in sqlalchemy 

```json
{
  ...,
  "DATABASE": {
    "default": "mysql",
    "mysql": {
          "driver": "mysql+pymysql",
          "user": "replace this with your database user",
          "password": "replace this with your database user's password",
          "database": "replace this with your database name",
          "address": "replace this with your hostname",
          "models": "mysql (python module that require to be put under Models.Persistent module)"
    }
  },
  ...

}
```

##### default database with non builtin driver in sqlalchemy 

```json
{
  ...,
  "DATABASE": {
    "default": "informix",
    "informix" : {
          "driver": "informix",
          "user": "replace this with your database user",
          "password": "replace this with your database user's password",
          "database": "replace this with your database name",
          "address": "replace this with your hostname",
          "models": "informix (python module that require to be put under Models.Persistent module)",
          "params": {
              "SERVER": "replace with your server name",
              "CLIENT_LOCALE" : "replace with your client locale",
              "DB_LOCALE": "replace with your server locale"
          },
          "dialects": {
            "informix":  {"module": "IfxAlchemy.IfxPy", "class":"IfxDialect_IfxPy"},
            "informix.IfxPy": {"module": "IfxAlchemy.IfxPy", "class": "IfxDialect_IfxPy"},
            "informix.pyodbc": {"module":  "IfxAlchemy.pyodbc", "class": "IfxDialect_pyodbc"}
          }
      }
  },
  ...

}
```
__"params"__ are parameters that need to be send within the connection to the database.
In that example using informix database __"SERVER"__, __"CLIENT_LOCALE"__ and __"DB_LOCALE"__ are required parameters for the connection to the database.

__"dialects"__ are the python modules configuration to translate models into sql statements to query the database

##### multiple databases

```json
{
  ...,
  "DATABASE": {
    "db01" : {
      ...
    },
    "db02" : {
      ...
    }
  },
  ...

}
```


##### Adding users session

To enable sessions in the server you need to add __"APP_KEY"__ and __"SESSION"__ into the __"SERVER_DATA"__ section in the configuration file

__"APP_KEY"__ : random string value (keep that secret)

__"SESSION"__ : string value, possible values are [__"filesystem"__, __"memcahed"__, __"redis"__, __"mongodb"__, __"sqlalchemy"__]

##### Using filesystem, redis or memcached based sessions

```json
{
    ...,
    "SERVICES": {
        "redis": {
            "HOST": "localhost",
            "PORT": 6379
        },
        "filesystem": {
            "PATH": "sessions"
        },
        "memcached": {
            "HOST": "localhost",
            "PORT": 11211
        }
    }
}
```

##### Using mongodb or sqlalchemy based sessions

Session based on sqlalchemy will use the default configured database

```json
{
    ...,
    "DATABASES": {
        "default": "mysql",
        "mysql": {
              "driver": "mysql+pymysql",
              "user": "replace this with your database user",
              "password": "replace this with your database user's password",
              "database": "replace this with your database name",
              "address": "replace this with your hostname",
              "models": "mysql (python module that require to be put under Models.Persistent module)"
        },
        "mongodb": {
              "driver": "mongodb",
              "user": "replace this with your database user",
              "password": "replace this with your database user's password",
              "database": "replace this with your database name",
              "address": "replace this with your hostname",
              "collection": "rreplace this with your collection name for the sessions",
              "models": "mongodb (python module that require to be put under Models.Persistent module)"
        }
  },
  ...
}
```

##### Adding cors to the server

```json
{
  "SERVER_DATA": {
      ...,
      "CORS": {
            "ORIGINS": [
                    "http://localhost"
            ],
            "ALLOW_HEADERS": ["Content-Type", "Authorization"],
            "ALWAYS_SEND": true,
            "AUTOMATIC_OPTIONS": true,
            "EXPOSE_HEADERS": "Authorization",
            "INTERCEPT_EXCEPTIONS": true,
            "MAX_AGE": null,
            "METHODS": ["GET", "HEAD", "POST", "OPTIONS"],
            "SEND_WILDCARD": false,
            "SUPPORTS_CREDENTIALS": true,
            "VARY_HEADER": true
      },
      ...
  },
  ...
}
``` 

#### Creating server routes

There are 3 files where you could register your flask server routes, You could find these file under the src/Server folder:

* Errors:

All the server http error code must be registered inside the __init__ method of the ErrorHandler.py file.

* Web based http file routes:

All the web based http routes must be registered inside the __init__ method of the Web.py file.

* Rest api routes:

All the Rest API based routes must be registered inside the __init__ method of the WS.py file.

#### Creating controllers:

* Web based http file controllers:

All web based http file controllers must be placed under the src/Controllers/Web folder.

* Rest api controllers:

All Rest API based controllers must be placed under the src/Controllers/WS folder.

#### Creating models:


you can create SQLAlchemy models by creating a new module under the ```Models.Persistent``` module and place each models inside your module that you previously created. 

The models that you register into the app must be an ```Database.Model ``` or ```Database.get_models_by_name('replace that with your database connection name')``` object, you could import this object using the following line into your database model:


```python
from Database import Database
```

All models must be imported inside the ```__init__.py``` of your base module and you must import this module in the ```__init__.py``` of the ```Models.Persistent``` module

#### Creating scheduling tasks:

Tasks are some python code that are running at specific interval time. These task must be placed inside the src/Task folder.
After that you must add these line inside the src/server.py file to enable your task function:

```python
    Server.Process.add_task("Task.YourFileOrClass.YourStaticMethodOrClassMethod", second=30)
```

Note the task you are registering must be before the line:

```python
    Server.Process.start(args)
```


#### Static folder:

The src/static folder contains all static file for your web based application.

#### Template folder:

The src/template folder contains layouts and templates file for your web based application.
Those files are content configurable, you can also import layout inside the your template file, it allow you to have only content editable part into your template file.

---

# Using docker-compose file:

* At first start of the flask server:

```bash
docker-compose up 
```

* On restart of the flask server:

```bash
docker-compose start 
```

####     Or

```bash
docker-compose restart 
```

* To shutdown the flask server:

```bash
docker-compose stop 
```

---

# Running on local desktop:

We assume that your system already had python v3+ and pip v3+ installed.

* pre-installation:

```bash 
pip3 install -r requirements.txt
```

* post-installation:

```bash 
pip3 install -r extensions.txt
```

* First start of the flask server

```bash
mkdir log
```

* On every startup of the flask server in standalone

```bash 
export LOG_FILE=log/process.log
```

```bash 
export CONFIG_FILE=config/config.orig.json
```

* Starting the flask server in standalone

```bash 
./src/server.py
```

* On every startup of the flask server in standalone

```bash 
export LOG_DIR=log/
```

```bash 
export CONFIG_FILE=config/config.orig.json
```

* Starting the flask server with workers

```bash 
./src/wsgi.py
```

---

# LICENSE

#### See [License file](LICENSE)