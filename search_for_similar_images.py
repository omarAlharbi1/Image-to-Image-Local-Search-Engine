import shutil
from colorama import Fore, Back, Style
import colorama
import os
from resnet18_similarity import compare_images
import multiprocessing
import threading
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_this_file_an_image(file_location):
    return file_location.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif','jfif','pjpeg','pjp','svg','avif','webp','apng'))

def return_list_of_images_in_folder(list_of_files):
    for i in list_of_files:
        print(i)


def search(show_theme,image_location,folder_location,thresh_hold,move_images,performance):
    clear_screen()
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
    list_of_images_to_search = os.listdir(folder_location)
    

    queue = multiprocessing.Queue()

    similar_images=[]
    
    def search_of_similar_images(list_of_images_to_search):
        first_run=True
        for i ,(image) in enumerate(list_of_images_to_search):

            if not is_this_file_an_image(image):
                continue
            # print(i)
            img = folder_location+image
            similarity = compare_images(img,image_location)
            if first_run:
                clear_screen()
                first_run=False
            if similarity>=thresh_hold/100.0:
                if img !=image_location:
                    print(Dark+'image ',Bright+image,Dark+'has a similarity:',Bright+f"{similarity*100:.2f}%")
                similar_images.append(image)
        # Store output of the process to the queue
        queue.put(similar_images)
        

    def move_file_to_folder(file_path, destination_folder):
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"The file {file_path} does not exist.")
            return

        # Check if the destination folder exists, create it if not
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Create the full destination path
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))

        # Move the file to the destination folder
        shutil.move(file_path, destination_path)

        print(f"File {file_path} moved to {destination_folder}.")

    def move_images():
        for image in similar_images:
            image_location=folder_location+image
            distination=folder_location+"similar2"
            move_file_to_folder(image_location,distination)

    len_of_list = len(list_of_images_to_search)
    print(len_of_list)
    chunck_size = int(len_of_list/6)
    rest_elemnts = len_of_list%6

    list_1 = list_of_images_to_search[0:chunck_size]
    list_2 = list_of_images_to_search[chunck_size:chunck_size*2]
    list_3 = list_of_images_to_search[chunck_size*2:chunck_size*3]
    list_4 = list_of_images_to_search[chunck_size*3:chunck_size*4]
    list_5 = list_of_images_to_search[chunck_size*4:chunck_size*5]
    list_6 = list_of_images_to_search[chunck_size*5:chunck_size*6+rest_elemnts]


    time1=time.time()
    processes = []
    list_of_lists=[list_1,list_2,list_3,list_4,list_5,list_6]
    for i in range(6):
        process = multiprocessing.Process(target=lambda: search_of_similar_images(list_of_lists[i]))
        processes.append(process)
        process.start()
    
    # Wait for all processes to finish before proceeding
    for process in processes:
        process.join()

    # Retrieve output from the queue
    for i in range(6):
        list_of_similar_images = queue.get()
        for image in list_of_similar_images:
            similar_images.append(image)
    print(Dark+"==================================================================")
    print(Dark+"Similar Pictures found:",Bright+str(len(similar_images)-1))
    print(Dark+"whole process toke:"+Bright+f"{(time.time()-time1):0.4f}"+Dark+" Seconds")
    print(Dark+"do you want to move all images to a folder in \n"+folder_location+"\n")
    print(Bright+"(y) for yes, (n) for no: ",end="")
    user_input=input(Dark)
    if user_input=="y":
        print("hi")
        move_images()
    print(user_input)
    print(user_input=="y")
    user_input=input(Dark)
