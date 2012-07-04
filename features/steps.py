from argparse import Namespace

from nose.tools import assert_equals, assert_raises
from lettuce import world, step
from ludibrio import Mock

@step('my key is (.+)')
def key(step, key):
    world.key = key
    
@step('my type is (.+)')
def type_is(step, the_type):
    world.type = eval(the_type)
    
@step('my value is (.+)')
def value(step, value):
    world.value = world.type(value)
    
@step('I start the program')
def start_the_program(step):
    # simple way to create a mock with no expectations (yet)
    world.mock_arg_parser = Mock()
    # using the empty with like this prevents ludibrio from complaining if the
    # mock is not used (such as in the duplicate key test) 
    with Mock() as world.mock_qsettings:
        pass
    with Mock() as QSettings:
        from PySide.QtCore import QSettings
        QSettings() >> world.mock_qsettings
    from pyside_program_config import ProgramConfig
    # inject the mocks
    world.program_config = ProgramConfig(arg_parser=world.mock_arg_parser,
                                         qsettings=world.mock_qsettings)
    
@step('I require the key')
def require_the_key(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     type=world.type,
                                     help='random help string')
    world.program_config.add_required(world.key, world.type,
                                      'random help string')

@step('I require the key with a default value')
def require_the_key_with_default_value(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                metavar=world.key.upper(),
                                type=world.type,
                                help='random help string')
    world.program_config.add_required_with_default(world.key, world.type,
                                                   'random help string',
                                                   world.value)

@step('I require the key with a callback')
def require_the_key_with_callback(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     type=world.type,
                                     help='random help string')    
    def callback(key, the_type, the_help):
        assert_equals(world.key, key)
        assert_equals(world.type, the_type)
        assert_equals('random help string', the_help)
        return world.value
        
    world.program_config.add_required_with_callback(world.key, world.type,
                                      'random help string', callback)
    
@step('I validate the configuration with command-line options')
def validate_configuration_with_command_line_options(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: world.value})
        mock_arg_parser.parse_args(['--' + world.key, str(world.value)]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.setValue(world.key, world.value)
        mock_qsettings.sync()
    world.config = world.program_config.validate(['--' + world.key,
                                                  str(world.value)])
        
@step('my key and value have been previously saved')
def key_and_value_have_been_previously_saved(step):
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.setValue(world.key, world.type(world.value))
        mock_qsettings.contains(world.key) >> True
        mock_qsettings.value(world.key) >> world.value
    world.program_config.set(world.key, world.value, world.type,
                             'random help string')

@step('I validate the configuration with the previously saved values')
def validate_the_configuration_with_previously_saved_values(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains(world.key) >> True
        mock_qsettings.value(world.key) >> world.value
        mock_qsettings.setValue(world.key, world.value)
        mock_qsettings.sync()
    world.config = world.program_config.validate()
    
@step('I validate the configuration with the default values')
def validate_the_configuration_with_default_values(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains(world.key) >> False
        mock_qsettings.setValue(world.key, world.value)
        mock_qsettings.sync()
    world.config = world.program_config.validate()
    
@step('I validate the configuration with the callback')
def validate_the_configuration_with_callback(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains(world.key) >> False
        mock_qsettings.setValue(world.key, world.value)
        mock_qsettings.sync()
    world.config = world.program_config.validate()

@step('specify the key as optional')
def specify_key_as_optional(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     type=world.type,
                                     help='random help string')
    world.program_config.add_optional(world.key, world.type,
                                      'random help string')
    
@step('validate the configuration without the optional configuration provided')
def validate_the_configuration_without_optional(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains(world.key) >> False
        mock_qsettings.sync()
    config = world.program_config.validate()
    assert_raises(KeyError, config.__getitem__, world.key)    
    
@step('program fails to validate the configuration')
def fails_to_validate_configuration(step):
    from pyside_program_config import RequiredKeyError
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains(world.key) >> False
    assert_raises(RequiredKeyError, world.program_config.validate)
    
@step('configuration is available')
def config_is_available(step):
    assert_equals(world.value, world.config[world.key])
    
@step('cannot require the key again')
def cannot_require_key_again(step):
    from pyside_program_config import DuplicateKeyError
    assert_raises(DuplicateKeyError, world.program_config.add_required, world.key, world.type, 'random help string')