
@staticmethod
def use(databases=['default']):
    import logging
    from .driver import Driver
    def using(func):
        def decorator(*args, **kwargs):
            logging.info('connecting')
            sessions = dict()
            for db_name in databases:
                sessions[db_name] = Driver.start_session_by_name(db_name)
                kwargs.setdefault('sessions', sessions)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logging.error(e)
                result = None
            for name, session in sessions.items():
                session.close()
            logging.info('disconnecting')
            return result

        return decorator

    return using

