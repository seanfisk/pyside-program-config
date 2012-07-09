from pyside_program_config import ProgramConfig
from argparse import Namespace

from nose.tools import assert_equals, assert_raises, assert_is_none
from lettuce import world, step, before
from ludibrio import Mock

# Notes to self
# 1. Don't create a step sentence which is a substring of another step sentence!
# 2. lettuce seems to eat the last line of output from a step when printing!
# 3. ludibirio apparently doesn't take the mock expectations when using two
#    with statements in the same method (i.e., same scope)
# 4. ludibrio doesn't like having two with statement to setup mocks. To limit
#    trouble just don't do it!

@before.each_scenario
def setup_mocks(scenario):
    # using the empty with like this prevents ludibrio from complaining if the
    # mock is not used (such as in the duplicate key test)
    with Mock() as world.mock_arg_parser:
        pass 
    with Mock() as world.mock_qsettings:
        pass
    # inject the mocks
    world.program_config = ProgramConfig(arg_parser=world.mock_arg_parser,
                                         qsettings=world.mock_qsettings)

@step('I have an example configuration')
def example_config(step):
    world.test_config = [{'key': 'verbosity',
                        'value': 3,
                        'type': int,
                        'help': 'how much output to print',
                        'is_persistent': True},
                       {'key': 'name',
                        'value': 'sean',
                        'type': str,
                        'help': 'your name',
                        'is_persistent': False}]
    
@step('I have the configuration')
def have_config(step):
    world.test_config = step.hashes
                                
@step('I require the configuration with no fallback')
def require_config_no_fallback(step):
    for config in world.test_config:
        with world.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.add_argument('--' + config['key'],
                                         metavar=config['key'].upper(),
                                         help=config['help'],
                                         type=config['type']) >> None
        world.program_config.add_required(config['key'],
                                          help=config['help'],
                                          type=config['type'],
                                          is_persistent=config['is_persistent'])
        
@step('I require the configuration with default values')
def require_the_key_with_default_value(step):
    for config in world.test_config:
        with world.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.add_argument('--' + config['key'],
                                         metavar=config['key'].upper(),
                                         help=config['help'],
                                         type=config['type']) >> None
        world.program_config.add_required_with_default(config['key'],
                                                       config['value'],
                                                       help=config['help'],
                                                       type=config['type'],
                                                       is_persistent=config['is_persistent'])        

@step('I require the configuration with a callback')
def require_the_key_with_callback(step):
    # IMPORTANT:
    # Because of the callback function, only use one config in world.test_config
    for config in world.test_config:
        with world.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.add_argument('--' + config['key'],
                                         metavar=config['key'].upper(),
                                         help=config['help'],    
                                         type=config['type']) >> None
        def callback(key, help, type):
            assert_equals(config['key'], key)
            assert_equals(config['help'], help)
            assert_equals(config['type'], type)
            return config['value']
        world.program_config.add_required_with_callback(config['key'],
                                                        callback,
                                                        help=config['help'],
                                                        type=config['type'],
                                                        is_persistent=config['is_persistent'])

@step('specify the configuration as optional')
def specify_config_as_optional(step):
    for config in world.test_config:
        with world.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.add_argument('--' + config['key'],
                                         metavar=config['key'].upper(),
                                         help=config['help'],
                                         type=config['type']) >> None
        world.program_config.add_optional(config['key'],
                                          help=config['help'],
                                          type=config['type'],
                                          is_persistent=config['is_persistent'])        

@step('I validate the configuration with a previously saved configuration')
def validate_config_with_previously_saved_config(step):
    namespace_dict = {}
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            mock_qsettings.contains(config['key']) >> True
            mock_qsettings.value(config['key']) >> config['value']
            namespace_dict[config['key']] = None
        for config in world.test_config:
            if config['is_persistent']:
                mock_qsettings.setValue(config['key'], config['value']) >> None
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args([]) >> namespace
    world.real_config = world.program_config.validate([])
    
@step('I validate the configuration with command-line options with persistence')
def validate_config_with_command_line_options_with_persistence(step):
    namespace_dict = {}
    args = []
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            namespace_dict[config['key']] = config['value']
            args.append('--' + config['key'])
            args.append(str(config['value']))
            if config['is_persistent']:
                mock_qsettings.setValue(config['key'], config['value']) >> None
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args(args) >> namespace
    world.real_config = world.program_config.validate(args)
    
@step('I validate the configuration with command-line options '
      'without persistence')
def validate_config_with_command_line_options_without_persistence(step):
    namespace_dict = {}
    args = []
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            namespace_dict[config['key']] = config['value']
            args.append('--' + config['key'])
            args.append(str(config['value']))
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args(args) >> namespace
    world.real_config = world.program_config.validate(args)

@step('I validate the configuration without command-line options '
      'with persistence')
def validate_config_without_command_line_options_with_persistence(step):
    namespace_dict = {}
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            mock_qsettings.contains(config['key']) >> False
            namespace_dict[config['key']] = None
        for config in world.test_config:
            if config['is_persistent']:
                mock_qsettings.setValue(config['key'], config['value']) >> None
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args([]) >> namespace
    world.real_config = world.program_config.validate([])
    
@step('I validate the configuration without command-line options '
      'without persistence')
def validate_config_without_command_line_options_without_persistence(step):
    namespace_dict = {}
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            mock_qsettings.contains(config['key']) >> False
            namespace_dict[config['key']] = None
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args([]) >> namespace
    world.real_config = world.program_config.validate([])

@step('program fails to validate the configuration')
def fails_to_validate_configuration(step):
    from pyside_program_config import RequiredKeyError
    namespace_dict = {}
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            mock_qsettings.contains(config['key']) >> False
            namespace_dict[config['key']] = None
            # never persist anything upon failure
            # make sure to use a persistent key first

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args([]) >> namespace
    assert_raises(RequiredKeyError, world.program_config.validate)
    
@step('configuration is available')
def config_is_available(step):
    for test_config in world.test_config:
        assert_equals(test_config['value'], world.real_config[test_config['key']])
    
@step('cannot require the configuration again')
def cannot_require_config_again(step):
    from pyside_program_config import DuplicateKeyError
    for config in world.test_config:
        assert_raises(DuplicateKeyError,
                      world.program_config.add_required,
                      config['key'])
        
#@step('cannot set the configuration')
#def cannot_set_config(step):
#    from pyside_program_config import KeyNotRequiredError
#    for config in world.test_config:
#        assert_raises(KeyNotRequiredError,
#                      world.program_config.set,
#                      config['key'],
#                      config['value'])
    
@step('I validate the configuration with command-line options equivalent'
      'to defaults')
def validate_config_with_command_line_options_equivalent_to_defaults(step):
    namespace_dict = {}
    args = []
    with world.mock_qsettings as mock_qsettings:
        for config in world.test_config:
            namespace_dict[config['key']] = config['value']
            args.append('--' + config['key'])
            args.append(str(config['value']))
        mock_qsettings.sync() >> None

    namespace = Namespace(**namespace_dict)
    with world.mock_arg_parser as mock_arg_parser:
        mock_arg_parser.parse_args(args) >> namespace
    world.program_config.validate(args)
    
#
#@step('I require the key without persistence')
#def frequire_the_key_without_persistence(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        mock_arg_parser.add_argument('--' + world.key,
#                                     metavar=world.key.upper(),
#                                     help='random help string',
#                                     type=world.type)
#    world.program_config.add_required(world.key,
#                                      help='random help string',
#                                      type=world.type,
#                                      is_persistent=False)
#    
#@step('I validate the configuration with command-line options with persistence')
#def validate_configuration_with_command_line_options(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        namespace = Namespace(**{world.key: world.value})
#        mock_arg_parser.parse_args(['--' + world.key, str(world.value)]) \
#            >> namespace
#    with world.mock_qsettings as mock_qsettings:
#        mock_qsettings.setValue(world.key, world.value)
#        mock_qsettings.sync()
#    world.config = world.program_config.validate(['--' + world.key,
#                                                  str(world.value)])
#    
#@step('I validate the configuration with the previously saved values')
#def validate_the_configuration_with_previously_saved_values(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        namespace = Namespace(**{world.key: None})
#        mock_arg_parser.parse_args([]) >> namespace
#    with world.mock_qsettings as mock_qsettings:
#        mock_qsettings.contains(world.key) >> True
#        mock_qsettings.value(world.key) >> world.value
#        mock_qsettings.setValue(world.key, world.value)
#        mock_qsettings.sync()
#    world.config = world.program_config.validate()
#    
#@step('I validate the configuration with the default values')
#def validate_the_configuration_with_default_values(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        namespace = Namespace(**{world.key: None})
#        mock_arg_parser.parse_args([]) >> namespace
#    with world.mock_qsettings as mock_qsettings:
#        mock_qsettings.contains(world.key) >> False
#        mock_qsettings.setValue(world.key, world.value)
#        mock_qsettings.sync()
#    world.config = world.program_config.validate()
#    
#@step('I validate the configuration with the callback')
#def validate_the_configuration_with_callback(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        namespace = Namespace(**{world.key: None})
#        mock_arg_parser.parse_args([]) >> namespace
#    with world.mock_qsettings as mock_qsettings:
#        mock_qsettings.contains(world.key) >> False
#        mock_qsettings.setValue(world.key, world.value)
#        mock_qsettings.sync()
#    world.config = world.program_config.validate()
#    
#@step('validate the configuration without the optional configuration provided')
#def validate_the_configuration_without_optional(step):
#    with world.mock_arg_parser as mock_arg_parser:
#        namespace = Namespace(**{world.key: None})
#        mock_arg_parser.parse_args([]) >> namespace
#    with world.mock_qsettings as mock_qsettings:
#        mock_qsettings.contains(world.key) >> False
#        mock_qsettings.sync()
#    config = world.program_config.validate()
#    assert_raises(KeyError, config.__getitem__, world.key)    
