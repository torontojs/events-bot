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

def check_ahead(event, context):
    """
    Run a cronjob to check all the Google Calenar API Links.
    """
    week_ahead = []
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
                if (diff_days >= 0) and (diff_days < 8):
                    time_str = (event_time - datetime.timedelta(hours=4))\
                    .strftime("%A, %B %-d at %-I:%M%p")
                    creator = resp['summary'].replace('Events - ', "")
                    title = "{title} by {creator}".format(
                        creator=creator, title=item['summary'])
                    link = item['description'].split().pop()
                    week_ahead.append({
                        'title': title,
                        'link': link,
                        'footer': time_str
                    })
    slack_payload = {
        "text": "*Here are the meetups this week*",
        "channel": channel,
        "username": "torontojs-events-bot",
        "attachments": [
            {
                "fields": [
                    {
                        "title": event['title'],
                        "value": event['link'],
                        "short": False
                    }
                ],
                "footer": event['footer'],
            } for event in week_ahead
        ]
    }
    requests.post(webhook_url, json=slack_payload)
    logger.info("[%s] Slack Post Week Ahead.")

