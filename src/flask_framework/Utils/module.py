# coding: utf-8


__author = "Frederick NEY"


import os


def generate(basepath, module, sub_module=None):

    if not os.path.exists(os.path.join(os.path.join(basepath,'Controllers'), os.path.dirname(module))):
        generate(
            basepath, "/".join(
                [module.split('/')[i] for i in  range(0, len(module.split('/')) - 1)]), module.split('/')[-1]
        )
        os.mkdir(os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)), 0o755)
        while not os.path.exists(os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module))):
            "Waiting for path creation"
    if sub_module is not None:
        if os.path.exists(os.path.join(
                    os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)), '__init__.py'
        )):
            fp = open(
                os.path.join(os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)),
                             '__init__.py'),
                "a"
            )
            fp.write(
"""
from . import {}
""".format(module.split("/")[-1])
            )
            fp.close()
        else:
            fp = open(
                os.path.join(os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)), '__init__.py'),
                "w"
            )
            fp.write(
"""# coding: utf-8


from . import {}
""".format(module.split("/")[-1])
            )
            fp.close()
    else:
        if not os.path.exists(os.path.join(
                os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)),
                '__init__.py'
        )):
            fp = open(
                os.path.join(os.path.join(os.path.join(basepath, 'Controllers'), os.path.dirname(module)), '__init__.py'),
                "w"
            )
            fp.write('# coding: utf-8\n\n\n')
            fp.close()
