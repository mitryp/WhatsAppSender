# encoding UTF-8

import os
import time
from sys import argv
from argparse import ArgumentParser

import requests as r

from sender import check_connection, format_number, get_new_browser, _send


__version__ = '1.0.0'

# Enter your API links here:
API_LINK = ''
API_GET_LINK_BODY = ''
API_REPORT_LINK_BODY = ''
# A text response from URL `{API_LINK}/{API_GET_LINK_BODY}{number}` will be used to get count of messages sent 
# to the certain number;
# A request to URL `{API_LINK}/{API_REPORT_LINK_BODY}{number}` will be used to report message sending;
# If you don't want to use the API to count messages centrally, just leave that constants unchanged.

if __name__ == '__main__':
    # Get CLI arguments
    parser = ArgumentParser(description='A script to send message to all WhatsApp numbers listed in file.'
                                        '\nFirst, it opens a WhatsApp login page for you to log in and, maybe, turn '
                                        'the VPN on. Then, you press Enter in the console and the distribution begins.'
                                        '\nNote that you shouldn\'t touch the keyboard and the mouse during '
                                        'the process.')
    parser.add_argument('source', action='store', type=str,
                        help='A path to source file with phone numbers. Numbers must be placed one per line')
    parser.add_argument('-t', '--text', action='store', type=str, help='A text message to send')
    parser.add_argument('-f', '--file', action='store', type=str, help='A path to a file with a message that will be'
                                                                       ' sent')
    parser.add_argument('-l', '--logged-in', action='store_true',
                        help='To mark that you are already logged in. With this flag the script won\'t wait until you '
                             'press ENTER after logging in and start sending instantly')
    parser.add_argument('--message-limit', action='store', type=int, default=1,
                        help='An absolute messages limit per one number')
    parser.add_argument('--timeout', action='store', type=int, default=60,
                        help='A timeout in seconds to wait between every 8 messages. Default is 60 seconds')
    parser.add_argument('--wait-time', action='store', type=int, default=10,
                        help='A time in seconds for WhatsApp to load before sending a message. Default is 10 seconds')
    parser.add_argument('--force', action='store_true',
                        help='Do not check whether the messages were already sent to this number. If present, '
                             'the script won\'t connect to the API to get messages count, but still will report about '
                             'sending messages')

    args = parser.parse_args(argv[1:])

    # Display the help message if the arguments are incorrect
    if len(argv) < 2:
        parser.print_help()
        exit(1)

    # Check the source file to exist
    if not os.path.exists(args.source):
        print("The source file does not exist.")
        exit(1)

    # Get numbers from the source file
    with open(args.source, 'r', encoding='utf-8') as f:
        numbers_list: list = f.readlines()

    # Try to get message
    message: str
    if args.text:
        message = args.text
    elif args.file is not None and os.path.exists(args.file):
        with open(args.file, 'r', encoding='utf-8') as f:
            message = f.read()
    else:
        print('No message provided or the message file does not exist.')
        exit(1)

    # Check connection to WhatsApp
    print('Trying to resolve https://web.whatsapp.com/')
    if check_connection():
        print("Success!")
    else:
        print("No connection to WhatsApp.")
        exit(1)

    # Check connection to the API
    # If the API is unavailable, uses the --force flag
    try:
        r.get(API_LINK)
    except r.RequestException:
        args.force = True

    print("Starting distribution..")

    # Get the browser instance
    browser = get_new_browser()

    # Open login page if the user didn't set the -l flag
    if not args.logged_in:
        browser.open_new('https://web.whatsapp.com/')
        input("Browser was opened. Press ENTER after logging in..")
    else:
        print('Without logging in.')

    # Send the message to each number if the number hasn't got more messages than the limit
    #                                 --force flag cancels this check
    messages_sent = 0
    for number in numbers_list:
        if messages_sent != 0 and messages_sent % 8 == 0:
            time.sleep(args.timeout)

        try:
            if args.force or int(r.get(f'{API_LINK}/{API_GET_LINK_BODY}{format_number(number)}').text) < args.message_limit:
                print("Trying to send message", '->', number)
                _send(number, message, browser)
                messages_sent += 1
                if len(API_LINK) > 0:
                    try:
                        r.get(f'{API_LINK}/{API_REPORT_LINK_BODY}{format_number(number)}')
                        print('Message reported')
                    except r.RequestException:
                        print('Reporting failed')

            else:
                print('Didn\'t send message to number', number)

        except ValueError:
            _send(number, message, browser)
            messages_sent += 1
    else:
        print('The script has finished his work.')
        input('Press ENTER to exit')
