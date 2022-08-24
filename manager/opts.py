
import argparse
from cgitb import reset


def get_parser():
    
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]... URL...",
        add_help=False,
    )

    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-h", "--help",
        action="help",
        help="Print this help message and exit",
    )
    parser.add_argument(
        "urls",
        metavar="URL", nargs="*",
        help=argparse.SUPPRESS,
    )

    # TODO: add actual options here 

    return parser


def get_parser_for_terminal_input():

    # parser = argparse.ArgumentParser(
    #     usage="%(prog)s [OPTION]... URL...",
    #     add_help=False,
    # )

    # parser.add_argument(
    #     "-h", "--help",
    #     dest="help", action="store_true",
    #     help="",
    # )

    # parser.add_argument(
    #     "-ls", "--list",
    #     dest="ls", action="store_true",
    #     help="List the database for given item.",
    # )

    # parser.add_argument(
    #     "-save", "--save",
    #     metavar="N", dest="save", 
    #     help="Save the given item to the given name.",
    # )

    # parser.add_argument(
    #     "-restore", "--restore",
    #     metavar="N", dest="restore", 
    #     help="Same as save but sets the original name.",
    # )

    # parser.add_argument(
    #     "-dl", "--download",
    #     dest="dl", action="store_true",
    #     help="Continue with download option.",
    # )

    parser = Simple_Args_Parser()
    parser.add_argumnet(("help", (0, "Shows help message")))
    parser.add_argumnet(("ls", (0, "Lists the database")))
    parser.add_argumnet(("cls", (0, "Clear the terminal")))
    parser.add_argumnet(("clear", (0, "Clear the terminal")))
    parser.add_argumnet(("dl", (0, "Continues with download")))
    parser.add_argumnet(("restore", (1, "Gets the selected file and restores it with it's original name")))
    parser.add_argumnet(("save", (2, "Gets the selected file and saves it to the given path")))
    parser.add_argumnet(("exit", (0, "Kills the program")))
    parser.add_argumnet(("continue", (0, "Continues the loop")))
    # parser.add_argumnet(("*", 0))

    return parser


class Parse_Exception(Exception):
    pass 

class Parse_Argument_Exception(Parse_Exception):

    def __init__(self, command_name : str = "", command_arguments : int = 0, *args: object) -> None:
        super().__init__(*args)

        self.command_name = command_name
        self.command_args = command_arguments

    def __repr__(self) -> str:

        if not self.command_name and not self.command_args:
            return super().__repr__()

        return f"{super().__repr__()}" \
               f"Command: {self.command_name}, Expected Arguments: {self.command_args}\n"

class Simple_Args_Parser():

    __ARGUMENT_INDEX = 0
    __HELP_INDEX = 1

    def __init__(self) -> None:
        self.opts = dict()


    def add_argumnet(self, arg):

        self.opts[arg[0]] = arg[1]


    def show_help(self):

        for command, info in self.opts.items():

            print(f"Command: '{command}'", f"Args: {info[self.__ARGUMENT_INDEX]}", f"Help: {info[self.__HELP_INDEX]}", sep="\n   ")


    def parse_args(self, list_ : list):

        result = {}

        l = len(list_)

        skip = 0

        for i, item in enumerate(list_):

            if skip > 0:

                skip -= 1
                
                continue

            if item in self.opts:

                # args passed with the given command 
                command_args = []

                if item not in result:

                    result[item] = []

                # add them to arg list for the command 
                result[item].append(command_args)

                a_count = self.opts[item][self.__ARGUMENT_INDEX]

                # if there is no arguments just set true so we know it was at least called
                if a_count <= 0:

                    command_args.append(True)
                    continue


                # grab arguments for the given command 
                for n in range(a_count):

                    if i + n + 1 >= l:
                        raise Parse_Argument_Exception(item, a_count, f"Not enough arguments provided for {item}")

                    command_args.append(list_[i + n + 1])

                # we can now skip over the arguments 
                skip = a_count


            # if the parser supports wildcard command 
            elif "*" in self.opts:

                # just grab anything that isn't a command or command argument 
                if "*" not in result:

                    result["*"] = []

                result["*"].append(item)


        return result 






