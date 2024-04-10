import sys, os
import requests
import time
from threading import Thread, Event
from ahk import AHK
from tkinter import Tk, Button, Label, Radiobutton, IntVar, Frame
import keyboard 

ahk = AHK()

def is_pixel_white(x, y):
    color = ahk.pixel_get_color(x, y)
    return color == '0xFFFFFF'

def update_task_label(text):
    root.after(0, lambda: current_task_label.config(text=f"Aktuální úloha: {text}"))
def execute_ahk_actions(text, remove_f=False, type_34=False):

    ahk.win_activate('Roblox')
    ahk.win_wait_active('Roblox', timeout=30)
    time.sleep(1)
    
    ahk.key_press('F')
    time.sleep(0.5)

    if not is_pixel_white(1214, 250): #bílá plocha v inventáři (pro kontrolu zda je otevřen inventář)
        ahk.key_press('F')
        print("No White")
    
    if type_34:
        update_task_label("Consume Potions")
        ahk.mouse_move(414, 457, speed=5) #Klik na ikonu potionů v inventáři
        time.sleep(0.1)
        ahk.click()
        time.sleep(0.1)

        ahk.mouse_move(783, 505, speed=5) #Klik na pozici IV potionů
        for _ in range(200):
            ahk.click()
            time.sleep(0.001) 
        time.sleep(1)
    
    if not type_34:
        ahk.mouse_move(413, 398, speed=5) #Klik na ikonu itemů v inventáři (batůžek)
        time.sleep(0.1)
        ahk.click()

        ahk.mouse_move(1340, 251, speed=5) #Klik na search bar
        time.sleep(0.3)
        ahk.click()
        ahk.click()
        time.sleep(0.1)

        print(f"Sending text: {text}")
        update_task_label(text)
        ahk.type(text)
        time.sleep(0.1)
    
        ahk.mouse_move(504, 381, speed=5) #Klik na první nalezený item 
        time.sleep(0.1)
        ahk.click()
        time.sleep(0.2)

        ahk.mouse_move(947, 746, speed=5) #Klik na tlačítko "ok", když se vypíše chyba, že už je v lokaci item
        time.sleep(0.1)
        ahk.click()
        time.sleep(0.2)

    if type_34:
        ahk.mouse_move(410, 394, speed=10) #Klik na ikonu itemů v inventáři (batůžek)
        time.sleep(0.1)
        ahk.click()
        time.sleep(0.1)

    ahk.mouse_move(908, 126, speed=10) #Klik mimo inventář před zavřením (kamkoliv nad okno inventáře)
    time.sleep(0.1)
    if not remove_f:
        ahk.key_press('F')

def stop_all_threads():
    for event in thread_stop_events:
        event.set()

    running_threads.clear()
    thread_stop_events.clear()
    print("Threads cleared!")

def press_space_and_r():
    update_task_label("ANTI AFK!")
    print("Pressing Space and R")
    ahk.key_press('Space')
    ahk.key_press('R')

def activate_goal(goal_type):
    stop_all_threads()  
    global active_goal_type
    active_goal_type = goal_type

    new_stop_event = Event()
    thread_stop_events.append(new_stop_event)

    if goal_type == 37:
        text = "Basic Coin Jar"
        interval = 2
        remove_f = False
        type_34 = False
    elif goal_type == 38:
        text = "Comet"
        interval = 1
        remove_f = False
        type_34 = False
    elif goal_type == 44:
        text = "Lucky Block"
        interval = 8
        remove_f = True
        type_34 = False
    elif goal_type == 34:  
        text = "IV" 
        interval = 0
        remove_f = False
        type_34 = True 
    elif goal_type == 43:
        text = "Piñata"
        interval = 4
        remove_f = True
        type_34 = False
    else: 
        text = "ANTI AFK"
        interval = 60
        remove_f = False
        type_34 = False 
        
    print(f"Detected goal type: {goal_type}, executing script with '{text}'")
    new_thread = Thread(target=execute_ahk_script, args=(text, interval, remove_f, type_34, new_stop_event))
    new_thread.start()
    running_threads.append(new_thread)    

def execute_ahk_script(text, interval, remove_f=False, type_34=False, stop_event=None):
    stop_event = stop_event or Event()
    while not stop_event.is_set():
        if active_goal_type in [37, 38, 44, 34, 43]:
            execute_ahk_actions(text, remove_f, type_34)
        else:
            press_space_and_r()
        time.sleep(interval)

running_threads = []
thread_stop_events = []

def check_api_and_run():
    global active_goal_type
    priority_types = [37, 38, 44, 34, 43]
    while not stop_thread.is_set():
        url = 'https://biggamesapi.io/api/clan/VLP' if clan_choice.get() == 1 else 'https://biggamesapi.io/api/clan/VLP2'
        response = requests.get(url)
        data = response.json()

        last_two_goals = data['data']['Battles']['GoalBattleTwo']['Goals'][-2:]

        found_priority_type = False
        for goal in last_two_goals[::-1]:
            goal_type = goal['Type']
            if goal_type in priority_types:
                if active_goal_type != goal_type:
                    stop_all_threads()
                    activate_goal(goal_type)
                found_priority_type = True
                break

        if not found_priority_type:
            stop_all_threads()
            print("No active priority goal type, pressing space and R.")
            press_space_and_r()
            time.sleep(60)

        time.sleep(5)

def toggle_script():
    global running_threads, thread_stop_events, active_goal_type
    if button.config('text')[-1] == 'START (F7)':
        button.config(text='STOP (F7)')
        stop_thread.clear()
        checker_thread = Thread(target=check_api_and_run)
        checker_thread.start()
        running_threads.append(checker_thread)
    else:
        button.config(text='START (F7)')
        stop_thread.set()
        for event in thread_stop_events:
            event.set()

        for thread in running_threads:
            thread.join()

        running_threads.clear()
        thread_stop_events.clear()
        active_goal_type = None

active_goal_type = None
stop_thread = Event()

root = Tk()
root.title("Auto Clan Quests | by Psyche")
root.attributes('-topmost', True)
root.geometry('280x250')

root.configure(bg='#333333')

title_label = Label(root, text="Auto Clan Quest 2.0b", font=("Helvetica", 16, "bold"), bg='#333333', fg='white')
title_label.pack(pady=(15, 0))

current_task_label = Label(root, text="by Psychedelic", font=("Helvetica", 12), bg='#333333', fg='white')
current_task_label.pack(pady=(5, 10))

current_task_label = Label(root, text="Aktuální úloha: ", font=("Helvetica", 11), bg='#333333', fg='white')
current_task_label.pack(pady=(0, 0))

radiobutton_frame = Frame(root, bg='#333333')
radiobutton_frame.pack(pady=10)

clan_choice = IntVar(value=1)

Radiobutton(radiobutton_frame, text="VLP", font=("Helvetica", 10), variable=clan_choice, value=1, bg='#333333', fg='white', selectcolor='#555555').pack(side='left')
Radiobutton(radiobutton_frame, text="VLP2", font=("Helvetica", 10), variable=clan_choice, value=2, bg='#333333', fg='white', selectcolor='#555555').pack(side='left')

button = Button(root, text="START (F7)", command=toggle_script, 
                bg='#556677', fg='white', 
                font=('Helvetica', 12, 'bold'), 
                padx=5, pady=5, 
                borderwidth=2, relief="ridge")
button.pack(pady=20)

keyboard.add_hotkey('F7', toggle_script)

root.mainloop()
