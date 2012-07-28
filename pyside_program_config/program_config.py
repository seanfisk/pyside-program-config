from collections import OrderedDict

class RequiredKeyError(Exception):
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'Required key not provided: {0}'.format(self.key)

class DuplicateKeyError(Exception):
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'Attempt to define duplicate key: {0}'.format(self.key)
    
class KeyInfo(object):
    def __init__(self, is_required, help, type, is_persistent):
        self.is_required = is_required
        self.type = type
        self.help = help
        self.is_persistent = is_persistent

class ProgramConfig(object):
    def __init__(self, arg_parser=None, qsettings=None):
        # this is not the best technique, but it allows ease of use without
        # creating explicit dependencies on ArgumentParser and QSettings,
        # and makes this module more easily testable 
        if arg_parser is None:
            from argparse import ArgumentParser
            arg_parser = ArgumentParser()
        if qsettings is None:
            from PySide.QtCore import QSettings
            qsettings = QSettings()
            
        self._arg_parser = arg_parser
        self._qsettings = qsettings
        # make this ordered so they are validated in order of insertion
        self._key_info = OrderedDict()
        # store defaults in a separate dictionary so we can have None defaults
        self._defaults = {}
        # similar story here
        self._callbacks = {}
    
    def _add_key(self, key, is_required, help, type, is_persistent):
        if key in self._key_info:
            raise DuplicateKeyError(key)
        self._key_info[key] = KeyInfo(is_required, help, type, is_persistent)
        self._arg_parser.add_argument('--' + key,
                                      metavar=key.upper(),
                                      help=help,
                                      type=type)
    
    def add_required(self, key, help=None, type=str, is_persistent=True):
        self._add_key(key, True, help, type, is_persistent)
        
    def add_optional(self, key, help=None, type=str, is_persistent=True):
        self._add_key(key, False, help, type, is_persistent)
    
    def add_required_with_callback(self, key, callback, help=None, type=str,
                                   is_persistent=True):
        self.add_required(key, help, type, is_persistent)
        self._callbacks[key] = callback
    
    def add_required_with_default(self, key, default, help=None, type=str,
                                  is_persistent=True):
        self.add_required(key, help, type, is_persistent)
        self._defaults[key] = default
        
    def validate(self, args=[]):
        parsed_args = vars(self._arg_parser.parse_args(args))
        # make this ordered so they are returned in inserted order
        config = OrderedDict()
        for key, info in self._key_info.iteritems():
            # order of precedence is:
            #   command-line args, stored settings, default, callback
            # only one of a callback OR a default should be defined for a key
            
            # the value of the option will be None if not passed on the
            # command-line
            if parsed_args[key]:
                value = parsed_args[key]
            elif self._qsettings.contains(key):
                value = info.type(self._qsettings.value(key))
            else:
                try:
                    value = self._defaults[key]
                except KeyError:
                    try:
                        value = self._callbacks[key](key,
                                                     info.help,
                                                     info.type)
                    except KeyError:
                        if info.is_required:
                            raise RequiredKeyError(key)
                        else:
                            continue
            config[key] = value
            
        # once all are verified, commit all to QSettings
        for key, value in config.iteritems():
            value_equal_to_default = False
            try:
                value_equal_to_default = self._defaults[key] == value
            except KeyError:
                # key doesn't have a default
                pass
            if self._key_info[key].is_persistent and not value_equal_to_default:
                self._qsettings.setValue(key, value)
            
        # ensure settings are written
        self._qsettings.sync()
        
        return config
