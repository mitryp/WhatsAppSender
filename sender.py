# encoding UTF-8

import time
import webbrowser as web
from urllib.parse import quote

import requests as r
from pyautogui import size, click, hotkey


def check_connection() -> bool:
    """Checks connection to WhatsApp.

    :return: bool: True if connection is established
    """
    try:
        r.get('https://web.whatsapp.com/')
        return True
    except r.RequestException:
        return False


def format_number(number: str) -> str:
    """Formats phone number to match WhatsApp's phone number format.

    :param number: pure number
    :return: str: formatted number in format "+number"
    """
    newline = '\n'
    return f"{'+' if not '+' in number else ''}{number.strip().replace(newline, '')}"


def format_message(message: str) -> str:
    """Formats message to match URL encoding rules.

    :param message: pure text
    :return: str: formatted message with special symbols escaped
    """
    message = message.strip()
    # return message.replace(' ', '%20').replace('!', '%21').replace('\n', '%0A').replace('\"', '%22').replace('\'',
    #                                                                                                          '%27')
    return quote(message)


def get_new_browser() -> web.BaseBrowser:
    """Returns a new browser instance.

    :return: BaseBrowser
    """
    return web.get()


def _send(number: str, message: str, browser: web.BaseBrowser, wait_time: float = 8, close_tab: bool =False) -> None:
    """Sends a message `message` to the WhatsApp user with the number `number` with browser `browser`.

    The script will control your mouse and keyboard while sending the message.

    Note that you must log in to your WhatsApp account in your default browser before sending a message.
    Also, you should not press any buttons during the message sending.

    :param number: pure or formatted number
    :param message: pure or formatted message
    :param browser: BaseBrowser instance: browser instance in which the message will be sent
    :param wait_time: float: time to wait before sending a message
    :param close_tab: bool: if True, tab will be closed after sending a message
    :return: None
    """
    number = format_number(number)
    message = format_message(message)

    browser.open_new_tab(
        "https://web.whatsapp.com/send?phone=" + number + "&text=" + message
    )
    time.sleep(wait_time)
    width, height = size()
    click(width / 2, height / 2)
    hotkey("enter")
    time.sleep(wait_time/10)
    if close_tab:
        hotkey("ctrl", "command", "w")
