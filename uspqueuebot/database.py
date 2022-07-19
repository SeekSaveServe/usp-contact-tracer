import logging
import boto3
from datetime import datetime, timedelta

# time-zone
time_zone = "Singapore"

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

# Setting up client with AWS
client = boto3.resource("dynamodb", region_name='us-east-1')
TABLE_NAME = "USPContactTraceBotTable"
table = client.Table(TABLE_NAME)

def create_table():
    """
    Creates a DynamoDB table
    """

    try:
        client.create_table(
            TableName = TABLE_NAME,
            KeySchema = [
                {
                    "AttributeName": 'hashid',
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions = [
                {
                    "AttributeName": "hashid",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput = {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        logger.info("Table named " + TABLE_NAME + " was created in DynamoDB.")
    except:
        logger.info("Table named " + TABLE_NAME + " already exists in DynamoDB.")
    return

def get_table():
    """
    Retrieve all contents of the table

    Returns
    -------
    dic
        Response from scan requeston DynamoDB
    """
    try:
        response = table.scan()
        logger.info("All entries have been retrieved and returned.")
        return response
    except:
        create_table()
        response = get_table()
        return response    

def insert_user(hashid, chat_id, username, queue_number, room_no):
    """
    Insert a new entry into the table with timestamp
    """
    # utc + 8 = sg time
    timestamp = repr(datetime.utcnow() + timedelta(hours=8))
    logger.info(f"room_no: {room_no}, timestamp {timestamp}")
    table.update_item(
        Key = {"hashid": hashid},
        UpdateExpression = "SET {} = :val1, {} =:val2, {} =:val3, {} =:val4, {} =:val5, {} =:val6".format("chat_id", "username", "queue_number", "entry_time", "exit_time", "room_no"),
        ExpressionAttributeValues = {":val1": chat_id, ":val2": username, ":val3": queue_number, ":val4": timestamp, ":val5": False, ":val6":room_no}
        )
    logger.info("New entry successfully added into DynamoDB.")

def remove_user(hashid):
    """
    Adds exit time to an entry with hashid
    """
    # utc + 8 = sg time
    timestamp = repr(datetime.utcnow() + timedelta(hours=8))
    logger.info("Updating table")
    table.update_item(
        Key = {"hashid": hashid},
        UpdateExpression = "SET {} =:val5".format( "exit_time"),
        ExpressionAttributeValues = {":val5": timestamp}
        )
    logger.info("Exit time successfully updated into DynamoDB.")
# table.delete_item(Key = {'hashid' : '2ecf0e196e4154e9cb85f269a4a0c4fcd8466dc128a85450f27f820d7f8a4947'})