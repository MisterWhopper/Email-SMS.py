# Email-SMS.py
A janky method using SMTP and IMAP to handle SMS messages.

These files are designed for Windows-based systems, and also by a younger me who didn't believe in things like objects and classes. So to say this code is a bit jank is an understatement; you can also find remnants of cleanup efforts, but I gave up and moved on to other projects as I am wont to do. **I also have no idea how well this will work on networks other than mine**, so for the sake of disclosure I wrote this for my iPhone on the Verizon network. If you encounter errors, please feel free to submit a PR.

To use this, simply double-click the file in Windows and it will run. If you are using the `board-to-phone.pyw` file, you must select some data you wish to send, place it into your keyboard, and then hit the `Win+Shift+Ctrl+S` keys to send the data over SMTP to your SMS device. The `phone-to-board.pyw` file will run in the background constantly looking for the next email to parse.

This collection of scripts requires the following 3rd-party modules to run:

* `keyboard` - this fantastic module gives system-wide access to the keyboard. This is used to detect the keyboard shortcut to trigger the sending script

* `win10toast` - allows us to make Windows notifications easily

* `Pillow` - image framework for Python, used for grabbing image data from the clipboard

* `win32clipboard` - handles the clipboard for Windows, used for setting image data in clipboard