import json
import logging
import os
import time
import uuid
import requests
import boto3
from events.calendars import endpoints
from events import decimalencoder
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb')
webhook_url = os.environ['SLACK_WEBHOOK']
channel = os.environ.get('SLACK_CHANNEL', '#events-testing')

def check_events(event, context):
    """
    Run a cronjob to check all the Google Calenar API Links.
    """
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    timestamp = int(time.time())
    for (call_id, url) in endpoints:
        result = table.get_item(
            Key={
                'id': call_id,
            }
        )
        if 'Item' in result:
            logger.info("[%s] get_item %s", call_id, json.dumps(
                result, indent=4, cls=decimalencoder.DecimalEncoder))
            sync_token = result['Item']['syncToken']
            url_with_sync_token = "%s&syncToken=%s" % (url, sync_token)
            logger.info("[%s] Fetching with SyncToken %s",
                        call_id, url_with_sync_token)
            req = requests.get(url_with_sync_token)
            resp = req.json()
            logger.info("[%s] Request. Resp %s",
                        call_id, json.dumps(result, indent=4, cls=decimalencoder.DecimalEncoder))
            if 'error' in resp:
                logger.warn("[%s] api error %s", call_id, json.dumps(
                    resp, indent=4, cls=decimalencoder.DecimalEncoder))
                result = table.update_item(
                    Key={
                        'id': call_id,
                    },
                    ExpressionAttributeValues={
                        ':syncToken': None,
                        ':checkedAt': timestamp,
                    },
                    UpdateExpression='SET syncToken = :syncToken, '
                    'checkedAt = :checkedAt',
                    ReturnValues='ALL_NEW',
                )
                logger.info("[%s] Reset SyncToken")
                continue
            else:
                new_items = resp['items']
            logger.info("[%s] There are %d new events",
                        call_id, len(new_items))
            creator = resp['summary'].replace('Events - ', "")
            text_format = "*{creator} announced a new tech meetup*".format(
                creator=creator)
            for item in new_items:
                if item['status'] == 'confirmed':
                    link = item['description'].split().pop()
                    slack_payload = {
                        "text": text_format,
                        "channel": channel,
                        "username": "torontojs-events-bot",
                        "attachments": [
                            {
                                "fields": [
                                    {
                                        "title": "Location",
                                        "value": item.get('location', "I don't know"),
                                        "short": True
                                    },
                                    {
                                        "title": "Title",
                                        "value": item['summary'],
                                        "short": True
                                    },
                                    {
                                        "title": "Meetup Link",
                                        "value": link,
                                        "short": False
                                    },
                                ]
                            }
                        ]
                    }
                    requests.post(webhook_url, json=slack_payload)
                    logger.info("[%s] Slack POST. eventId %s",
                                call_id, item['id'])
            result = table.update_item(
                Key={
                    'id': call_id,
                },
                ExpressionAttributeValues={
                    ':syncToken': resp['nextSyncToken'],
                    ':checkedAt': timestamp,
                },
                UpdateExpression='SET syncToken = :syncToken, '
                'checkedAt = :checkedAt',
                ReturnValues='ALL_NEW',
            )
            logger.info("[%s] Updating with SyncToken %s",
                        call_id, resp['nextSyncToken'])
        else:
            req = requests.get(url)
            resp = req.json()
            logger.info("[%s] Request. Resp %s",
                        call_id, resp)
            item = {
                'id': call_id,
                'syncToken': resp['nextSyncToken'],
                'checkedAt': timestamp,
            }
            logger.info("[%s] Fetching first time. SyncToken is %s",
                        call_id, resp['nextSyncToken'])
            logger.info("[%s] There are %d new events",
                        call_id, len(resp['items']))
            table.put_item(Item=item)
