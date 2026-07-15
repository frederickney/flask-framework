# coding: utf-8


class LDAPUser(object):
    def __init__(self, attrs):
        for key, attr in attrs.items():
            setattr(self, key, str(attr))

    def get_id(self):
        return getattr(self, 'mail')

    def __repr__(self):
        _str = '{'
        attr = []
        for key in dir(self):
            if not key.startswith('__') and not key.startswith('_') and not key.startswith('set_'):
                attr.append(key)
        for i in range(len(attr)):
            _str += (
                '"{}": "{}"'.format(
                    attr[i],
                    getattr(self, attr[i])
                ) if i == len(attr) - 1
                else '"{}": "{}", '.format(
                    attr[i],
                    getattr(self, attr[i])
                )
            )
        _str += '}'
        return _str

    @property
    def is_active(self):
        return True
