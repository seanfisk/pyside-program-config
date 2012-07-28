from pyside_program_config import ProgramConfig
from argparse import Namespace

from ludibrio import Mock

class TestProgramConfig:
    def test_required_configuration_specified_on_command_line(self):
        mock_arg_parser = Mock()
        mock_qsettings = Mock()
        program_config = ProgramConfig(arg_parser=mock_arg_parser,
                                       qsettings=mock_qsettings)
        test_config = [{'key': 'verbosity',
                   'value': 3,
                   'type': int,
                   'help': 'how much output to print',
                   'is_persistent': True},
                   {'key': 'name',
                    'value': 'sean',
                    'type': str,
                    'help': 'your name',
                    'is_persistent': False}]
        for config in test_config:
            with mock_arg_parser:
                mock_arg_parser.add_argument('--' + config['key'],
                                             metavar=config['key'].upper(),
                                             help=config['help'],
                                             type=config['type']) >> None
            program_config.add_required(config['key'],
                                        help=config['help'],
                                        type=config['type'],
                is_persistent=config['is_persistent'])

        namespace_dict = {}
        args = []
        with mock_qsettings:
            for config in test_config:
                namespace_dict[config['key']] = config['value']
                args.append('--' + config['key'])
                args.append(str(config['value']))
                if config['is_persistent']:
                    mock_qsettings.setValue(config['key'], config['value']) >> None
            mock_qsettings.sync() >> None

        namespace = Namespace(**namespace_dict)
        with mock_arg_parser:
            mock_arg_parser.parse_args(args) >> namespace
        real_config = program_config.validate(args)

        for config in test_config:
            assert config['value'] == real_config[config['key']]

