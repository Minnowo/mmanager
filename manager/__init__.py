from genericpath import isfile
from . import util
from . import opts
from . import const 
from . import db 
from . import ytdlp

import shlex
import os 
import shutil


def print_sep():

    print("="*32)

def restore_file_to(row, path, use_original_filename = False):
    
    HASH_ID = 0
    ROW_ID = 1
    SHA256 = 2
    ARG_ID = 3
    MIME   = 4 

    print(f"Restoring {row}")

    hex_ = row[SHA256].hex()

    if use_original_filename:

        path = db.get_filename(row[HASH_ID])

        if path is None:

            print("Could get get original filename")

            path = os.path.join(const.EXPORT_PATH, hex_ + row[MIME])

        else:

            path = os.path.join(const.EXPORT_PATH, path)


    src = os.path.join(const.CONTENT_PATH, hex_[0:2], hex_ + row[MIME])

    print(f"Restoring from {src} to {path}")

    if os.path.isfile(src):

        util.copy_file(src, path, False)

        util.open_file_location(path)

    else:

        print(f"Could not find src file at '{src}'")



def get_user_input(opts):

    while True:

        inp = input(opts["message"]).strip().lower()

        if inp == "message":
            continue

        if opts.get(inp, None):

            return opts[inp]

def get_user_input_complex(message, parser):

    while True:

        inp = shlex.split(input(message).strip())

        try:

            args = parser.parse_args(inp)

        except opts.Parse_Argument_Exception as e:

            print(f"Argument exception, command '{e.command_name}' expects {e.command_args} arguments.")
            continue

        yield args 


def std_ls(rows):

    count = len(rows)

    print(f"\nFound {count} files with given url.")

    print_sep()

    URL_ID = 0
    ROW_ID = 1
    SHA256 = 2
    ARG_ID = 3
    MIME   = 4 

    # TODO: force this to be all uniform based on data lengths 
    print(f"[n] ---short-name--- mime argument_id")
    for i, row in enumerate(rows):

        print(f'[{i}] {row[SHA256].hex()[0:16] + row[MIME]} {row[ARG_ID]}')

    print()


def run_terminal_loop(url_tuple, rows, message, dl_callback):

    URL_ID = 0
    ROW_ID = 1
    SHA256 = 2
    ARG_ID = 3
    MIME   = 4 

    url_id, url = url_tuple

    row_count = len(rows)

    parser = opts.get_parser_for_terminal_input()

    for args in get_user_input_complex(message, parser):

        if "help" in args:

            parser.show_help()
            continue

        if "exit" in args:
            import sys 
            sys.exit()

        if "continue" in args:
            return 

        if "cls" in args or "clear" in args:

            util.clear_console()
            continue

        if "ls" in args:

            std_ls(rows)
            continue

        if "dl" in args:

            dl_callback(url)
            return 

        if "restore" in args:

            for i, command_args in enumerate(args["restore"]):

                file_index = command_args[0]
                file_index = util.parse_int(file_index, None)

                if file_index is None or \
                   file_index >= row_count or \
                   file_index < 0 :

                    continue

                row = rows[file_index]

                restore_file_to(row, None, True)

        if "save" in args:

            for i, command_args in enumerate(args["save"]):

                file_index = command_args[0]
                save_to    = command_args[1]
                file_index = util.parse_int(file_index, None)

                if file_index is None or \
                   file_index >= row_count or \
                   file_index < 0 :

                    continue

                print(save_to)

                row = rows[file_index]
                restore_file_to(row, save_to, False)
        

    # TODO: insert terminal like env here with commands for the user to type to choose how they want to continue 
 


def down_highest_quality_audio(url):
    
    print_sep()

    url_id = db.get_url(url)

    if url_id == -1:

        ytdlp.download_highest_quality_audio(url)
        return 

    rows = list(db.get_files_from_url_id(url_id))

    std_ls(rows)

    print_sep()

    run_terminal_loop((url_id, url), rows, "\nWhat do you want to do now? >> ", ytdlp.download_highest_quality_audio)
    

def down_highest_quality_video(url):

    print_sep()

    url_id = db.get_url(url)

    if url_id == -1:

        ytdlp.download_highest_quality_video(url)
        return 

    rows = list(db.get_files_from_url_id(url_id))

    std_ls(rows)

    print_sep()

    run_terminal_loop((url_id, url), rows, "\nWhat do you want to do now? >> ", ytdlp.download_highest_quality_video) 

def down_with_custom_args(url):
    pass 
    # TODO: add a way for the user to add custom args 


def handle_url(url):
    
    url = util.basic_url_check(url)

    opts = {
        "message" : f"What do you want to do with {url}?\n"
                     "[1] Download Highest Quality Audio\n"
                     "[2] Download Highest Quality Video\n" 
                     ">> ",
        "1" : down_highest_quality_audio,
        "2" : down_highest_quality_video 
    }

    func = get_user_input(opts)

    func(url)


def main():
    
    parser = opts.get_parser()
    args   = parser.parse_args()

    util.create_hex_folder_structure(const.CONTENT_PATH)

    urls = args.urls 

    l = len(urls)
    for i, x in enumerate(urls):

        print(f"[{i + 1}/{l}] {x}")
        handle_url(x)

