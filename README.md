# TorontoJS Events Slack Bot
Slack Bot that posts events to slack from the Calendar feeds

Built with AWS Lambda and Python using [serverless ⚡️](https://serverless.com/framework/docs/) 

# Modes of operation
Function | Operation
------------ | -------------
cron | Checks the calendar feeds every 3 hours and looks for newly announced events
weekly | Every Monday at 10am posts the upcoming meetups in the week
reminder | Every day at 10am posts the meetups happening that day

