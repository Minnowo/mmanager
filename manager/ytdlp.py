from ntpath import altsep
import os 
import subprocess
from . import util
from . import const 
from . import db 


class YTDLP_ERROR(Exception):
    pass 

def run_ytdlp(args):

    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr = subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='') 

        for line in p.stderr:
            print(line, end='') 

    print(f"exit with status {p.returncode}")

    return p.returncode


    # process = subprocess.Popen(args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )

    # ( stdout, stderr ) = util.subprocess_communicate( process )

    # if stderr:

    #     raise YTDLP_ERROR(util.non_failing_unicode_decode(stderr, 'utf-8'))

    # print(util.non_failing_unicode_decode(stdout, 'utf-8'))

def get_dl_dir(url):

    output = os.path.join(".", "dl", util.get_str_sha1(url))

    while output.endswith(os.sep) or (os.altsep and output.endswith(altsep)):

        output = output.rstrip(os.sep)

        if os.altsep:

            output = output.rstrip(os.altsep)

    return output

def download_highest_quality_audio(url):
    
    dl = get_dl_dir(url)

    args = [
        const.YT_DLP_PATH, 
        "-f", "bestaudio/best",
        "--extract-audio", 
        "--audio-quality", "0", 
        "--embed-thumbnail", 
        "--add-metadata", "-ciw", 
        "-o", "{}\\{}".format(dl, "%(title)s.%(ext)s"), 
        url
    ]

    arg_ = args.copy()
    arg_.remove(const.YT_DLP_PATH)
    arg_.remove("{}\\{}".format(dl, "%(title)s.%(ext)s"))
    arg_.remove("-o")
    arg_.remove(url)
    arg_ = " ".join(arg_)

    if run_ytdlp(args) == 0:

        handle_finished(dl, arg_, url)


def download_highest_quality_video(url):
    
    dl = get_dl_dir(url)

    args = [
        const.YT_DLP_PATH, 
        "-f" "bestvideo+bestaudio[ext=m4a]/best" ,
        "--embed-thumbnail", "--embed-subs" ,
        "--add-metadata", "-ciw",  
        "-o", "{}\\{}".format(dl, "%(title)s.%(ext)s"), 
    ]

    arg_ = args.copy()
    arg_.remove(const.YT_DLP_PATH)
    arg_.remove("{}\\{}".format(dl, "%(title)s.%(ext)s"))
    arg_.remove("-o")
    arg_.remove(url)
    arg_ = " ".join(arg_)

    if run_ytdlp(args) == 0:

        handle_finished(dl, arg_, url)



def handle_finished(path, arg_, url):

    print(f"scanning {url}")

    for p in os.listdir(path):

        full_p = os.path.join(path, p)

        if os.name == "nt" and not full_p.startswith("\\\\?\\"):
            full_p = "\\\\?\\" + os.path.abspath(full_p)

        mime = os.path.splitext(full_p)[1]

        sha256 = util.get_sha256_file(full_p)

        hash_id = db.add_hash(sha256, arg_, mime)

        url_id = db.add_url(url)

        db.add_url_hash(hash_id, url_id)

        db.add_hash_filename(hash_id, p)

        _hex = sha256.hex()

        print(f"moving to {_hex[0:2]}\\{_hex + mime}")

        os.rename(full_p, os.path.join(const.CONTENT_PATH, _hex[0:2], _hex + mime))
