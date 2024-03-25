import sys, os
import requests
import time
from threading import Thread, Event
from ahk import AHK
from tkinter import Tk, Button, Label
import keyboard 

ahk = AHK()

def update_task_label(text):
    root.after(0, lambda: current_task_label.config(text=f"Aktuální úloha: {text}"))
def execute_ahk_actions(text, remove_f=False, type_34=False):
    ahk.win_activate('Roblox')
    ahk.win_wait_active('Roblox', timeout=30)
    time.sleep(1)
    
    ahk.key_press('F')
    time.sleep(0.1)
    
    if type_34:
        update_task_label("Consume Potions")
        ahk.mouse_move(414, 457, speed=5) #Klik na ikonu potionů v inventáři
        time.sleep(0.1)
        ahk.click()
        time.sleep(0.1)

        ahk.mouse_move(684, 513, speed=5) #Klik na pozici IV potionů
        for _ in range(200):
            ahk.click()
            time.sleep(0.001) 
        time.sleep(1)
    
    if not type_34:
        ahk.mouse_move(413, 398, speed=5) #Klik na ikonu itemů v inventáři (batůžek)
        time.sleep(0.1)
        ahk.click()

        ahk.mouse_move(1340, 251, speed=5) #Klik na search bar
        time.sleep(0.1)
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

def execute_ahk_script(text, interval, remove_f=False, type_34=False, stop_event=None):
    stop_event = stop_event or Event()
    while not stop_event.is_set():
        execute_ahk_actions(text, remove_f, type_34)
        time.sleep(interval)


running_threads = []
thread_stop_events = []

def check_api_and_run():
    global active_goal_type
    while not stop_thread.is_set():
        response = requests.get('https://biggamesapi.io/api/clan/VLP')
        data = response.json()

        last_two_goals = data['data']['Battles']['GoalBattleOne']['Goals'][-2:]
        types = [goal['Type'] for goal in last_two_goals]

        if active_goal_type not in types:
            active_goal_type = None

        for goal_type in types[::-1]:
            if goal_type in [37, 38, 44, 34, 43]:
                if active_goal_type != goal_type:
                    active_goal_type = goal_type
                    for event in thread_stop_events:
                        event.set()
                    running_threads.clear()
                    thread_stop_events.clear()

                    new_stop_event = Event()
                    thread_stop_events.append(new_stop_event)
                    if goal_type == 37:
                        text = "Basic Coin Jar"
                        interval = 6
                        remove_f = False
                        type_34 = False
                    elif goal_type == 38:
                        text = "Comet"
                        interval = 5
                        remove_f = False
                        type_34 = False
                    elif goal_type == 44:
                        text = "Lucky Block"
                        interval = 8
                        remove_f = True
                        type_34 = False
                    elif goal_type == 43:
                        text = "Piñata"
                        interval = 4
                        remove_f = True
                        type_34 = False
                    elif goal_type == 34:  
                        text = "IV" 
                        interval = 0
                        remove_f = False
                        type_34 = True 
                        
                    print(f"Detected goal type: {goal_type}, executing script with '{text}'")
                    new_thread = Thread(target=execute_ahk_script, args=(text, interval, remove_f, type_34, new_stop_event))
                    new_thread.start()
                    running_threads.append(new_thread)
                break
        else:
            if active_goal_type is not None:
                stop_thread.set()
                for event in thread_stop_events:
                    event.set()
                running_threads.clear()
                thread_stop_events.clear()
                active_goal_type = None
                print("No matching goal type found, pressing R and Space")
                ahk.key_press('R')
                ahk.key_press('Space')
                time.sleep(60)
            else:
                print("Continuing to press R and Space as no goal is active")
                ahk.key_press('R')
                ahk.key_press('Space')
                time.sleep(60)
        time.sleep(5)

def toggle_script():
    global running_threads, thread_stop_events, active_goal_type
    if button.config('text')[-1] == 'Start':
        button.config(text='Stop')
        stop_thread.clear() 
        checker_thread = Thread(target=check_api_and_run)
        checker_thread.start()
        running_threads.append(checker_thread) 
    else:
        button.config(text='Start')
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

title_label = Label(root, text="Auto Clan Quest", font=("Helvetica", 16, "bold"))
title_label.pack(pady=(15, 0))

current_task_label = Label(root, text="by Psychedelic", font=("Helvetica", 12))
current_task_label.pack(pady=(5, 10))

current_task_label = Label(root, text="Aktuální úloha: ", font=("Helvetica", 11))
current_task_label.pack(pady=(0, 0))

button = Button(root, text="Start", command=toggle_script)
button.pack(pady=20)

keyboard.add_hotkey('F7', toggle_script)

root.mainloop()
