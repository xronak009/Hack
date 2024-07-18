import telebot
import requests
from bs4 import BeautifulSoup
import os
import time

bot = telebot.TeleBot('7390224751:AAGsXfghYYvStUGFqoFIVYocKv9ii7s71gs')

# Replace with your actual API key
API_KEY = "AIzaSyCD3sWeDT3j5z0B0tphHifkDWD06io5nOE"
CUSTOM_SEARCH_ENGINE_ID = "a012d00b3fd6f436c"  # Replace with your custom search engine ID

# Owner user ID
OWNER_ID = 1192484969  # Replace with your actual user ID

# Database file
DATABASE_FILE = "database.txt"

# Anti-spam cooldown (seconds)
COOLDOWN = 15

# Dictionary to store user last command time
last_command_time = {}

# Check if database file exists, create it if not
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as f:
        pass

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Welcome to the Dork Bot! Use /register to register and then /dork [word] to search.")

@bot.message_handler(commands=['register'])
def register_command(message):
    user_id = message.from_user.id
    # Check if user already registered
    with open(DATABASE_FILE, "r") as f:
        registered_users = [line.strip() for line in f]
    if str(user_id) in registered_users:
        bot.reply_to(message, "You are already registered! ✅✨")
    else:
        # Register user
        with open(DATABASE_FILE, "a") as f:
            f.write(str(user_id) + "\n")
        bot.reply_to(message, "Registration successful! ✅")

@bot.message_handler(commands=['dork'])
def dork_command(message):
    user_id = message.from_user.id
    # Check if user is registered
    with open(DATABASE_FILE, "r") as f:
        registered_users = [line.strip() for line in f]
    if str(user_id) not in registered_users:
        bot.reply_to(message, "Please register first using /register..👾")
        return

    # Anti-spam check
    if user_id in last_command_time:
        if time.time() - last_command_time[user_id] < COOLDOWN and user_id != OWNER_ID:
            bot.reply_to(message, f"Please wait {COOLDOWN} seconds before using the /dork command again.")
            return

    try:
        args = message.text.split()
        if len(args) == 2:
            word = args[1]

            bot.reply_to(message, f"Wait, I'm searching for {word}. This may take a while....")

            # Define the number of results per page
            results_per_page = 10 # Increase this value to fetch more results per API call. 
            start = 0 
            sites = []

            while True:
                time.sleep(1) # Wait for 1 second before each API call

                url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CUSTOM_SEARCH_ENGINE_ID}&q={word}&start={start}&num={results_per_page}"
                response = requests.get(url)
                data = response.json()

                if 'items' in data:
                    sites.extend([item['link'] for item in data['items']])
                    start += results_per_page
                    if len(data['items']) < results_per_page:
                        break 
                else:
                    break  # Stop if there are no more results

            if len(sites) > 0:
                with open(f"{word}.txt", "w", encoding="utf-8") as file:
                    for site in sites:
                        file.write(site + "\n")
                bot.send_document(message.chat.id, open(f"{word}.txt", 'rb'),
                                  caption=f"Found {len(sites)} sites.\n\n owner - @xRonak ⛈️")
                os.remove(f"{word}.txt")
            else:
                bot.reply_to(message, "No sites found..🥲")

        else:
            bot.reply_to(message, "Incorrect format. Use /dork [word]")
    except ValueError:
        bot.reply_to(message, "Incorrect format. Use /dork [word]")

    # Update last command time for the user
    last_command_time[user_id] = time.time()

bot.polling()
