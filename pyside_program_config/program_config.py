""":mod:`pyside_program_config.program_config` --- Program config module
"""

from collections import OrderedDict

class RequiredKeyError(Exception):
    """Error raised when a key specified as required is not given."""
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'Required key not provided: {0}'.format(self.key)

class DuplicateKeyError(Exception):
    """Error raised when an attempt is made to add a key multiple times."""
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'Attempt to define duplicate key: {0}'.format(self.key)
    
class KeyInfo(object):
    """Key configuration item storage object.
    """
    def __init__(self, required, help, type, persistent):
        self.required = required
        self.type = type
        self.help = help
        self.persistent = persistent

class ProgramConfig(object):
    """Main program configuration object. Manages and stores all
    configurations."""
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

    def _key_from_argparse(self, key):
        """Utility method to transform a key for use with :mod:`argparse`.

        :param key: the key to transform
        :type key: :class:`str`
        :returns: the transformed key
        :rtype: :class:`str`
        """
        return key.replace('-', '_')

    def _key_to_argparse(self, key):
        """Utility method to transform a key for the purposes of pulling from
        :mod:`argparse`.

        :param key: the key to transform
        :type key: :class:`str`
        :returns: the transformed key
        :rtype: :class:`str`
        """
        return key.replace('_', '-')
    
    def _add_key(self, key, required, help, type, persistent):
        """Utility method to add a key to the key storage variable.
        
        :param key: the key to add
        :type key: :class:`str`
        :param required: whether the key is required
        :type required: :class:`bool`
        :param help: description of the purpose of the key
        :type help: :class:`str`
        :param type: the type of the key
        :type type: :class:`type`
        :param persistent: whether the key should persist between runs
        :type persistent: :class:`bool`
        :raises: :exc:`DuplicateKeyError` -- when the key has already been added
        """
        if key in self._key_info:
            raise DuplicateKeyError(key)
        self._key_info[key] = KeyInfo(required, help, type, persistent)
        self._arg_parser.add_argument('--' + self._key_to_argparse(key),
                                      metavar=key.upper(),
                                      help=help,
                                      type=type)
    
    def add_required(self, key, help=None, type=str, persistent=False):
        """Add a required configuration item. Since no fallback is provided, the
        configuration will fail to validate if no key is provided.
        
        :param key: the key to add
        :type key: :class:`str`
        :param help: description of the purpose of the key
        :type help: :class:`str`
        :param type: the type of the key
        :type type: :class:`type`
        :param persistent: whether the key should persist between runs
        :type persistent: :class:`bool`
        :raises: :exc:`DuplicateKeyError` -- when the key has already been added
        """
        self._add_key(key, True, help, type, persistent)
        
    def add_optional(self, key, help=None, type=str, persistent=False):
        """Add an optional configuration item.
        
        :param key: the key to add
        :type key: :class:`str`
        :param help: description of the purpose of the key
        :type help: :class:`str`
        :param type: the type of the key
        :type type: :class:`type`
        :param persistent: whether the key should persist between runs
        :type persistent: :class:`bool`
        :raises: :exc:`DuplicateKeyError` -- when the key has already been added
        """
        self._add_key(key, False, help, type, persistent)
    
    def add_required_with_callback(self, key, callback, help=None, type=str,
                                   persistent=False):
        """Add a required configuration item which calls the specified callback
        function. For example, one could use this to ask the user to input
        neceesary information. This function is passed three parameters and should return the
        desired value. The return value is not cast, so it must be cast to the
        proper type if that is what is desired. Here is an example:

        .. code-block:: python

            def my_callback(key, help, type):
               return type(raw_input('Please enter the {0}: '.format(key))

        The specification of the callback function is as follows:

        .. function:: callback(key, help, type)

           Callback function when a required key is not provided. Must return
           the desired value of the key.

           :param key: the original key passed into :meth:`add_required_with_callback`
           :type key: :class:`str`
           :param help: the original help text passed into :meth:`add_required_with_callback`
           :type help: :class:`str`
           :param type: the original type passed into :meth:`add_required_with_callback`
           :type type: :class:`type`
           :returns: the desired value for the key
           :rtype: the original type passed into :meth:`add_required_with_callback`
        
        :param key: the key to add
        :type key: :class:`str`
        :param help: description of the purpose of the key
        :type help: :class:`str`
        :param type: the type of the key
        :type type: :class:`type`
        :param persistent: whether the key should persist between runs
        :type persistent: :class:`bool`
        :raises: :exc:`DuplicateKeyError` -- when the key has already been added
        """
        self.add_required(key, help, type, persistent)
        self._callbacks[key] = callback
    
    def add_required_with_default(self, key, default, help=None, type=str,
                                  persistent=False):
        """Add a required key with a default value.
        
        :param key: the key to add
        :type key: :class:`str`
        :param default: the key's default
        :type default: same type that is passed in as :data:`type`
        :param help: description of the purpose of the key
        :type help: :class:`str`
        :param type: the type of the key
        :type type: :class:`type`
        :param persistent: whether the key should persist between runs
        :type persistent: :class:`bool`
        :raises: :exc:`DuplicateKeyError` -- when the key has already been added
        """
        self.add_required(key, help, type, persistent)
        self._defaults[key] = default
        
    def validate(self, args=[]):
        """Validate the given configurations. When successful, the specified
        configurations are persisted and the entire configuration is returned as
        an :class:`OrderedDict`, ordered based upon when it is entered. Any
        required keys with no fallback that are not preset will raise a
        :exc:`RequiredKeyError`. Any keys required with a callback that are not
        present will cause the callback be called to obtain the value.  Any keys
        required with a default that are not present will assume the
        default. Any optional keys that are not preset will not be present in
        the returned configuration.

        :param args: Command-line arguments to be parsed. Unlike :mod:`argparse`, this does not default to :data:`sys.argv`.
        :type args: :class:`list` of :class:`str`
        :returns: the parsed configuration
        :rtype: :class:`OrderedDict`
        :raises: :exc:`RequiredKeyError` -- when a required key is not provided
        """
        parsed_args = vars(self._arg_parser.parse_args(args))
        # make this ordered so they are returned in inserted order
        config = OrderedDict()
        for key, info in self._key_info.iteritems():
            # order of precedence is:
            #   command-line args, stored settings, default, callback
            # only one of a callback OR a default should be defined for a key
            
            # the value of the option will be None if not passed on the
            # command-line
            parsed_value = parsed_args[self._key_from_argparse(key)]
            if parsed_value is not None:
                value = parsed_value
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
                        if info.required:
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
            if self._key_info[key].persistent and not value_equal_to_default:
                self._qsettings.setValue(key, value)
            
        # ensure settings are written
        self._qsettings.sync()
        
        return config
