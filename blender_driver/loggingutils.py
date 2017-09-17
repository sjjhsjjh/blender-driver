#!/usr/bin/python
# (c) 2017 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Python module for the Blender Driver logging utilities.

This module is common to the initial Blender context and the Blender Game Engine
context. This means that it is imported by the launch.py script and by the
controllers module.

Can only be imported as a module, not run as a script, sorry.
"""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3.5/howto/logging.html
# Reference is here: https://docs.python.org/3.5/library/logging.html
import logging
import logging.config

def filter_warning(record):
    # print('filter_warning', record.levelno)
    return 1 if record.levelno == logging.WARNING else 0

def filter_not_warning(record):
    # print('filter_not_warning', record.levelno)
    return 0 if record.levelno == logging.WARNING else 1

class LogRecord(logging.LogRecord):
    """LogRecord subclass that uses format instead of percent."""
    
    def getMessage(self):
        # print('getMessage "{}" {} {} {}'.format(
        #     self.msg, isinstance(self.msg, str), self.args
        #     , isinstance(self.args, dict)))
        if isinstance(self.msg, str):
            if isinstance(self.args, dict):
                return self.msg.format(self.args)
            else:
                return self.msg.format(*self.args)
        try:
            _ = self.args[0]
            raise TypeError("Log message with args but msg isn't string.")
        except IndexError:
            return str(self.msg)

def initialise_logging(verbose):
    # ToDo: Change this so that it doesn't use the logging root. Maybe instead
    # create a Logger that doesn't propagate?
    #
    # Get rid of the default logging handlers.
    logging.config.dictConfig({'version': 1, 'root': {'handlers':[]}})
    logger = logging.root
    #
    # Convenience variables for all the formats.
    terseMessageformat = '%(levelname)s %(message)s'
    verboseMessageformat = (
        '%(asctime)s.%(module)s.%(funcName)s.%(levelname)s %(message)s')
    dateFormat = '%H:%M:%S'
    #
    # Set a logging factory to use the LogRecord subclass above instead of the
    # default.
    def factory(*args, **kwargs):
        return LogRecord(*args, **kwargs)
    logging.setLogRecordFactory(factory)
    #
    # In verbose mode, everything gets logged verbosely, which is simple.
    # Otherwise, warnings get logged verbosely and everything else gets logged
    # briefly.
    if verbose:
        defaultHandler = logging.StreamHandler()
        defaultHandler.setFormatter(logging.Formatter(verboseMessageformat
                                                      , dateFormat))
        logger.addHandler(defaultHandler)
        logger.setLevel(logging.DEBUG)
    else:
        defaultHandler = logging.StreamHandler()
        defaultHandler.addFilter(filter_not_warning)
        defaultHandler.setFormatter(logging.Formatter(terseMessageformat
                                                      , None))
        warningHandler = logging.StreamHandler()
        warningHandler.addFilter(filter_warning)
        warningHandler.setFormatter(logging.Formatter(verboseMessageformat
                                                      , dateFormat))
        logger.addHandler(defaultHandler)
        logger.addHandler(warningHandler)
        logger.setLevel(logging.INFO)

    return "Logging level: {}.".format(
        logging.getLevelName(logger.getEffectiveLevel()))
