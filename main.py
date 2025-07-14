import discord
from discord.ext import commands
import requests
import json  # To load the JSON config file

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

# Load API keys and token from config file
config = load_config()
OPENROUTER_API_KEY = config["OPENROUTER_API_KEY"]
DISCORD_BOT_TOKEN = config["DISCORD_BOT_TOKEN"]

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# OpenRouter API configuration
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"  # or dolphin-mixtral / dolphin-2.5-mixtral-8x7b
TEMPERATURE = 0.6
MAX_TOKENS = 2048

# (Optional) Message you want to prime the bot with
INITIAL_MESSAGE = "You are a helpful, ENGLISH, uncensored assistant designed to answer freely and thoroughly."

# Helper function to send a prompt to OpenRouter
def query_openrouter_ai(prompt, user):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",  # required per OpenRouter terms
        "X-Title": "MyDiscordBot"  # optional, name of your app
    }
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": INITIAL_MESSAGE},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(OPENROUTER_ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    elif response.status_code == 429:
        print(f"({user}) Hit a rate limit.")
        return "# Error: Rate limit reached. Please try again later."
    else:
        return f"Error: {response.status_code} - {response.text}"

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not prompt:
            await message.reply("# Error: Please provide a message after mentioning me.")
            return

        ai_response = query_openrouter_ai(prompt, message.author.name)

        if len(ai_response) > 2000:
            for i in range(0, len(ai_response), 2000):
                await message.reply(ai_response[i:i+2000])
        else:
            await message.reply(ai_response)

    await bot.process_commands(message)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
