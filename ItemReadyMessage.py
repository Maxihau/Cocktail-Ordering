import requests
from bottle import Bottle, request
app = Bottle()

DISCORD_BOT_TOKEN = 'MTE4NDQzMzI3NzUzNzM2NjAzNg.Gf_dwn.RVRN64S767PjzcdnkWjLRSsHHqGfS8MxJ2u7U8'


@app.post('/')
def send_discord_message():
    try:
        # Get data from the POST request
        # Retrieve all form data from the POST request
        form_data = request.forms

        # Convert the form data to a dictionary for easy processing (optional)
        form_data_dict = dict(form_data)

        # Extract user ID and item from the data
        user_id = int(form_data_dict['user_id'])
        item = form_data_dict['item']
        print(f"UserID: {user_id}, item: {item}")

        message = f"Your item {item} is now ready to be picked up!"

        channel_id = create_dm_channel(DISCORD_BOT_TOKEN, user_id)
        send_message(DISCORD_BOT_TOKEN, channel_id, message)
    except Exception as e:
        return {'success': False, 'message': f"An error occurred: {e}"}


def create_dm_channel(token, user_id):
    data = {"recipient_id": user_id}
    headers = {"authorization": f'Bot {token}'}
    r = requests.post(f'https://discord.com/api/v9/users/@me/channels', json=data, headers=headers)
    print(f"Create DM channel status: {r.status_code}")
    channel_id = r.json()['id']
    return channel_id


def send_message(token, channel_id, message):
    url = 'https://discord.com/api/v8/channels/{}/messages'.format(channel_id)
    data = {"content": message}
    header = {"authorization": f'Bot {token}'}
    r = requests.post(url, data=data, headers=header)
    print(f"Send message status: {r.status_code}")


if __name__ == '__main__':
    # Local test
    # app.run(host='localhost', port=8081, debug=True)

    app.run(host="::", port=5001)
