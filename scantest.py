# -*- coding: utf-8 -*-
import telebot
import config
import dc
import datetime
import pytz
import json
import traceback
import os
from images import extract
from dotenv import load_dotenv
import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from queue import Queue
import requests
import easyocr


load_dotenv()
token = os.environ['TOKEN']
D_timezone = pytz.timezone(config.timezone)
D_common_name = config.timezone_commonname
bot = telebot.TeleBot(token)

##start command
@bot.message_handler(commands=['start'])


def startcommand(message):
    bot.send_message(
        message.chat.id,
        "📚 Welcome to the Dictionary Bot! 📖\n\n" +
        "To search for the meaning of a word, press /search 🔍\n" +
        "To add a word to the dictionary, press /add ➕\n" +
        "To delete a word from the dictionary, press /delete ❌\n" +
        "To edit a word, press /edit ✏️\n" +
        "To scan a word, click /scan 📸\n" +
        "If you need any help, press /help ℹ️\n"
    )
    bot.register_next_step_handler(message, is_valid_start_command)
    # is_valid_command(message)


@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           "Message the developer 👩‍💻", url='telegram.me/sharon_enam'
       )
   )

   bot.send_message(
       message.chat.id,
       "🆘 Need Help? Here's what you can do:\n" +
       "1) To search for a word, press /search 🔍\n" +
       "2) For more assistance, feel free to reach out to the developer 👩‍💻.\n",
        reply_markup=keyboard
        
   )

##function to check validity of input
def is_valid_command(message):
    valid_commands = {
        '/start': startcommand,
        '/search': search_command,
        '/add': add_command,
        '/delete': delete_command,
        '/edit': edit_command,
        '/help': help_command,
        '/scan' : scan_command
    }
    lowered_input = message.text.lower() 

    if lowered_input.startswith('/') and len(lowered_input) > 1:
        for cmd, cmd_func in valid_commands.items():
            if lowered_input.startswith(cmd):
                cmd_func(message)
                return True  # Exit the function after calling the command function
    elif lowered_input.startswith("/") :
        bot.send_message(
        message.chat.id,
         "Ooops that's not a valid command! \nYou would have to presss /start again😀")
        # bot.register_next_step_handler(message,is_valid_command)

##search command
@bot.message_handler(commands=['search'] ,content_types=['text'])
def search_command(message):
    bot.send_message(
        message.chat.id,
        "🔍 Type the word you want to search for! 📚")
    
    bot.register_next_step_handler(message, handle_search)

    
def handle_search(message):
    if message.text == None:
        bot.reply_to(message, "⚠️ You didn't type text.\n Please click /search and type a word to find it's meaning")
        # bot.register_next_step_handler(, image_handler)
        return
    # print(message.text)
        
    with open("dictionary.json") as json_file:
         word_dict = json.load(json_file)
    
    word_to_search = message.text.title() 
    # print(word_to_search)
    if is_valid_command(message):
        return
        
        
    if word_to_search in word_dict:
            results = word_dict[word_to_search]
            meaning = results['Meaning']
            synonym = results['Synonyms']
            antonym = results['Antonyms']
            parts_of_speech = results['Parts of Speech']
            similar_words = results['Similar words']

            response = (
                f"Meaning: {meaning}\n"
                f"Parts of Speech: {parts_of_speech}\n"
                f"Synonyms: {synonym}\n"
                f"Antonyms: {antonym}\n"
                f"Similar words: {similar_words}"
                
            )

            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                "Click here for pronunciation", url=f'https://www.google.com/search?q={word_to_search}+pronunciation&oq={word_to_search}+pronunciation'
       )
   )
           
        

            bot.send_message(message.chat.id if message.chat.id else None, response,reply_markup=keyboard)
            
            bot.register_next_step_handler(message, handle_search)
           
                 
    else:
            
            bot.send_message(
                message.chat.id if message.chat.id else None,
                "❌ Word not found. Please try another word.\n " +
                "Press /add if you want to add a word to my dictionary \n")
      
            bot.register_next_step_handler(message, handle_search)
    
def is_valid_start_command(message):
    valid_commands = {
        '/start': startcommand,
        '/search': search_command,
        '/add': add_command,
        '/delete': delete_command,
        '/edit': edit_command,
        '/help': help_command,
        '/scan' : scan_command
    }
    lowered_input = message.text.lower() 

    if lowered_input.startswith('/') and len(lowered_input) > 1:
        for cmd, cmd_func in valid_commands.items():
            if lowered_input.startswith(cmd):
                cmd_func(message)
                return True  # Exit the function after calling the command function
    else:
        bot.send_message(
        message.chat.id,
         "Ooops that's not a valid command! \nYou would have to presss /start again😀")
        # bot.register_next_step_handler(message,is_valid_command)
            
##function to add a word
def write_json(newword, filename="dictionary.json"):
    try:
        with open(filename, 'r+') as json_file:
            # Load existing data or initialize an empty dictionary
            try:
                word_dict = json.load(json_file)
            except json.JSONDecodeError:
                word_dict = {}

            # Update with new word
            word_dict.update(newword)

            # Move file position to the beginning
            json_file.seek(0)

            # Write updated dictionary back to the file
            json.dump(word_dict, json_file, indent=4)
            json_file.truncate()  # Truncate to remove any remaining content if the new data is shorter
    except FileNotFoundError:
        # Handle file not found error
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")



          
@bot.message_handler(commands=['add'],content_types=['text']) 
def add_command(message):
    
    
    bot.send_message(
        message.chat.id,
        "✏️ Type the word you want to add!,Please provide word, meaning, parts of speech, synonyms, antonyms, and similar words separated by spaces"
    )   
    bot.register_next_step_handler(message, handle_add)    


def handle_add(message):
    if message.text == None:
        bot.reply_to(message,"Oops! It seems like you didn't provide any text. 🤔 Please click on /add and type the word you want to add to the dictionary.")
        # bot.register_next_step_handler(, image_handler)
        return
    global word
    if is_valid_command(message):
            return 
   
    
    try:
        word,meaning,parts_of_speech,synonym,antonym,similar_words = message.text.split(',', maxsplit=5)
        word = word.strip()
        
        # print(word)
    except ValueError:
        bot.send_message(
             message.chat.id,
            "Uh-oh! It seems like you provided an invalid format. 😕 Please make sure to provide the word, meaning, parts of speech, synonyms, antonyms, and similar words separated by spaces."

        )
        
        bot.register_next_step_handler(message, handle_add)
        return

    
    
    with open("dictionary.json") as json_file:
        word_dict = json.load(json_file)
        # print(word_dict)
    # print(word.title())
    if word.title() in word_dict:
        bot.send_message(
              message.chat.id,
              f"{word} already exits in the dictionary!"
         )
        bot.register_next_step_handler(message, handle_add)
    else:
         
         newword = {word.title():{
            "Meaning": meaning,
            "Parts of Speech": parts_of_speech,
            "Synonyms": synonym,
            "Antonyms": antonym,
            "Similar words": similar_words
           
         }}
         write_json(newword)
         bot.send_message(
              message.chat.id, 
              f"{word} added to the dictionary.")
         bot.register_next_step_handler(message, handle_add)

   
         
## to delete word
@bot.message_handler(commands=['delete'], content_types=['text'])  
def delete_command(message):
    bot.send_message(
        message.chat.id,
        "🗑️ Sure! Just type the word you want to delete from the dictionary."

    )
    bot.register_next_step_handler(message,delete_button)

def delete_button(message):
    if message.text == None:
        bot.reply_to(message, "You didn't type text.\n Please click /delete and type a word to delete it")
        # bot.register_next_step_handler(, image_handler)
        return
    if is_valid_command(message):
        return
    with open("dictionary.json") as json_file:
         word_dict = json.load(json_file)


    word_to_delete = message.text.title()
    # [8:]
    if word_to_delete in word_dict:
        word_dict.pop(word_to_delete)
        with open('dictionary.json', 'w') as file:
            json.dump(word_dict, file, indent=2)
        bot.send_message(
              message.chat.id, 
              f"{word_to_delete} has been successfully deleted from the dictionary ✅ .")
        bot.register_next_step_handler(message, delete_button)
        return
        
    else:
        bot.send_message(
              message.chat.id, 
              f"{word_to_delete} does not exist in dictionary ❌ ")
        bot.register_next_step_handler(message, delete_button)
        return

   
@bot.message_handler(commands=['edit'], content_types=['text'])     
def edit_command(message):
    bot.send_message(
        message.chat.id,
        "📝 Enter the word you want to edit "

    )
    bot.register_next_step_handler(message, edit_dictionary)

def edit_dictionary(message):
    if message.text == None:
        bot.reply_to(message, "⚠️ You didn't type text.\n Please click /editt and type a word to edit it")
        # bot.register_next_step_handler(, image_handler)
        return
    word_to_edit = message.text.title()

    if is_valid_command(message):
        return

    with open("dictionary.json", "r") as json_file:
        word_dict = json.load(json_file)

    if word_to_edit not in word_dict:
        bot.send_message(message.chat.id, f"{word_to_edit} does not exist in the dictionary ❌")
        bot.register_next_step_handler(message,edit_dictionary)
    else:
        if is_valid_command(message):
            return


        bot.send_message(message.chat.id, f"Editing {word_to_edit}:")
        bot.send_message(message.chat.id, "Options:")
        bot.send_message(message.chat.id, "1. Meaning")
        bot.send_message(message.chat.id, "2. Parts of Speech")
        bot.send_message(message.chat.id, "3. Synonym")
        bot.send_message(message.chat.id, "4. Antonym")
        bot.send_message(message.chat.id, "5. Similar words")

        bot.register_next_step_handler(message, process_field_choice, word_to_edit, word_dict)


def process_field_choice(message, word_to_edit, word_dict):
    field_choice = message.text.strip()

    if is_valid_command(message):
        return

    if field_choice not in ["1", "2", "3", "4", "5"]:
        bot.send_message(message.chat.id, "Invalid option. Please enter a number from 1 to 5 ⚠️")
        bot.register_next_step_handler(message, process_field_choice, word_to_edit, word_dict)
        
        return
    else:
       


        fields = ["Meaning", "Parts of Speech", "Synonym", "Antonym", "Similar words"]
        field_to_edit = fields[int(field_choice) - 1]

        bot.send_message(message.chat.id, f"Enter the new value for {field_to_edit}:")
        bot.register_next_step_handler(message, process_new_value, word_to_edit, field_to_edit, word_dict)


def process_new_value(message, word_to_edit, field_to_edit, word_dict):
    new_value = message.text.strip()
    if is_valid_command(message):
            return
    word_dict[word_to_edit][field_to_edit] = new_value

    with open("dictionary.json", "w") as json_file:
        json.dump(word_dict, json_file, indent=2)

    bot.send_message(message.chat.id, f"{field_to_edit} for {word_to_edit} updated successfully 🥳.")
    bot.register_next_step_handler(message,edit_dictionary)
        
##image search
    
def handle_image_search(word_to_search, chat_id=None):
    with open("dictionary.json") as json_file:
        word_dict = json.load(json_file)

    word_to_search = word_to_search.title()
    # print(word_to_search)

    if word_to_search in word_dict:
        results = word_dict[word_to_search]
        meaning = results['Meaning']
        synonym = results['Synonyms']
        antonym = results['Antonyms']
        parts_of_speech = results['Parts of Speech']
        similar_words = results['Similar words']

        response = (
            f"Meaning: {meaning}\n"
            f"Parts of Speech: {parts_of_speech}\n"
            f"Synonyms: {synonym}\n"
            f"Antonyms: {antonym}\n"
            f"Similar words: {similar_words}"
        )

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                "Click here for pronunciation", url=f'https://www.google.com/search?q={word_to_search}+pronunciation&oq={word_to_search}+pronunciation'
            )
        )

        bot.send_message(chat_id, response, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, f"Word '{word_to_search}' not found in the dictionary 😵.")




@bot.message_handler(commands=['scan'], content_types=['text'])     
def scan_command(message):
    bot.send_message(
        message.chat.id,
        "😮‍💨📷 Scan the word"

    )
    bot.register_next_step_handler(message, image_handler)

def image_handler(update):
    # print(update.photo[-1] == False)
    if update.text: 

        if is_valid_command(update):
            return
        else:
            bot.reply_to(update, "🚫 You typed a text instead of uploading a photo, please click /scan to upload a photo")
        # bot.register_next_step_handler(, image_handler)
            return

    else:
        file_id = update.photo[-1].file_id  # Using the last sent photo
        file_info = bot.get_file(file_id)
        
        # Get the direct download link for the file
        download_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        # Download the file
        response = requests.get(download_url)


    
    if response.status_code == 200:
        # File downloaded successfully
        file_path = 'images/downloaded_image.jpg'  # Path to save the downloaded file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        # Process the image or do whatever you want with the file_path
        # For now, let's just reply with "Image received"
        bot.reply_to(update, "Image received")
        
        try:
            # Process the image here
            reader = easyocr.Reader(['en'])
            result = reader.readtext('images/downloaded_image.jpg', detail = 0)
            # print(result[0])
            # handle_image_search(result[0])
            # print(update.message.chat.id)
            # print(update.chat.id)
            if result:
                handle_image_search(result[0] if result[0] else "", update.chat.id)
                
            else:
                update.message.reply_text("No text recognized in the image.")
            bot.register_next_step_handler(update, image_handler)
        except Exception as e:
            bot.reply_to(update, f"An error occurred while processing the image: {str(e)}")
    else:
        bot.reply_to(update, "No text recognized in the image 🚫")
        bot.register_next_step_handler(update, image_handler)

# Assuming you have registered the image_handler with the bot
# bot.add_message_handler(image_handler)

# # Start the bot
# bot.polling(none_stop=True)


bot.polling(none_stop=True)
#print meaning of word and use an api for pronunciation and origin of the word