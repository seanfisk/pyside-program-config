from pyside_program_config import ProgramConfig
from argparse import Namespace

from ludibrio import Mock
import pytest

def pytest_funcarg__test_config(request):
    return [{'key': 'verbosity',
             'value': 3,
             'type': int,
             'help': 'how much output to print',
             'is_persistent': True},
             {'key': 'name',
              'value': 'sean',
              'type': str,
              'help': 'your name',
              'is_persistent': False}]

class TestProgramConfig:
    def setup_method(self, method):
        self.mock_arg_parser = Mock()
        self.mock_qsettings = Mock()
        self.program_config = ProgramConfig(arg_parser=self.mock_arg_parser,
                                            qsettings=self.mock_qsettings)

    def require_no_fallback(self, config):
        for item in config:
            with self.mock_arg_parser as mock_arg_parser:
                mock_arg_parser.add_argument('--' + item['key'],
                                             metavar=item['key'].upper(),
                                             help=item['help'],
                                             type=item['type']) >> None
            self.program_config.add_required(item['key'],
                                        help=item['help'],
                                        type=item['type'],
                is_persistent=item['is_persistent'])

    def validate_no_command_line_no_persistence(self, config):
        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in config:
                mock_qsettings.contains(item['key']) >> False
                namespace_dict[item['key']] = None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args([]) >> namespace
        return self.program_config.validate([])

    def assert_config_available(self, test, real):
        for item in test:
            assert item['value'] == real[item['key']]

    def test_required_configuration_specified_on_command_line(self, test_config):
        self.require_no_fallback(test_config)
        namespace_dict = {}
        args = []
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                namespace_dict[item['key']] = item['value']
                args.append('--' + item['key'])
                args.append(str(item['value']))
                if item['is_persistent']:
                    mock_qsettings.setValue(item['key'], item['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        real_config = self.program_config.validate(args)

        self.assert_config_available(test_config, real_config)

    def test_required_configuration_previously_saved(self, test_config):
        self.require_no_fallback(test_config)

        namespace_dict = {}
        with self.mock_qsettings as mock_qsettings:
            for item in test_config:
                mock_qsettings.contains(item['key']) >> True
                mock_qsettings.value(item['key']) >> item['value']
                namespace_dict[item['key']] = None
            for item in test_config:
                if item['is_persistent']:
                    mock_qsettings.setValue(item['key'], item['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with self.mock_arg_parser as mock_arg_parser:
            mock_arg_parser.parse_args([]) >> namespace
        real_config = self.program_config.validate([])

        self.assert_config_available(test_config, real_config)

    def test_required_configuration_default_value(self, test_config):
        for item in test_config:
            with self.mock_arg_parser as mock_arg_parser:
                mock_arg_parser.add_argument('--' + item['key'],
                                             metavar=item['key'].upper(),
                                             help=item['help'],
                                             type=item['type']) >> None
            self.program_config.add_required_with_default(item['key'],
                                                       item['value'],
                                                       help=item['help'],
                                                       type=item['type'],
                                                       is_persistent=item['is_persistent'])
        real_config = self.validate_no_command_line_no_persistence(test_config)
        self.assert_config_available(test_config, real_config)

    def test_required_configuration_callback(self):
        # IMPORTANT:
        # Because of the callback function, only use one config item
        item = {'key': 'verbosity',
                'value': 3,
                'help': 'how much output to print',
                'type': int,
                'is_persistent': False}
        with self.mock_arg_parser as mock_arg_parser:
                mock_arg_parser.add_argument('--' + item['key'],
                                             metavar=item['key'].upper(),
                                             help=item['help'],    
                                             type=item['type']) >> None
        def callback(key, help, type):
            assert item['key'] == key
            assert item['help'] == help
            assert item['type'] == type
            return item['value']
        self.program_config.add_required_with_callback(item['key'],
                                                       callback,
                                                       help=item['help'],
                                                       type=item['type'],
            is_persistent=item['is_persistent'])

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
        with pytest.raises(RequiredKeyError):
            self.program_config.validate([])

    def test_optional_configuration(self, test_config):
        for item in test_config:
            with self.mock_arg_parser as mock_arg_parser:
                mock_arg_parser.add_argument('--' + item['key'],
                                             metavar=item['key'].upper(),
                                             help=item['help'],
                                             type=item['type']) >> None
            self.program_config.add_optional(item['key'],
                                        help=item['help'],
                                        type=item['type'],
                is_persistent=item['is_persistent'])
        real_config = self.validate_no_command_line_no_persistence(test_config)
        assert real_config == {}
