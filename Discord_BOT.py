import discord
import requests

intents = discord.Intents.all()
client = discord.Client(intents=intents)
DISCORD_BOT_TOKEN = 'MTE4NDQzMzI3NzUzNzM2NjAzNg.Gf_dwn.RVRN64S767PjzcdnkWjLRSsHHqGfS8MxJ2u7U8'

# For testing locally
# REST_SERVICE_URL = 'http://localhost:8080/'

REST_SERVICE_URL = 'https://lehre.bpm.in.tum.de/ports/5321/'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


# Handles the order and sends it to the Ordering RS via HTTP POST
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!order'):
        print(message.content)
        # Checks if there has been a cocktail ordered
        content = message.content.split(' ')

        if len(content) >= 1:
            _, cocktail = message.content.split(' ', 1)
            payload = {'cocktail': cocktail, 'userID': message.author.id}
            print(f"Payload: {payload}")
            try:
                response = requests.post(REST_SERVICE_URL, json=payload)
                print(f"Response code: {response.status_code}")

                # Feedback to the user
                if response.status_code == 200:
                    await message.channel.send(f"Your order has been placed: {cocktail}")
                else:
                    await message.channel.send("Failed to place the order. Please try again.")

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                await message.channel.send("Failed to communicate with the service. Please try again later.")


if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
