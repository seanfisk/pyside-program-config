from pyside_program_config import ProgramConfig
from argparse import Namespace

from nose.tools import assert_equals, assert_raises, assert_is_none
from lettuce import world, step
from ludibrio import Mock

# note to self
# DON'T CREATE A STEP SENTENCE WHICH IS A SUBSTRING OF ANOTHER STEP SENTENCE!

@step('my key is (.+)')
def key(step, key):
    world.key = key
    
@step('my type is (.+)')
def type_is(step, type):
    world.type = eval(type)
    
@step('my value is (.+)')
def value(step, value):
    world.value = world.type(value)
    
@step('I start the program')
def start_the_program(step):
    # using the empty with like this prevents ludibrio from complaining if the
    # mock is not used (such as in the duplicate key test)
    with Mock() as world.mock_arg_parser:
        pass 
    with Mock() as world.mock_qsettings:
        pass
    # inject the mocks
    world.program_config = ProgramConfig(arg_parser=world.mock_arg_parser,
                                         qsettings=world.mock_qsettings)
    
@step('I require the key with no fallback')
def require_the_key(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     help='random help string',
                                     type=world.type)
    world.program_config.add_required(world.key,
                                      help='random help string',
                                      type=world.type)

@step('I require the key with a default value')
def require_the_key_with_default_value(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                metavar=world.key.upper(),
                                help='random help string',
                                type=world.type)
    world.program_config.add_required_with_default(world.key,
                                                   world.value,
                                                   help='random help string',
                                                   type=world.type)

@step('I require the key with a callback')
def require_the_key_with_callback(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     help='random help string',    
                                     type=world.type)
        
    def callback(key, help, type):
        assert_equals(world.key, key)
        assert_equals('random help string', help)
        assert_equals(world.type, type)
        return world.value
    
    world.program_config.add_required_with_callback(world.key,
                                                    callback,
                                                    help='random help string',
                                                    type=world.type)

@step('I require the key without persistence')
def frequire_the_key_without_persistence(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     help='random help string',
                                     type=world.type)
    world.program_config.add_required(world.key,
                                      help='random help string',
                                      type=world.type,
                                      is_persistent=False)
    
@step('I validate the configuration with command-line options with persistence')
def validate_configuration_with_command_line_options(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: world.value})
        mock_arg_parser.parse_args(['--' + world.key, str(world.value)]) \
            >> namespace
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
    world.program_config.set(world.key,
                             world.value)
    
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
    
@step('I validate the configuration with command-line '
      'options without persistence')
def validate_configuration_with_command_line_options_without_persistence(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{world.key: world.value})
        mock_arg_parser.parse_args(['--' + world.key, str(world.value)]) \
            >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.sync()
    world.config = world.program_config.validate(['--' + world.key,
                                                  str(world.value)])

@step('specify the key as optional')
def specify_key_as_optional(step):
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.add_argument('--' + world.key,
                                     metavar=world.key.upper(),
                                     help='random help string',
                                     type=world.type)
    world.program_config.add_optional(world.key,
                                      help='random help string',
                                      type=world.type)
    
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
    assert_raises(DuplicateKeyError,
                  world.program_config.add_required,
                  world.key,
                  help='random help string',
                  type=world.type)
    
@step('cannot set the key')
def cannot_set_the_key(step):
    from pyside_program_config import KeyNotRequiredError
    assert_raises(KeyNotRequiredError,
                  world.program_config.set,
                  world.key,
                  world.value)
    
@step('I require two keys')
def require_two_keys(step):
    for key in ['key1', 'key2']:
        with world.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.add_argument('--' + key,
                                         metavar=key.upper())
            world.program_config.add_required(key)
    
@step('the first key is not persisted '
      'upon validation with an invalid second key')
def attempt_to_validate_with_invalid_second_key(step):
    with world.mock_arg_parser as mock_arg_parser:
        namespace = Namespace(**{'key1': 'value1',
                                 'key2': None})
        mock_arg_parser.parse_args([]) >> namespace
    with world.mock_qsettings as mock_qsettings:
        mock_qsettings.contains('key2') >> False
    # monkey-patch to ensure an order
    try:
        from collections import OrderedDict
    except ImportError:
        from ordereddict import OrderedDict
    world.program_config._key_info = \
        OrderedDict(sorted(world.program_config._key_info.items()))
                
    from pyside_program_config import RequiredKeyError
    assert_raises(RequiredKeyError, world.program_config.validate)
