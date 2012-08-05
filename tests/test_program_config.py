from pyside_program_config import ProgramConfig
from argparse import Namespace

from ludibrio import Mock
import pytest


def pytest_funcarg__test_config(request):
    return [{'key': 'verbosity',
             'value': 3,
             'type': int,
             'help': 'how much output to print',
             'persistent': True},
            {'key': 'name',
             'value': 'sean',
             'type': str,
             'help': 'your name',
             'persistent': False}]


def pytest_funcarg__test_config_default_persistence(request):
    return [{'key': 'default-persistence-test',
             'value': 'meaningless',
             'type': str,
             'help': 'help one'},
            {'key': 'default-persistence-test-two',
             'value': 'no meaning',
             'type': str,
             'help': 'help two'}]


class TestProgramConfig:
    def setup_method(self, method):
        self.mock_arg_parser = Mock()
        self.mock_qsettings = Mock()
        self.program_config = ProgramConfig(arg_parser=self.mock_arg_parser,
                                            qsettings=self.mock_qsettings)

    def test_required_configuration_specified_on_command_line(self,
                                                              test_config):
        self.require_no_fallback(test_config)
        real_config = self.validate_command_line_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_required_configuration_previously_saved(self, test_config):
        self.require_no_fallback(test_config)

        # validate no command line persistence
        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                mock_qsettings.contains(item['key']) >> True
                mock_qsettings.value(item['key']) >> item['value']
                namespace_dict[item['key']] = None
            for item in test_config:
                if item['persistent']:
                    mock_qsettings.setValue(item['key'], item['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args([]) >> namespace
        real_config = self.program_config.validate([])

        self.assert_config_available(test_config, real_config)

    def test_required_configuration_default_value(self, test_config):
        self.require_default(test_config)
        real_config = self.validate_no_command_line_no_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_required_configuration_callback(self):
        # IMPORTANT:
        # Because of the callback function, only use one config item
        item = {'key': 'verbosity',
                'value': 3,
                'help': 'how much output to print',
                'type': int,
                'persistent': False}
        self.add_argument(item)

        def callback(key, help, type):
            assert item['key'] == key
            assert item['help'] == help
            assert item['type'] == type
            return item['value']
        self.program_config.\
            add_required_with_callback(item['key'],
                                       callback,
                                       help=item['help'],
                                       type=item['type'],
                                       persistent=item['persistent'])

        test_config = [item]

        real_config = self.validate_no_command_line_no_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_required_configuration_fails_when_not_given(self, test_config):
        self.require_no_fallback(test_config)
        from pyside_program_config import RequiredKeyError
        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                mock_qsettings.contains(item['key']) >> False
                namespace_dict[item['key']] = None
                # never persist anything upon failure
                # make sure to use a persistent key first

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args([]) >> namespace
        with pytest.raises(RequiredKeyError) as e:
            self.program_config.validate([])
        assert str(e).endswith('Required key not provided: {0}'.
                               format(test_config[0]['key']))

    def test_optional_configuration(self, test_config):
        for item in test_config:
            self.add_argument(item)
            self.program_config.add_optional(item['key'],
                                             help=item['help'],
                                             type=item['type'],
                                             persistent=item['persistent'])
        real_config = self.validate_no_command_line_no_persistence(test_config)
        assert real_config == {}

    def test_add_duplicate_configuration(self, test_config):
        self.require_no_fallback(test_config)
        from pyside_program_config import DuplicateKeyError
        for item in test_config:
            with pytest.raises(DuplicateKeyError) as e:
                self.program_config.add_required(item['key'])
            assert str(e).endswith('Attempt to define duplicate key: {0}'.
                                   format(item['key']))

    def test_default_configuration_never_persisted(self, test_config):
        self.require_default(test_config)
        real_config = self.validate_no_command_line_no_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_default_configuration_on_command_line_never_persisted(
            self, test_config):
        self.require_default(test_config)

        namespace_dict = {}
        args = []
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                namespace_dict[item['key']] = item['value']
                args.append('--' + item['key'])
                args.append(str(item['value']))
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        real_config = self.program_config.validate(args)

        self.assert_config_available(test_config, real_config)

    def test_handles_hyphens_properly(self):
        # argparse converts hyphens to underscores in the Namespace object
        # since hyphens are not valid characters in Python identifiers
        # PySide Program Config should always use hyphens in its command-line
        # xargument names
        # however, this should be transparent to the user
        test_config = [{'key': 'key-with-hyphens',
                        'value': 10,
                        'type': int,
                        'help': 'just a test',
                        'persistent': False}]
        self.require_no_fallback(test_config)
        real_config = self.validate_command_line_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_handles_underscores_properly(self):
        # PySide Program Config should always use hyphens in its command-line
        # argument names
        # however, this should be transparent to the user
        test_config = [{'key': 'key_with_underscores',
                        'value': 10,
                        'type': int,
                        'help': 'just a test',
                        'persistent': False}]
        self.require_no_fallback(test_config)
        real_config = self.validate_command_line_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_default_persistence_is_not_persistent_no_fallback(
            self, test_config_default_persistence):
        for item in test_config_default_persistence:
            self.add_argument(item)
            self.program_config.add_required(item['key'],
                                             help=item['help'],
                                             type=item['type'])
        real_config = self.validate_command_line_no_persistence(
            test_config_default_persistence)
        self.assert_config_available(test_config_default_persistence,
                                     real_config)

    def test_default_persistence_is_not_persistent_optional(
            self, test_config_default_persistence):
        for item in test_config_default_persistence:
            self.add_argument(item)
            self.program_config.add_optional(item['key'],
                                             help=item['help'],
                                             type=item['type'])
        real_config = self.validate_command_line_no_persistence(
            test_config_default_persistence)
        self.assert_config_available(test_config_default_persistence,
                                     real_config)

    def test_default_persistence_is_not_persistent_callback(self):
        # IMPORTANT:
        # Because of the callback function, only use one config item
        item = {'key': 'verbosity',
                'value': 3,
                'help': 'how much output to print',
                'type': int}
        self.add_argument(item)

        def callback(key, help, type):
            assert item['key'] == key
            assert item['help'] == help
            assert item['type'] == type
            return item['value']
        self.program_config.add_required_with_callback(item['key'],
                                                       callback,
                                                       help=item['help'],
                                                       type=item['type'])
        test_config_default_persistence = [item]
        real_config = self.validate_command_line_no_persistence(
            test_config_default_persistence)
        self.assert_config_available(test_config_default_persistence,
                                     real_config)

    def test_default_persistence_is_not_persistent_default(
            self, test_config_default_persistence):
        for item in test_config_default_persistence:
            self.add_argument(item)
            self.program_config.add_required_with_default(item['key'],
                                                          item['value'],
                                                          help=item['help'],
                                                          type=item['type'])
        real_config = self.validate_command_line_no_persistence(
            test_config_default_persistence)
        self.assert_config_available(test_config_default_persistence,
                                     real_config)

    def test_default_argument_list_to_validate_is_sys_argv(self, test_config):
        self.require_no_fallback(test_config)
        
        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                namespace_dict[self.key_from_argparse(item['key'])] = \
                    item['value']
                if item['persistent']:
                    mock_qsettings.setValue(item['key'], item['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(None) >> namespace
        real_config = self.program_config.validate()
        
        self.assert_config_available(test_config, real_config)

    def test_validate_does_not_discard_other_argparse_arguments(self,
                                                                test_config):
        ppc_key = test_config[0]
        argparse_key = test_config[1]
        self.require_no_fallback([ppc_key])
        namespace_dict = {}
        args = []
        with self.mock_qsettings as mock_qsettings:
            for item in [ppc_key, argparse_key]:
                namespace_dict[self.key_from_argparse(item['key'])] = \
                    item['value']
                args.append('--' + item['key'])
                args.append(str(item['value']))
            if ppc_key['persistent']:
                mock_qsettings.setValue(ppc_key['key'], ppc_key['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        real_config = self.program_config.validate(args)

        self.assert_config_available([ppc_key, argparse_key], real_config)


    def key_from_argparse(self, key):
        return key.replace('-', '_')

    def key_to_argparse(self, key):
        return key.replace('_', '-')

    def add_argument(self, item):
        with self.mock_arg_parser as mock_arg_parser:
                mock_arg_parser.add_argument('--' +
                                             self.key_to_argparse(item['key']),
                                             metavar=item['key'].upper(),
                                             help=item['help'],
                                             type=item['type']) >> None

    def require_no_fallback(self, config):
        for item in config:
            self.add_argument(item)
            self.program_config.add_required(item['key'],
                                             help=item['help'],
                                             type=item['type'],
                                             persistent=item['persistent'])

    def require_default(self, config):
        for item in config:
            self.add_argument(item)
            self.program_config.\
                add_required_with_default(item['key'],
                                          item['value'],
                                          help=item['help'],
                                          type=item['type'],
                                          persistent=item['persistent'])

    def validate_no_command_line_no_persistence(self, config):
        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in config:
                mock_qsettings.contains(item['key']) >> False
                namespace_dict[self.key_from_argparse(item['key'])] = None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args([]) >> namespace
        return self.program_config.validate([])

    def validate_command_line_persistence(self, config):
        namespace_dict = {}
        args = []
        with self.mock_qsettings as mock_qsettings:
            for item in config:
                namespace_dict[self.key_from_argparse(item['key'])] = \
                    item['value']
                args.append('--' + item['key'])
                args.append(str(item['value']))
                if item['persistent']:
                    mock_qsettings.setValue(item['key'], item['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        return self.program_config.validate(args)

    def validate_command_line_no_persistence(self, config):
        namespace_dict = {}
        args = []
        with self.mock_qsettings as mock_qsettings:
            for item in config:
                namespace_dict[self.key_from_argparse(item['key'])] = \
                    item['value']
                args.append('--' + item['key'])
                args.append(str(item['value']))
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        return self.program_config.validate(args)

    def assert_config_available(self, test, real):
        for item in test:
            assert item['value'] == real[item['key']]
