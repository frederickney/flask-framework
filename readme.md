# Introduction to the structure of the files:

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

All models are stored inside the src/Models folder.
The models that you register into the app must be an Database.Model object, you could import this object using the following line into your database model:

```python
from Database import Database
```

All models must be registered inside the Models.ModelsRegistry.
For allowing the server to initiate the database structure you must then import all of your models, that are registered into the Models.ModelsRegistry, inside the Database.driver.init method such as this example:

```python
    @classmethod
    def init(cls):
        """
        Function that create schema tables based on imported models within this function
        :return: N/A
        """
        from Models.ModelsRegistry import YourModel
        cls.Model.metadata.create_all(bind=cls.engine)
```

#### Creating scheduling tasks:

Tasks are some python code that are running at specific interval time. These task must be placed inside the src/Task folder.
After that you must add these line inside the src/server.py file to enable your task function:

```python
    Server.Process.add_task("Task.YourFileOrClass.YourStaticMethodOrClassMethod", second=30)
```

Note the task your registering must be before the line:

```python
    Server.Process.start(args)
```


#### Static folder:

The src/static folder contains all static file for your web based application.

#### Template folder:

The src/template folder contains layouts and templates file for your web based application.
Those files are content configurable, you can also import layout inside the your template file, it allow you to have only content editable part into your template file.

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

* On every startup of the flask server 

```bash 
export LOG_FILE=log/process.log
```

```bash 
export CONFIG_FILE=config/config.orig.json
```

* Starting the flask server

```bash 
./src/server.py
```
