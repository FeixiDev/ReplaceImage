import utils
import operation
import argparse

class argparse_operator:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='argparse')
        self.setup_parse()

    def setup_parse(self):
        sub_parser = self.parser.add_subparsers()

        self.parser.add_argument('-v',
                                 '--version',
                                 dest='version',
                                 help='Show current version',
                                 action='store_true')

        parser_test = sub_parser.add_parser("update", aliases=['u'], help='update CoSAN Manager console and server')

        self.parser.set_defaults(func=self.main_usage)

        parser_test.set_defaults(func=self.test_operation)


    def main_usage(self,args):
        if args.version:
            print(f'Version: ？')
        else:
            self.parser.print_help()

    def test_operation(self,args):
        print("python3 main.py update")
        obj = operation.UpdateConsoleAndServer()
        obj.main()

    def parser_init(self):
        args = self.parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    cmd = argparse_operator()
    cmd.parser_init()