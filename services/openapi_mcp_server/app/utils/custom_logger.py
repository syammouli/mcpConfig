import logging
import sys



def get_logger():

    app_logger = logging.getLogger("app")
    if(app_logger.hasHandlers() == False):
        print(f"app logger id: {hex(id(app_logger))}")


        stream_handler = logging.StreamHandler(stream=sys.stdout)
        simple_formatter = logging.Formatter(
            "{asctime} - {name} - {levelname} - {module} - {funcName} - {message}",
            style="{",
        )
        stream_handler.setFormatter(simple_formatter)


        app_logger.setLevel(logging.INFO)

        app_logger.addHandler(stream_handler)
    else:
        pass

    return app_logger