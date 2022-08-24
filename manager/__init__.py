from . import util
from . import opts
from . import const 
from . import db 
from . import ytdlp

def get_user_input(opts):

    while True:

        inp = input(opts["message"]).strip().lower()

        if inp == "message":
            continue

        if opts.get(inp, None):

            return opts[inp]



def down_highest_quality_audio(url):
    
    url_id = db.get_url(url)

    if url_id == -1:

        ytdlp.download_highest_quality_audio(url)
        return 

    rows = list(db.get_files_from_url_id(url_id))

    count = len(rows)

    print(f"Found {count} files with given url.")

    URL_ID = 0
    ROW_ID = 1
    SHA256 = 2
    ARG_ID = 3
    MIME   = 4 

    print(f"[n] ---short-name--- mime argument_id")
    for i, row in enumerate(rows):

        print(f'[{i}] {row[SHA256].hex()[0:16] + row[MIME]} {row[ARG_ID]}')

def down_highest_quality_video(url):
    pass 


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

