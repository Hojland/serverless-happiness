import json
from urllib.parse import unquote, parse_qs
import re
import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import slack_bodies

keyword_to_command = {'block_actions': 'star_response'}

def get_secret(client_session):
    secret_name = "slack_api_token"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    secrets_client = client_session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    resp = secrets_client.get_secret_value(SecretId=secret_name)
    secret = resp['SecretString']
    secret = json.loads(secret)
    return secret['SLACK_API_TOKEN']

class ResponseManager:
    def __init__(self, slack_event: dict):
        self.commands = []
        self.response_body = ""
        self.slack_event = self.jsonize_payload(slack_event)

    def jsonize_payload(self, slack_event: dict):
        return json.loads(unquote(slack_event['payload'][0]))

    def put_command_in_queue(self, command):
        if command == 'star_response':
            self.commands.append(StarResponseCommand(self.slack_event))

    def execute_top_command_in_queue(self):
        if len(self.commands) > 0:
            return self.commands.pop().execute()

class Command:
    """Command abstract class"""
    def __init__(self, slack_event: dict):
        self.invoker_id = slack_event['user']['id']
        self.invoker_name = slack_event['user']['name']
        self.actions = slack_event['actions']
        self.selected_option = slack_event['actions'][0]['selected_option']
        self.container = slack_event['container']
        self.response = ""
        self.arguments = []

    def extract_arguments(self):
        """To be overriden by the different child commands"""
        raise Exception('Not implemented exception')

    def execute(self):
        """To be overridden by the different child commands"""
        raise Exception('Not implemented exception')


class StarResponseCommand(Command):
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)
        self.stars = self.extract_stars()

    def extract_stars(self):
        stars = int(re.search("\d", self.selected_option['value'])[0])
        return stars

    def onestar_response(self, response_body: dict):
        mrkdwn = "I'm so sorry to hear that, what can we do to help? Ask your squadmembers to cheer you up"
        picture_url = "https://media.tenor.com/images/17889935cec2098aa6017c8808d53fb8/tenor.png"
        response = self.insert_text_and_picture(response_body, mrkdwn, picture_url)
        return response

    def twostar_response(self, response_body: dict):
        mrkdwn = "That's not too well. Cheer up, invite someone out for a cup of coffee :coffee:"
        picture_url = "https://bitesizebio.com/wp-content/uploads/2011/10/for-Bhoopalan-article.jpg"
        response = self.insert_text_and_picture(response_body, mrkdwn, picture_url)
        return response

    def threestar_response(self, response_body: dict):
        mrkdwn = "Okay. That's noted. Let's hope for an upward tendency here"
        picture_url = "https://www.weekendavisen.dk/media/cache/resolve/embedded_image/image/2/28614/23264008-saxo-photo.jpeg"
        response = self.insert_text_and_picture(response_body, mrkdwn, picture_url)
        return response

    def fourstar_response(self, response_body: dict):
        mrkdwn = "Okay, you maniac boxer, we love you :heart:"
        picture_url = "https://pbs.twimg.com/media/Ek9q1QhXEAUVBGD.jpg"
        response = self.insert_text_and_picture(response_body, mrkdwn, picture_url)
        return response

    def fivestar_response(self, response_body: dict):
        mrkdwn = "Yess, you absolute stud, I want to have your babies"
        picture_url = "https://images.daznservices.com/di/library/omnisport/f9/17/kasper-schmeichel-cropped_k6uuso12qk2l13qvibjk1amtv.jpg?t=529253702&quality=100"
        response = self.insert_text_and_picture(response_body, mrkdwn, picture_url)
        return response
    
    def insert_text_and_picture(self, response_body: dict, mrkdwn: str, picture_url: str):
        for block in response_body['blocks']:
            if block['type'] == "section":
                block['text'].update(text=mrkdwn)
            if block['type'] == "image":
                block.update(image_url=picture_url)
        return response_body

    def execute(self):
        """Execute happiness reaction"""
        if self.stars == 1:
            self.response = self.onestar_response(slack_bodies.response_body)
        elif self.stars == 2:
            self.response = self.twostar_response(slack_bodies.response_body)
        elif self.stars == 3: 
            self.response = self.threestar_response(slack_bodies.response_body)
        elif self.stars == 4: 
            self.response = self.fourstar_response(slack_bodies.response_body)
        elif self.stars == 5: 
            self.response = self.fivestar_response(slack_bodies.response_body)

        else:
            self.response = "Not Implemented"
        return self.response

def main(event, context):
    print(f"event: {event}")
    body = event['body']
    slack_event = parse_qs(body)

    aws_session = boto3.session.Session()
    SLACK_TOKEN = get_secret(aws_session)
    slack_client = WebClient(token=SLACK_TOKEN)
    # entry level message
    if not "payload" in slack_event.keys():
        user_id = slack_event["user_id"][0]
        print(f"user_id: {user_id}")
        channel = f"@{slack_event['user_name'][0]}"if slack_event['channel_name'][0] == 'directmessage' else slack_event['channel_id'][0]
        try:
            slack_client.chat_postMessage(blocks=json.dumps(slack_bodies.intro_body['blocks']), channel=channel)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
        return {"statusCode": 200}

    # star response
    else:
        resp_manager = ResponseManager(slack_event)
        command = keyword_to_command[resp_manager.slack_event['type']]
        resp_manager.put_command_in_queue(command)
        response = resp_manager.execute_top_command_in_queue()
        try:
            channel = resp_manager.slack_event['container']['channel_id']
            user = resp_manager.slack_event['user']['id']
            ts = resp_manager.slack_event['container']['message_ts']
            slack_client.chat_postEphemeral(blocks=json.dumps(response['blocks']), user=user, channel=channel, ts=ts)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
        return {"statusCode": 200}

    #body = {"response_type": "in_channel", "text": output, "delete_original": "true"}


# TODO
# make request for new app. Make the app.
# not ephemeral in first step, ephemeral in next
# use db to log stuff
# method to get result in time periods
# only football player moods (maybe only bendtner)
# responses should be public. So first message should be a vote or something. Not radio button

# chat update message - update initial with users_profile_get.
# users.profile.get
# chat:write
# commands