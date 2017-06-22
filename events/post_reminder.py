import json
import logging
import os
import time
import uuid
import requests
from events.calendars import endpoints
from events import decimalencoder
import logging
import datetime
from dateutil import parser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
webhook_url = os.environ['SLACK_WEBHOOK']
channel = os.environ.get('SLACK_CHANNEL', '#events-testing')


def check_reminder(event, context):
    """
    Run a cronjob to check all the Google Calenar API Links.
    """
    for (call_id, url) in endpoints:
        req = requests.get(url)
        resp = req.json()
        new_items = resp['items']
        logger.info("[%s] There are %d new events", call_id, len(new_items))
        for item in new_items:
            if item['status'] == 'confirmed':
                event_time = parser.parse(item['start']['dateTime'], ignoretz=True)
                now_time = datetime.datetime.utcnow()
                diff_days = (event_time - now_time).days
                logger.info("[%s] Event:%s EventTime:%s NowTime:%s Diff:%s", \
                    call_id, item['id'], event_time, now_time, diff_days)
                if diff_days == 0:
                    creator = resp['summary'].replace('Events - ', "")
                    text_format = "*{title} hosted by {creator} is happening today*".format(
                        creator=creator, title=item['summary'])
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
                    logger.info("[%s] Slack Reminder. eventId %s", call_id, item['id'])
