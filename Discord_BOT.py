import discord
import requests


intents = discord.Intents.all()
client = discord.Client(intents=intents)

REST_SERVICE_URL = 'http://localhost:8080/'  # Replace with your Bottle REST service URL
#REST_SERVICE_URL = 'https://lehre.bpm.in.tum.de/ports/5321/'
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!order'):
        print(message.content)
        content = message.content.split(' ')
        if len(content) >= 1:
            cocktail_name = content[1]

            # Sending a POST request to your Bottle REST service
            payload = {'cocktailName': cocktail_name, 'userID': client.user.id}
            print(payload)
            try:
                response = requests.post(REST_SERVICE_URL, json=payload)
                print(response.status_code)
                if response.status_code == 200:
                    await message.channel.send(f"Order placed for {cocktail_name} by user {client.user.id}")
                else:
                    await message.channel.send("Failed to place the order. Please try again.")
            except requests.exceptions.RequestException as e:
                await message.channel.send("Failed to communicate with the service. Please try again later.")

if __name__ == "__main__":
    # Run your Discord bot
    client.run("MTE4NDQzMzI3NzUzNzM2NjAzNg.Gf_dwn.RVRN64S767PjzcdnkWjLRSsHHqGfS8MxJ2u7U8")
