# Flask Framework mvc

> A ready to use industrialized **Model–View–Controller** framework built on top of [Flask](https://flask.palletsprojects.com/) — with a project generator, YAML-driven configuration, first-class SQLAlchemy multi-database support, and ready-to-go deployment targets using Gunicorn/Waitress (local, Docker, and Azure Functions).


[![PyPI version](https://img.shields.io/pypi/v/flask-framework-mvc.svg)](https://pypi.org/project/flask-framework-mvc/)
[![Python versions](https://img.shields.io/pypi/pyversions/flask-framework-mvc.svg)](https://pypi.org/project/flask-framework-mvc/)
[![Downloads](https://img.shields.io/pypi/dm/flask-framework-mvc.svg)](https://pypi.org/project/flask-framework-mvc/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Issues: ](https://img.shields.io/github/issues/frederickney/flask-framework.svg)](https://github.com/frederickney/flask-framework/issues)

---

## Why flask-framework-mvc?

Flask gives you a microframework and total freedom. **Flask Framework MVC** adds the missing structure so teams share a predictable one: an industrialized project layout, YAML-driven configuration, multi-database support, session management, scheduled tasks, and first-class deployment recipes — so you can go from `pip install` to a running, production-shaped app in minutes instead of wiring it all up by hand.

`flask-framework-mvc` adds a **convention-over-configuration** layer so teams get a predictable, Model-View-Controller structure without giving up Flask's performance:


- 🏗️ **A real MVC structure** — controllers, models, views/templates in known places, so anyone can navigate any project.
- 🧰 **A project & code generator** — scaffold a new project, controllers, routers, and middlewares from the CLI instead of copy-pasting boilerplate.
- 🗄️ **Configuration-driven databases** — declare one or many SQLAlchemy databases in YAML, including non-builtin dialects (e.g. Informix) and read-only connections. A `@safe` decorator handles session/transaction safety for you.
- 💻 **Session management** — filesystem, Memcached, Redis, MongoDB, or SQLAlchemy backends.
- 🌐 **CORS support** — declarative origins and allowed headers.
- 🔐 **Built-in SSL** — enable TLS straight from the config file.
- ⏱️ **Scheduled tasks** — run background jobs on intervals via the built-in process manager.
- 🚀 **Multiple deployment targets** — local dev, standalone server, Gunicorn workers (Linux/Mac), Waitress (Windows), Docker Compose, and Azure Functions, out of the box.
- 📦 **Packageable projects** — build your app into a pip package and compose several packaged apps into one server.
- ♻️ **Database migrations** — Allow alembic to use configured database connection(s) and drive its own migration plan over the database.
- 🤐 **Secrets managment** — All secrets / variables can be injected to the yaml configuration file throughout deployment environment / secret variable, names need to map the same ones into the yaml file.
- 🛡️ **Multi Factor Authentication (MFA)** — Allows user authentication through various single sign one provider (google, microsoft, keycloak, PingID and many more) using both OpenID and / or SAML protocoles

---

## Requirements

- Python **3.7+** (tested through 3.13)
- `pip` 3+

---

## Installation

From PyPI:

```bash
pip install flask-framework-mvc
```

From source:

```bash
git clone https://github.com/frederickney/flask-framework.git
cd flask-framework
pip3 install .
```

---

## Quick start

### Create a new project with the CLI:

```bash
flask_framework_mvc.cli project -c myapp
```
By running this command, it will create myapp folder in the CWD as well as creating the base structure for a new project under it.

> [!NOTE]
> By default it will create a app.py under the root folder of the project. It will be later used for developement settings and standalone single instance deployment (not recomended for full production settings).

### Point the framework at your config file:

```bash
# Linux / macOS
export CONFIG_FILE=config/config.yml

# Windows (PowerShell)
$env:CONFIG_FILE = "config\config.yml"
```

### Run it in dev mode:

```bash
# needs app.py in your app current working directory
python -m fastapi dev
```

### For production:

1. single instance:

```bash
# needs app.py in your app current working directory
python -m fastapi run
```

or
```bash
fastapi_framework_mvc.server -lp <listening-port>
```

2. production-driven:

For linux:
```bash
fastapi_framework_mvc.wsgi
```

For windows:
```bash
fastapi_framework_mvc.asgi
```


> [!NOTE]
> The CLI is also available as `python -m fastapi_framework_mvc.cli`. Run any command with `-h` for full usage.

---

## Project structure

A generated project follows this layout:

```
myapp/
├── config/
│   └── config.yml            # server, SSL, and database configuration
├── controllers/
│   ├── web/                  # HTML/file controllers (registered in web.py)
│   │   └── errors/           # HTTP error handlers (404, 500, …)
│   ├── ws/                   # REST API controllers (registered in ws.py)
│   └── socket/               # Web socket controllers (registered in socket.py)
├── models/
│   ├── forms/                # request/form models
│   └── persistent/           # SQLAlchemy models
├── server/
│   ├── middleware.py         # middlewares registration
│   ├── plugins.py            # plugins registration
│   ├── socket.py             # Web Socket registration
│   ├── web.py                # web route registration
│   ├── ws.py                 # REST route registration
│   └── errorhandler.py       # error route registration
├── static/                   # static assets for web apps
├── template/                 # Jinja2 layouts & templates
└── app.py                    # auto-generated app.py used for debuging or standalone execution
```

---


## Configuration

All runtime configuration lives in `config/config.yml`.

### SSL / TLS

Add an `SSL` block under the `SERVER` key:

```yaml
SERVER:
  SSL:
    Certificate: "path to the .crt file (public key)"
    PrivateKey: "path to the .pki file (private key)"
```

### Databases

Databases are declared entirely in config — no wiring code required.

> [!NOTE]
> This part is comming from [database-connector-kit](https://pypi.org/project/database-connector-kit), documentation may not match, please refer to documentation from this package.

**Built-in SQLAlchemy driver:**

```yaml
DATABASES:
  default: mysql
  mysql:
    driver: mysql+pymysql
    user: "your database user"
    password: "your database user's password"
    database: "your database name"
    address: "your hostname"
    models: "mysql"      # python module placed under models.persistent
    readonly: false
```

**Non-built-in driver (Informix example):**

```yaml
DATABASES:
  informix:
    driver: informix
    user: "your database user"
    password: "your database user's password"
    database: "your database name"
    address: "your hostname"
    models: "informix"
    params:
      SERVER: "your server name"
      CLIENT_LOCALE: "your client locale"
      DB_LOCALE: "your server locale"
    dialects:
      informix:
        module: IfxAlchemy.IfxPy
        class: IfxDialect_IfxPy
      informix.IfxPy:
        module: IfxAlchemy.IfxPy
        class: IfxDialect_IfxPy
      informix.pyodbc:
        module: IfxAlchemy.pyodbc
        class: IfxDialect_pyodbc
    readonly: false
```

- **`params`** — extra values sent with the connection (required ones vary by database).
- **`dialects`** — the Python modules used to translate models into SQL for non-built-in drivers.
- **URL separators** — default to `?` (first param) and `&` (subsequent params). Override per database:

  ```yaml
  url_param_separator: '?'
  params_separator: '&'
  ```

**Multiple databases** — just declare more database configuration entries:

```yaml
DATABASES:
  db01:
    ...
  db02:
    ...
```

---

## Defining routes

Routes are registered in three files under `server/`:

**Error handlers** (`server/errorhandler.py`):

```python
server.register_error_handler(500, controllers.web.errors.http_500)
```

**Web (HTML/file) routes** (`server/web.py`):

```python
server.add_url_rule(path='/', route=controllers.web.home.index, methods=["GET"], name='home')

# or include a FastAPI APIRouter
server.include_router(controllers.web.router, prefix='/api/v1')
```

**REST API routes** (`server/ws.py`):

```python
server.add_api_route('/api/content/', controllers.ws.api.index, methods=['GET'], name='api.content')

# or include a FastAPI APIRouter
server.register_blueprint(controllers.ws.api.v1.router, url_prefix='/api/v1/')
```

---

## Controllers

- **Web controllers** live under `controllers/web`.
- **REST controllers** live under `controllers/ws`.

Class-based controllers and view functions must be imported in the `__init__.py` of their respective module.

When a controller touches the database, decorate it with `@safe` from `flask_framework.database.decorators` to get safe session/transaction handling:

```python
from flask_framework.database.decorators import safe


class Content(object):

    @safe
    @staticmethod
    def index(api_param):
        return api_param


class Controller(Content):

    @classmethod
    def index(cls, api_param: str):
        return super(Controller, cls).index(api_param)
```
---

## Models

Create SQLAlchemy models inside a module under `models/persistent`. Each model must extend the framework's base model:

```python
from flask_framework.database import Database

# Use the default connection's model base…
class MyModel(Database.Model):
    ...

# …or bind to a named connection:
# Database.get_models_by_name('your_connection_name')
```

Import your models in your module's `__init__.py`, then import that module in the `__init__.py` of `models.persistent`.

---

## Views: static & templates

- **`static/`** — CSS, JS, images, and other static assets for web apps.
- **`template/`** — Jinja2 layouts and templates. Templates support layout inheritance, so pages only need to define their editable content.

---

## CLI reference

Run any command with `-h` for full options. All commands work via the `flask_framework_mvc.cli` executable or `python -m flask_framework.cli`.

| Task | Command |
| --- | --- |
| Create a project | `flask_framework_mvc.cli project -c <name>` |
| Create a standalone controller | `flask_framework_mvc.cli controller -c controllers/ws/contents` |
| Create a router controller | `flask_framework_mvc.cli controller -c controllers/ws/contents -router` |
| Install a standalone controller | `flask_framework_mvc.cli manager -l controllers/ws/contents` |
| Install a router controller (with prefix) | `flask_framework_mvc.cli manager -l controllers/ws/contents -p /api/` |
| Create a middleware | `flask_framework_mvc.cli middleware -c grant/authorization` |

---

## Running & deployment

### Local (FastAPI CLI)

```bash
export CONFIG_FILE=config/config.yml   # set once per shell
python -m flask run --debug            # development
python -m flask run                    # production
```

### Standalone server

```bash
python -m flask_framework.server -lp <listening port>
```

### Gunicorn with worker processes

```bash
python -m flask_framework.wsgi
```

### Docker Compose

```bash
docker-compose up        # first run (build + start)
docker-compose start     # start
docker-compose restart   # restart
docker-compose stop      # stop
```

### Azure Functions

```python
# coding: utf-8
import azure.functions as functions
import flask_framework.azure 
import logging
import os


os.environ.setdefault('CONFIG_FILE', './config/config.yml')
app = functions.WsgiFunctionApp(
    flask_framework.azure.AzureFunctionsApp(), 
    http_auth_level=functions.AuthLevel.ANONYMOUS
)

```

Ensure your `host.json` disables the route prefix:

```json
{
  "extensions": {
    "http": { "routePrefix": "" }
  }
}
```

---

## Packaging projects

A project can be built into a pip package and reused by the framework. Add a `pyproject.toml` (recommended: in the parent directory of your project) that builds your project into a package.

You'll still provide a `server` module (and a `models.persistent` module if you use databases). In `server/__init__.py`, re-export the submodules from your package:

```python
# server/__init__.py
from your_project.server import web, ws, errorhandler, plugins, middleware, socket
```

To compose **multiple packaged apps** into one server, recreate the `server` module tree and delegate to each app's routes instead of rewriting them:

```python
# server/ws.py — combining two projects
import your_first_project.server.ws
import your_second_project.server.ws


class Route(object):
    """Configure all REST (ws) routes for the server."""

    def __init__(self, server):
        """
        :param server: FastAPI instance
        :type server: fastapi.FastAPI
        """
        your_first_project.server.ws.Route(server)
        your_second_project.server.ws.Route(server)
```

For models, re-export from each package in `models/persistent/__init__.py`:

```python
# single project
from your_project.models.persistent import *

# multiple projects with potential model-name conflicts
from your_first_project.models import persistent as your_first_project
from your_second_project.models import persistent as your_second_project
```

---

## Contributing

Contributions are welcome! To get involved:

1. Open an [issue](https://github.com/frederickney/flask-framework/issues) to discuss a bug or feature.
2. Fork the repository and create a feature branch.
3. Make your change, add or update examples where relevant, and open a pull request.

Working examples live in the [`examples/`](examples/) directory (a `base` app and an `openid` app) — they're a good starting point for both using and contributing to the framework.

---

## License

Distributed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.
