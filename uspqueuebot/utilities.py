import hashlib
import logging
from uspqueuebot.constants import NUMBER_TO_BUMP
from uspqueuebot.database import get_table, remove_user
# for exporting data as csv file
import csv, io

def send_csv(bot, lst: "List[List[Any]]", fname: str, chat_id):
    """
    Returns data as a .csv file
    https://okhlopkov.medium.com/dont-save-a-file-on-disk-to-send-it-with-telegram-bot-d7cd591fec2d
    """
    # csv module can write data in io.StringIO buffer only
    s = io.StringIO()
    csv.writer(s).writerows(test_data)
    s.seek(0)

    # python-telegram-bot library can send files only from io.BytesIO buffer
    # we need to convert StringIO to BytesIO
    buf = io.BytesIO()

    # extract csv-string, convert it to bytes and write to buffer
    buf.write(s.getvalue().encode())
    buf.seek(0)

    # set a filename with file's extension
    buf.name = f'{fname}.csv'

    # send the buffer as a regular file
    bot.send_document(chat_id=update.message.chat_id, document=buf)

def get_message_type(body):
    """
    Determines the Telegram message type

    Parameters
    ----------
    body: dic
        Body of webhook event
    
    Returns
    -------
    string
        Description of message type
    """

    if "message" in body.keys():
        if "text" in body["message"]:
            return "text"
        elif "sticker" in body["message"]:
            return "sticker"
    
    if "edited_message" in body.keys():
        return "edited_message"
    
    return "others"

def decimal_to_int(decimal):
    """
    Converts a json decimal to an integer.
    Mostly used to convert chat_id
    """
    
    integer = int(str(decimal))
    return integer
    
def extract_user_details(body):
    """
    Obtains the chat ID from the event body

    Parameters
    ----------
    body: dic
        Body of webhook event
    
    Returns
    -------
    (int, str)
        Tuple containing chat ID and username of user
    """

    if "edited_message" in body.keys():
        chat_id = body["edited_message"]["chat"]["id"]
        username = body["edited_message"]["chat"]["username"]
    else:
        chat_id = body["message"]["chat"]["id"]
        username = body["message"]["chat"]["username"]

    chat_id = decimal_to_int(chat_id)
    return (chat_id, username)

def get_sha256_hash(plaintext):
    """
    Hashes an object using SHA256. Usually used to generate hash of chat ID for lookup
    Parameters
    ----------
    plaintext: int or str
        Item to hash
    
    Returns
    -------
    str
        Hash of the item
    """

    hasher = hashlib.sha256()
    string_to_hash = str(plaintext)
    hasher.update(string_to_hash.encode('utf-8'))
    hash = hasher.hexdigest()
    return hash

def get_queue(room_no, isAdmin=False):
    raw_table = get_table()
    queue = []
    # remove for deployment
    logging.error(repr(raw_table))
    if not isAdmin:
        for entry in raw_table["Items"]:
            if entry["room_no"] != room_no and room_no != "all":
                continue
            queue_number = decimal_to_int(entry["queue_number"])
            chat_id = decimal_to_int(entry["chat_id"])
            username = entry["username"]
            queue.append((queue_number, chat_id, username))
    else:
        for entry in raw_table["Items"]:
            if entry["room_no"] != room_no and room_no != "all":
                continue
            queue_number = decimal_to_int(entry["queue_number"])
            chat_id = decimal_to_int(entry["chat_id"])
            username = entry["username"]
            entry_time = entry["entry_time"]
            exit_time = exit_timr["exit_time"]
            queue.append((queue_number, chat_id, username, entry_time, exit_time, room_no))
    queue.sort()
    return queue

def get_next_queue_number(queue):
    queue_number = 0
    if len(queue) != 0:
        queue_number = queue[-1][0] + 1
    return queue_number
    
def is_in_queue(queue, chat_id):
    for entry in queue:
        # if the user has entered room and has not exited
        if entry[1] == chat_id and not entry["exit_time"]:
            return True
    return False

def get_position(chat_id, queue):
    ## position is equivalent to number of people ahead of user
    position = 0
    found = False
    for entry in queue:
        if entry[1] == chat_id:
            found = True
            break
        position += 1
    
    if not found:
        position = "Not in queue"
    return str(position)

def get_next_queue(queue):
    to_delete = queue[0][1]
    hashid = get_sha256_hash(to_delete)
    remove_user(hashid)
    return queue[1:]

def get_first_chat_id(queue):
    if len(queue) == 0:
        return "None"
    return queue[0][1]

def get_first_username(queue):
    if len(queue) == 0:
        return "None"
    return queue[0][2]

def get_bump_queue(queue):
    bump_queue = queue[1:NUMBER_TO_BUMP + 1]
    bump_queue.append(queue[0])
    bump_queue = [(new_index, curr_tuple[1], curr_tuple[2]) for new_index, curr_tuple in enumerate(bump_queue)]
    return bump_queue
