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

        parser_test = sub_parser.add_parser("update", aliases=['u'], help='Update CoSAN Manager console and server')

        parser_arm = sub_parser.add_parser("arm", aliases=['a'], help='Update ARM image')
        parser_arm.add_argument('-pull',
                                 dest='pull',
                                 help='Use feixitek warehouse',
                                 action='store_true')


        self.parser.set_defaults(func=self.main_usage)

        parser_test.set_defaults(func=self.test_operation)

        parser_arm.set_defaults(func=self.arm_operation)



    def main_usage(self,args):
        if args.version:
            print(f'Version: ？')
        else:
            self.parser.print_help()

    def test_operation(self,args):
        print("python3 main.py update")
        obj = operation.UpdateConsoleAndServer()
        obj.main()

    def arm_operation(self,args):
        flag = operation.UpdateArmImage()
        if args.pull:
            print("python3 main.py arm -pull")
            flag.main_pull()
        else:
            print("python3 main.py arm")
            flag.main_un_pull()

    def arm_pull_operation(self,args):
        print("python3 main.py arm -pull")

    def parser_init(self):
        args = self.parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    cmd = argparse_operator()
    cmd.parser_init()