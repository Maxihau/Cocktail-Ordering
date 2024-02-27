from datetime import datetime
import discord
import requests

intents = discord.Intents.all()
client = discord.Client(intents=intents)
DISCORD_BOT_TOKEN = 'MTE4NDQzMzI3NzUzNzM2NjAzNg.Gf_dwn.RVRN64S767PjzcdnkWjLRSsHHqGfS8MxJ2u7U8'

# # For testing locally
REST_SERVICE_URL = 'http://localhost:8080/'

# REST_SERVICE_URL = 'https://lehre.bpm.in.tum.de/ports/5321/'


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


# Handles the order and sends it to the Ordering RS via HTTP POST
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):

        print(message.content)
        # Checks if there has been a cocktail ordered
        content = message.content.split(' ')

        if len(content) >= 1:
            try:
                expr, item = message.content.split(' ', 1)
            except Exception as e:
                print(f"Exception {e}")
                await message.channel.send(f"There was no item found in the message")
                await message.channel.send(f"The message has to be in the following format: '!<expression> <item1>, <item2>, ...'")
                return
            expr = expr[1:]
            # Adds a timestamp which is later needed for the service requests
            timestamp = datetime.now().time()
            timestamp_str = timestamp.strftime("%H:%M:%S")
            payload = {'expr': expr, 'item': item, 'userID': message.author.id, 'timestamp': timestamp_str}
            print(f"Payload: {payload}")
            try:
                response = requests.post(REST_SERVICE_URL, json=payload)
                print(f"Response code: {response.status_code}")

                # Feedback to the user
                if response.status_code == 200:
                    await message.channel.send(f"Your order has been placed at {timestamp_str}")
                else:
                    await message.channel.send(f"Failed to place the {expr}. Please try again.")

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                await message.channel.send("Failed to communicate with the service. Please try again later.")
    else:
        await message.channel.send(f"Failed to order. Please try again.")
        await message.channel.send(f"The message has to be in the following format: '!<expression> <item1>, <item2>, ...'")


if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
