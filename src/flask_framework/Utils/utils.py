# coding: utf-8


__author__ = "Frederick NEY"


import os

from .module import generate


def make_auth():
    pass


def make_middleware(basepath, middleware):

    fp = open(os.path.join(os.path.join(basepath, 'Server'), 'Middleware.py'), "a")
    fp.write(
"""
class {}(object):

    @classmethod
    def use(cls):
        \"\"\"
        :return: call to the decorated function
        \"\"\"

        def using(func):
            def decorator(*args, **kwargs):

                result = func(*args, **kwargs)
                return result

            return decorator

        return using

""".format(middleware)
    )
    fp.close()
    pass


def make_controller(basepath, controller):
    generate(basepath, controller)
    fp = open(
        os.path.join(
            os.path.join(os.path.join(basepath,'Controllers'),os.path.dirname(controller)),
            "{}.py".format(os.path.basename(controller)),
        ),
        "w"
    )
    fp.write("""# coding: utf-8


class Controller(object):

    @staticmethod
    def index():
        return
""")
    fp.close()
    fp = open(
        os.path.join(os.path.join(os.path.join(basepath, 'Controllers'),os.path.dirname(controller)),'__init__.py'),"a"
    )
    fp.write("from .{} import Controller as {}\n".format(
        os.path.basename(controller), os.path.basename(controller)
    ))
    fp.close()
