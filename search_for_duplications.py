import shutil
from colorama import Fore, Back, Style
import colorama
import os
from resnet18_similarity import compare_images
import multiprocessing
import threading
import time

# /home/omar/Pictures/Scraping/testing/

def clear_screen():
    pass

def is_this_file_an_image(file_location):
    return file_location.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif','jfif','pjpeg','pjp','svg','avif','webp','apng'))

def return_list_of_images_in_folder(list_of_files):
    for i in list_of_files:
        print(i)

def return_file_name(location):
    for i in range(len(os.listdir(location))):
        new_location = location + "similar "+str(i)
        if not os.path.exists(new_location):
            return new_location

def search(show_theme,folder_location,thresh_hold,move_images,performance):
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

    def return_list_of_images(folder_location):
        full_list=os.listdir(folder_location)
        filtered_list = []
        for file in full_list:
            if is_this_file_an_image(file):
                filtered_list.append(file)
        return filtered_list


    def search_of_similar_images(process_num,original_image,list_of_images_to_search,already_scanned):
        # print("entered search_of_similar_images function!!!!")
        similar_images=[]
        first_run=True
        for i ,(image) in enumerate(list_of_images_to_search):
            if not is_this_file_an_image(image) or not is_this_file_an_image(original_image) or image in already_scanned:
                continue
            
            
            image_location = folder_location+image
            original_image_location = folder_location+original_image
            try:
                similarity = compare_images(original_image_location,image_location)
            except Exception as e:
                print(error_Normal+str(e))
                print(error_Normal+"\nError, couldn't process one of these images because one of them is not supported:")
                print(error_Bright+image)
                print(error_Bright+original_image)
                print(error_Normal+"Please change there extensions or fix them\n")
                continue
            if first_run:
                clear_screen()
                first_run=False
            if similarity>=thresh_hold/100.0:
                
                if image_location !=original_image_location:
                    print(Bright+str(i)+" "+original_image,Dark+"Match",Bright+image,Bright+f"{similarity*100:.2f}%")
                    # print(Dark+'image ',Bright+image,Dark+'has a similarity:',Bright+f"{similarity*100:.2f}%",Dark+"with",Bright+original_image)
                similar_images.append(image)
            else:
                print(Dark+"Process: "+str(process_num)+" image: "+str(i)+"/"+str(len(list_of_images_to_search)))
        # Store output of the process to the queue
        queue.put(similar_images)
        # return similar_images
        
    def move_file_to_folder(file_path, destination_folder):
        # Check if the file exists
        if not os.path.exists(file_path):
            print(error_Normal+f"The file {file_path} does not exist.")
            return

        # Check if the destination folder exists, create it if not
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Create the full destination path
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))

        # Move the file to the destination folder
        shutil.move(file_path, destination_path)

        # print(f"File {file_path} moved to {destination_folder}.")

    def move_images(similar_images):
        distination=return_file_name(folder_location)
        os.makedirs(distination)
        for image in similar_images:
            image_location=folder_location+image
            print(Bright+image,Normal+" is Moved to ",Bright+distination)
            move_file_to_folder(image_location,distination)

    def search_for_dup(list_of_images):
        similar_images_list = []

        while True:
            for i in range(len(list_of_images)):
                image = list_of_images[i]

                #get group of similar images names
                similar_images_list = search_of_similar_images(image,list_of_images)

                #if the list is not empty, move similar images together in a single folder,
                # also get out of loop so we can rearrange the list
                if len(similar_images_list) > 1:
                    print("============================================")
                    print("there is duplication!!")
                    print(len(similar_images_list))
                    print(similar_images_list)
                    print("============================================")
                    move_images(similar_images_list)
                    break
                
                #if we pass the whole folder and we didn't find similarities, return
                if i == len(list_of_images)-1:
                    return

            for image in similar_images_list:
                if image in list_of_images:
                    list_of_images.remove(image)
                    
    def split_list(chuncks,original_list):

        len_of_list = len(original_list)
        chunck_size = int(len_of_list/chuncks)
        rest_elemnts = len_of_list%chuncks
        lists=[]

        for i in range(chuncks):
            start = i*chunck_size
            if i == chuncks-1:
                end = (i+1)*chunck_size+rest_elemnts
            else:
                end = (i+1)*chunck_size

            lists.append(original_list[start : end])
        return lists
    
    time1=time.time()
    keep_running=True
    num_of_processes=int(os.cpu_count()/2)
    # num_of_processes=2
    counter = 0
    already_scanned=[]
    while keep_running:
        
        list_of_images_to_search = return_list_of_images(folder_location)
        limit =len(list_of_images_to_search)
        if len(list_of_images_to_search)< num_of_processes:
            num_of_processes = 1
        

        for iteration in range(len(list_of_images_to_search)):
            time_searching = time.time()
            similar_images=[]
            image = list_of_images_to_search[iteration]

            if not is_this_file_an_image(image) or image in already_scanned:
                if iteration == len(list_of_images_to_search) -1:
                    keep_running = False
                continue

            processes = []
            list_of_lists=split_list(num_of_processes, list_of_images_to_search)
            
            for i in range(num_of_processes):
                process = multiprocessing.Process(target=lambda: search_of_similar_images(i,image,list_of_lists[i],already_scanned))
                processes.append(process)
                process.start()
            
            # Wait for all processes to finish before proceeding
            for process in processes:
                process.join()
            
            # similar_images = search_of_similar_images(image,list_of_images_to_search)
            # Retrieve output from the queue
            print("Results of Searching for "+image)
            print("Results "+str(iteration)+"/"+str(limit)+"===============Images Matched===========================")
            temp_image = image
            already_scanned.append(image)
            for i in range(num_of_processes):
                list_of_similar_images = queue.get()
                for image in list_of_similar_images:
                    if image != temp_image:
                        print(image)
                    similar_images.append(image)
            time_taken=time.time()-time_searching
            print(pro_tip_Normal+"Searching took "+f"{time_taken:.3f}"+" Seconds and Found "+str(len(similar_images)-1)+" images similar to "+image)
            print("iteration number: "+str(iteration))
            print("==============================================================")
            if len(similar_images) >1:
                move_images(similar_images)
                print(pro_tip_Normal+"FINISHED MOVING SIMILAR IMAGES OF IMAGE "+image)
                break
            counter += 1
            if iteration == len(list_of_images_to_search) -1:
                keep_running = False
        counter += 1
    
    print(Dark+"==================================================================")
    # print(Dark+"Similar Pictures found:",Bright+str(len(similar_images)-1))
    print(Dark+"whole process toke:"+Bright+f"{(time.time()-time1):0.4f}"+Dark+" Seconds")
    print(Normal+"do you want to perform another Search ?")
    print(Bright+"(y) for yes, (n) for no: ",end="")
    user_input=input(Dark)
    if user_input=="n":
        exit()


# print(list_of_images_to_search)