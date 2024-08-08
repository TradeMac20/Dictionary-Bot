# -*- coding: utf-8 -*-
import telebot
import config
import dc
import datetime
import pytz
import json
import traceback
import os
from dotenv import load_dotenv
import json
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
        "Welcome to the dictonary bot! \n" +
        "To search for the meaning of a word press /search \n" +
        "To add a word to the dictionary word press /add \n" +
        "To delete a word from the dictionary press /delete \n" +
        "To edit a word press /edit\n" +
        "If you need any help press /help \n"

    )

@bot.message_handler(commands=['help'])
def help_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           "Message the developer", url='telegram.me/sharon_enam'
       )
   )

   bot.send_message(
       message.chat.id,
       "1) To search for a word press /search \n" +
       "2) Reach if you have more concerns \n",
        reply_markup=keyboard
        
   )
##search command
@bot.message_handler(commands=['search'] ,content_types=['text'])
def search_command(message):
    bot.send_message(
        message.chat.id,
        "Type the word you want to search for!"
    )
    bot.register_next_step_handler(message, handle_search)

    
def handle_search(message):
    with open("dictionary.json") as json_file:
         word_dict = json.load(json_file)
    
    word_to_search = message.text.title()
  
        
        
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
            
        

            bot.send_message(message.chat.id, response)
           
                 
    else:
            print(word_to_search)
            bot.send_message(
                message.chat.id,
                "Word not found. Please try another word.\n " +
                "Press /add if you want to add a word to my dictionary \n")
      
    # if message.text.startswith("/") == False:
    #     bot.register_next_step_handler(message, handle_search)
    

            
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
        "Type the word you want to add!,Please provide word, meaning, parts of speech, synonyms, antonyms, and similar words separated by spaces"
    )   
    bot.register_next_step_handler(message, handle_add)    


def handle_add(message):
    try:
        word,meaning,parts_of_speech,synonym,antonym,similar_words = message.text.split(',')
        word = word.strip()
        # print(word)
    except ValueError:
        bot.send_message(
             message.chat.id,
             "Invalid format. Please provide word, meaning, parts of speech, synonyms, antonyms, and similar words separated by spaces."
        )
        bot.register_next_step_handler(message, handle_add)
        
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
        #  bot.register_next_step_handler(message, handle_add)

   
    #  if message.text.startswith("/") == False:
    #     bot.register_next_step_handler(message, handle_search)
    

         
## to delete word
@bot.message_handler(commands=['delete'], content_types=['text'])  
def delete_command(message):
    bot.send_message(
        message.chat.id,
        "Type the word you want to delete"
    )
    bot.register_next_step_handler(message,delete_button)

def delete_button(message):
    with open("dictionary.json") as json_file:
         word_dict = json.load(json_file)

    print(message.text)

    word_to_delete = message.text.title()
    # [8:]
    if word_to_delete in word_dict:
        word_dict.pop(word_to_delete)
        with open('dictionary.json', 'w') as file:
            json.dump(word_dict, file, indent=2)
        bot.send_message(
              message.chat.id, 
              f"{word_to_delete} deleted from the dictionary")
        # bot.register_next_step_handler(message, delete_command)
        
    else:
        bot.send_message(
              message.chat.id, 
              f"{word_to_delete} does not exist in dictionary")
        bot.register_next_step_handler(message, handle_search)

    # if message.text.startswith("/") == False:
    #     bot.register_next_step_handler(message, handle_search)
   
 


##edit bot
@bot.message_handler(commands=['edit'], content_types=['text'])     
def edit_command(message):
    bot.send_message(
        message.chat.id,
        "Enter the word you want to edit"

    )
    bot.register_next_step_handler(message, edit_dictionary)

def edit_dictionary(message):
    word_to_edit = message.text.title()

    with open("dictionary.json", "r") as json_file:
        word_dict = json.load(json_file)

    if word_to_edit not in word_dict:
        bot.send_message(message.chat.id, f"{word_to_edit} does not exist in the dictionary.")
        bot.register_next_step_handler(message,edit_dictionary)
    else:


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

    if field_choice not in ["1", "2", "3", "4", "5"]:
        bot.send_message(message.chat.id, "Invalid option. Please enter a number from 1 to 5.")
        return
    else:


        fields = ["Meaning", "Parts of Speech", "Synonym", "Antonym", "Similar words"]
        field_to_edit = fields[int(field_choice) - 1]

        bot.send_message(message.chat.id, f"Enter the new value for {field_to_edit}:")
        bot.register_next_step_handler(message, process_new_value, word_to_edit, field_to_edit, word_dict)


def process_new_value(message, word_to_edit, field_to_edit, word_dict):
    new_value = message.text.strip()

    word_dict[word_to_edit][field_to_edit] = new_value

    with open("dictionary.json", "w") as json_file:
        json.dump(word_dict, json_file, indent=2)

    bot.send_message(message.chat.id, f"{field_to_edit} for {word_to_edit} updated successfully.")
        







    
bot.polling(none_stop=True)
#print meaning of word and use an api for pronunciation and origin of the word