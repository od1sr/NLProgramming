import socket
import flet as ft
from time import sleep
from src.frontend.settings import *
'''
    Function for checking internet connection
'''
def is_connected(hostname):
    try:
        # See if we can resolve the host name - tells us if there is
        # A DNS listening
        host = socket.gethostbyname(hostname)
        # Connect to the host - tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception:
        pass # We ignore any errors, returning False
    return False

'''
    Function for culdowning input box
'''
def wait_timer_start(page: ft.Page, input_button: ft.IconButton, timer_text):
    global wait_timer
    wait_timer = 10
    input_button.disabled = True
    input_button.bgcolor = COLORS['accent']
    timer_text.visible = True
    page.update()

    while wait_timer > 0:
        sleep(1)
        wait_timer -= 1
        timer_text.value = f'{wait_timer}s'
        page.update()

    input_button.disabled = False
    input_button.bgcolor = COLORS["primary"]
    timer_text.value = ''
    timer_text.visible = False
    page.update()


'''
    Function for server response timer
'''

