import colorama
from colorama import Fore, Back, Style
import argparse
import os
from search_for_similar_images import search as search_sim
from search_for_duplications import search as search_dup
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
import numpy as np
from PIL import Image
import timm
import requests
from io import BytesIO
from resnet18_similarity import compare_images

colorama.init(autoreset = True)

#settings:
thresh_hold = 80
move_images = True
performance = 'default'


parser = argparse.ArgumentParser()
parser.add_argument('--no_colors', dest='no_colors')
args = parser.parse_args()

show_theme = str(args.no_colors).lower() != "true"


#theme of the app
if show_theme:
    Bright = Style.BRIGHT+Fore.GREEN
    Normal = Style.NORMAL+Fore.GREEN
    Dark = Style.DIM+Fore.GREEN

    error_Bright = Style.BRIGHT+Fore.RED
    error_Normal = Style.NORMAL+Fore.RED
    error_Dark = Style.DIM+Fore.RED

    pro_tip_Dark = Style.DIM+Fore.YELLOW
    pro_tip_Normal = Style.NORMAL+Fore.YELLOW
else:
    Bright = ""
    Normal = ""
    Dark = ""
    
    error_Bright = ""
    error_Normal = ""
    error_Dark = ""

    pro_tip_Dark = ""
    pro_tip_Normal = ""



def print_logo():
    print("")
    print("\t"+"\t"+Dark+"||="+          "==========================================="+"|| ")
    print("\t"+"\t"+Dark+"||"+          "  _____                             _____  "+" || ")
    print("\t"+"\t"+Dark+"||"+          " |_   _|                           |  __ \ "+" || ")
    print("\t"+"\t"+Normal+"||"+        "   | |  _ __ ___   __ _  __ _  ___ | |__) |"+" || ")
    print("\t"+"\t"+Bright+"||"+        "   | | | '_ ` _ \ / _` |/ _` |/ _ \|  _  / "+" || ")
    print("\t"+"\t"+Bright+"||"+        "  _| |_| | | | | | (_| | (_| |  __/| | \ \ "+" || ")
    print("\t"+"\t"+Normal+"||"+        " |_____|_| |_| |_|\__,_|\__, |\___||_|  \_\\"+" || ")
    print("\t"+"\t"+Dark+"||"+          "                         __/ |             "+" || ")
    print("\t"+"\t"+Dark+"||"+          "                        |___/              "+" || ")
    print("\t"+"\t"+Dark+"||="+          "==========================================="+"|| ")  
    
def return_file_location(input_txt):
    while True:
        location = input(Normal+input_txt)
        if os.path.exists(location):
            return location
        print(error_Normal+"\tThe location you entered doesn't exist,\n\tPlease enter a valid location.")

def return_image_location(input_txt):
    while True:
        location = input(Normal+input_txt)
        if os.path.exists(location):
            if  location.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif','jfif','pjpeg','pjp','svg','avif','webp','apng')):
                return location
            else:
                print(error_Normal+"\tThe image extension you entered is not valid,\n\tor you didn't type the extension,\n\tPlease enter a valid image extension.")
        else:
            print(error_Normal+"\tThe image you entered doesn't exist,\n\tplease enter a path of an existing image")

def print_settings():
    clear_screen()
    print("")
    print(Dark+"||======================================================================||")
    print(Dark+"||"+"\t\t\t\t Settings:"+"\t\t\t\t||")
    print(Dark+"|| 1.Search Threshold: ",Bright+str(thresh_hold)+"%"+Dark+"\t\t\t\t\t\t||")
    print(Dark+"|| 2.Move Similar Images To a Folder Inside Searched Folder: ",Bright+str(move_images)+Dark+"\t||")
    print(Dark+"|| 3.Performance of Searching: ",Bright+str(performance)+Dark+"\t\t\t\t\t||")
    print(Dark+"||======================================================================||")
    print(pro_tip_Normal+"ProTip:",pro_tip_Dark+" type ",pro_tip_Normal+"restart",pro_tip_Dark+" to restart the tool.")
    print(Dark+"")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def greetings():
    clear_screen()
    if show_theme:
        print_logo()

    print("")
    print(Normal+"Welcome in omar's Image Search Engine ImageR,")
    print(Normal+"Where you can Search By Image And Filter duplications in datasets")
    print(pro_tip_Normal+"ProTip:"+pro_tip_Dark+" if you want to "+pro_tip_Normal+"exit"+pro_tip_Dark+" anywhere in the tool write "+pro_tip_Normal+"exit")
    print(pro_tip_Dark+"\tif you want to "+pro_tip_Normal+"Restart the tool"+pro_tip_Dark+" anywhere in the tool write "+pro_tip_Normal+"restart")
    print()

    print(Bright+"(Enter 1) "+Normal+"To search for a Similar Images for an image ")
    print(Bright+"(Enter 2) "+Normal+"To Filter Dataset from duplications\n")
    
def change_threshold():
    global thresh_hold
    while True:
        user_input = input(Normal+"Enter the Threshold value (0 to 100), or write return to return: "+Dark)
        if user_input=='return':
            return
        try:
            user_input = int(user_input)
            if user_input> 0 and user_input<100:
                thresh_hold = user_input
                return
            else:
                print(error_Normal+"\t the input is not valid, please enter a number between 0 to 100")
        except:
            print(error_Normal+"\t the input is not valid, please enter a number between 0 to 100")

def change_performance():
    global performance
    while True:
        print(end="")
        print(Bright+"(Enter 1) ",Dark+"To Choose Fast Performance and low accuracy")
        print(Bright+"(Enter 2) ",Dark+"To Choose Good Performance and Good accuracy")
        print(Bright+"(Enter 3) ",Dark+"To Choose Low Performance and Best accuracy")
        print(Bright+"(Enter return) ",Dark+"To return\n")

        user_input = input(Normal+"Enter your choice: "+Dark)
        if user_input=='return':
            return
        elif user_input=='1':
            performance = "fast"
            return

        elif user_input=='2':
            performance = "default"
            return

        elif user_input=='3':
            performance = "best"
            return

        else:
            print(error_Normal+"\tplease enter a valid input.")

def change_settings():
    global move_images
    while True:
        print("\n")
        print(Bright+"(Enter 1) ",Dark+"To Change the Threshold")
        if move_images:
            print(Bright+"(Enter 2) ",Dark+"To ",Bright+"Disable",Dark+" Moving images to a Folder inside the searched folder,")
            print(Dark+"\tthe tool will just print the names of similar images.")
        if not move_images:
            print(Bright+"(Enter 2) "+Dark+"To ",Bright+"Enable",Dark+" Moving images to a Folder inside the searched folder,")
            print(Dark+"\tthe tool will Move every group of similar images together in a Folder,\n\t every group will have different Folder.")
        print(Bright+"(Enter 3) ",Dark+"To Change the Performance")
        print(Bright+"(Enter return) ",Dark+"To return.\n")
        user_input = input(Normal+"Choose the number you want: "+Dark)

        if user_input == "1":
            change_threshold()
            return

        elif user_input == "2":
            if move_images:
                move_images=False
                return
            move_images = True
            return

        elif user_input == "3":
            change_performance()
            return

        elif user_input == "return":
            return
        
def return_image(folder_location):
    full_list=os.listdir(folder_location)
    for file in full_list:
        if file.lower().endswith(('.png', '.jpg', '.jpeg','webp')):
            return str(folder_location+file)
    return None

keep_application_working=True
while keep_application_working:
    greetings()
    # print(compare_images("scale_1200.png","scale_1200.png"))
    user_input = input(Normal+"Enter your Choice: "+Dark)

    #search for similar images
    if user_input == "1":
        thresh_hold=70
        print()
        print(pro_tip_Normal+"ProTip:"+pro_tip_Dark+" if the image path is too long,\n\tJust copy the image to the tool folder and write it's name only.")
        image_location=return_image_location("Enter the location of the Image you want to search for: \n"+Dark)
        folder_location=return_file_location("Enter the location of the Folder you want to search in: \n"+Dark)
        
        while True:
            print_settings()
            user_input = input(Normal+"Type (y) to Proceed with this Settings, Type (n) to change Settings:"+Dark)
            if user_input.lower()=="y":
                # compare_images(image_location,image_location)
                search_sim(
                    show_theme=show_theme,
                    image_location=image_location,
                    folder_location=folder_location,
                    thresh_hold=thresh_hold,
                    move_images=move_images,
                    performance=performance
                )


                break
            if user_input.lower()=="n":
                change_settings()

    #filter duplication
    elif user_input == "2":
        thresh_hold=90
        folder_location=return_file_location("Enter the location of the Folder you want to search in: \n"+Dark)
        
        while True:
            print_settings()
            user_input = input(Normal+"Type (y) to Proceed with this Settings, Type (n) to change Settings:"+Dark)
            if user_input.lower()=="y":
                # image = return_image(folder_location)
                # compare_images(image,image)
                search_dup(
                    show_theme=show_theme,
                    folder_location=folder_location,
                    thresh_hold=thresh_hold,
                    move_images=move_images,
                    performance=performance
                )
                break
            if user_input.lower()=="n":
                change_settings()

    else:
        print(Bright+"Good bye (:")
