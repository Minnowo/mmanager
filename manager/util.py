import os 
import hashlib
import subprocess
import shutil
import urllib.parse
from re import compile
from . import const 

DIGIT              = compile(r"([0-9]+)")
BASIC_HTTP_CHECK   = compile(r"(https?://)(.+)")


def natural_sort_key(s, _nsre=DIGIT):
    """    Provides a natural sort when used with sort(list, key=natural_sort_key) or sorted(list, key=natural_sort_key) """
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


def create_directory_from_file_name(path : str) -> bool:
    """    Creates a directory from the file path.    """
    return create_directory(os.path.dirname(path))



def create_directory(path : str) -> bool:
    """    Creates the given directory.    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return os.path.isdir(path)


def remove_file(path : str) -> bool:
    """    Deletes the given file.    """
    try:
        os.unlink(path)
        return True 
    except OSError:
        pass
    return False 



def remove_directory(path : str) -> bool:
    """    Deletes the given directory.    """
    try:
        shutil.rmtree(path, ignore_errors=False)
        return True 
    except OSError:
        pass 
    return False 



def parse_int(value : str, default = None):
    """    Convert 'value' to int    """

    if not value:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def iter_file(file, chunk_size : int = 262144): # 256kb 
    """    takes a file handle and yields it in blocks    """

    next_block = file.read(chunk_size)
    
    while len( next_block ) > 0:
        
        yield next_block
        
        next_block = file.read(chunk_size)



async def iter_file_async(file, chunk_size : int = 262144): # 256kb 
    """    takes a file handle and yields it in blocks    """

    next_block = await file.read(chunk_size)
    
    while len( next_block ) > 0:
        
        yield next_block
        
        next_block = await file.read(chunk_size)
              

def get_sha256_file(path : str):
  
    h_sha256 = hashlib.sha256()
    
    with open(path, 'rb') as file:
        
        for block in iter_file(file):
            
            h_sha256.update( block )
            
    return h_sha256.digest()

def get_extra_file_hash(path : str) -> tuple:
    """    returns a tuple of hashes as bytes in the order ( md5, sha1, sha256, sha512 )    """  
    h_md5    = hashlib.md5()
    h_sha1   = hashlib.sha1()
    h_sha256 = hashlib.sha256()
    h_sha512 = hashlib.sha512()
    
    with open(path, 'rb') as file:
        
        for block in iter_file(file):
            
            h_md5.update( block )
            h_sha1.update( block )
            h_sha256.update( block )
            h_sha512.update( block )
            
    return ( h_md5.digest(), 
             h_sha1.digest(), 
             h_sha256.digest(),
             h_sha512.digest() )
    


def get_temp_file_in_path(path : str, ext='.tmp'):
    """ returns a path in the given folder that does not exist """

    filename = os.path.join(path, os.urandom(32).hex() + ext)

    while os.path.isfile(filename):
        filename = os.path.join(path, os.urandom(32).hex() + ext)

    return filename




def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    



def in_range(item, range : tuple):

    """ 
    checks if the given number is in the range of the given min and max (inclusive) 
    
    item : the number to check

    range : the min and max range as a tuple
    """

    (min, max) = range 

    return item >= min and item <= max 



def create_hex_folder_structure(path):

    for i in range(256):

        f = hex(i)[2:].zfill(2)
        
        create_directory(os.path.join(path, f))


def get_str_sha1(st : str):

    h_sha1   = hashlib.sha1()
    h_sha1.update(st.encode())
    return h_sha1.digest().hex()


def basic_url_check(url : str):

    return url

    m = BASIC_HTTP_CHECK.match(url)

    if m:

        # take the https:// and quote everything after it 

        return m.group(1) + urllib.parse.quote(url[len(m.group(1)):])

    return "https://" + urllib.parse.quote(url) 


def default_decode( data ):
    
    default_encoding = 'windows-1252'
    
    default_text = str( data, default_encoding, errors = 'replace' )
    
    default_error_count = default_text.count( const.UNICODE_REPLACEMENT_CHARACTER )
    
    return ( default_text, default_encoding, default_error_count )
    


def non_failing_unicode_decode( data, encoding ):
    
    text = None
    
    try:
        
        if encoding in ( 'ISO-8859-1', 'Windows-1252', None ):
            
            # ok, the site delivered one of these non-utf-8 'default' encodings. this is probably actually requests filling this in as default
            # we don't want to trust these because they are very permissive sets and'll usually decode garbage without errors
            # we want chardet to have a proper look
            
            raise LookupError()
            
        
        text = str( data, encoding )
        
    except ( UnicodeDecodeError, LookupError ) as e:
        
        try:
            
            if isinstance( e, UnicodeDecodeError ):
                
                text = str( data, encoding, errors = 'replace' )
                
            if text is None:
                
                try:
                    
                    ( default_text, default_encoding, default_error_count ) = default_decode( data )
                    
                    text = default_text
                    encoding = default_encoding
                    
                except:
                    
                    text = 'Could not decode the page--problem with given encoding "{}".'.format( encoding )
                    encoding = 'utf-8'
            
            if text is None:
                
                raise Exception()
                
            
        except Exception as e:
            
            text = 'Unfortunately, could not decode the page with given encoding "{}".'.format( encoding )
            encoding = 'utf-8'
            
        
    
    if const.NULL_CHARACTER in text:
        
        # I guess this is valid in unicode for some reason
        # funnily enough, it is not replaced by 'replace'
        # nor does it raise an error in normal str creation
        
        text = text.replace( const.NULL_CHARACTER, '' )
        
    
    return ( text, encoding )
    
