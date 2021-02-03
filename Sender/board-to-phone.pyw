from PIL        import ImageGrab        # allows us to grab the image from the clipboard
import keyboard as kb                   # allows us to detect keyboard presses system-wide
from os         import remove           # deletes files
from os.path    import basename         # 'path/path/file.extension' becomes just 'file.extension'
from shutil     import copyfile         # allows us to copy files
from win10toast import ToastNotifier    # Gives us Windows 10 notifications
import win32clipboard as clip           # handles clipboard text

# email handler imports

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# email configuration

SENDING_EMAIL_ADDRESS   = "sample@gmail.com"
SENDING_EMAIL_PASSWORD  = "p@55w0rd!"
EMAIL_HOST              = "smtp.gmail.com"
EMAIL_PORT              = 587

TO_SEND = "who_you_want_to_send_it_to@gmail.com"

def sendMsg(to_addr, msg, host=EMAIL_HOST,port=EMAIL_PORT,username=SENDING_EMAIL_ADDRESS,password=SENDING_EMAIL_PASSWORD):
    server = smtplib.SMTP(host=host,port=port)
    server.ehlo()
    server.starttls()
    server.login(user=username,password=SENDING_EMAIL_PASSWORD)
    server.sendmail(SENDING_EMAIL_ADDRESS, to_addr,msg)

def sendAttachment(to_addr, fileName, sub="Test", text="File", host=EMAIL_HOST,port=EMAIL_PORT,username=SENDING_EMAIL_ADDRESS,password=SENDING_EMAIL_PASSWORD):
    server = smtplib.SMTP(host=host,port=port)
    server.ehlo()
    server.starttls()
    server.login(user=username,password=password)

    msg = MIMEMultipart()
    msg['From']     = username
    msg['To']       = to_addr
    msg['Date']     = formatdate(localtime=True)
    msg['Subject']  = sub

    msg.attach(MIMEText(text))

    with open(fileName, "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=fileName
        )
    # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % fileName
    msg.attach(part)

    server.sendmail(username,to_addr,msg.as_string())

def handler(): # Takes our input and saves it depending on what type of input that it is
    notifier = ToastNotifier() # Shows Windoew 10 notifications when we ask it to
    im = ImageGrab.grabclipboard() # get the image from the clipboard
    if im is not None: # is there a picture to save?
        im.save("paste.png","PNG") # save it as a PNG
        # here is where the magic happens; we send out the email w/ the image
        sendAttachment(TO_SEND, "paste.png")
        remove("paste.png") # delete the PNG, we don't need it anymore
        notifier.show_toast("Board2Phone", "Screenshot sent!") # alert the user their screenshot has been sent
    else:
        txt = clip.GetClipboardData(clip.CF_UNICODETEXT) # grab the text from the clipboard
        if txt.find("http") >= 0: # if the text is a link, we may need to send it in a file or else the carrier may see it as spam
            with open("link.txt","w") as f: # Create a new file to hold the link text
                f.write(txt)
            # here we send the link text file through MMS
            sendAttachment(TO_SEND, "link.txt")
            remove("link.txt") # once we have sent it, we no longer need the link file
            notifier.show_toast("Board2Phone","Link sent!")
        elif txt.find("C:\\") >= 0: # This is a file path, so let's send the file itself
            fpath = txt.strip('"').strip('"') # remove quotation marks if there are any
            fname = basename(fpath)
            copyfile(fpath,f"./{fname}") # copy the file to our local directory
            # Send the file through MMS
            sendAttachment(TO_SEND, fname)
            remove(fname) # remove the locally copied file
            notifier.show_toast("Board2Phone","File sent!")
        elif len(txt) >= 160: # SMS only allows for text of 160-chars or less; long text send as attachment
            f = open("msg.txt","w")
            f.write(txt)
            f.close()
            # Send the long text file through MMS as an attachment
            sendAttachment(TO_SEND, "msg.txt")
            remove("msg.txt")
            notifier.show_toast("Board2Phone","Long message sent!")
        else:
            # Send the message through SMS
            sendMsg(TO_SEND, txt)
            notifier.show_toast("Board2Phone", "Text sent!")
        

def main(): # this runs our keyboard shortcut indefinitely until we press the magic keys to tell it to stop
    shortcut = "Win+Ctrl+Shift+S" # the keyboard shortcut we want to push to activate our code
    kb.add_hotkey(shortcut,handler,args=None) # listen for the keyboard shortcut, and when it is pressed, run the code
    kb.wait("Win+Shift+Esc") # always run this program until we push Win+Shift+Esc, and when we do stop running

if __name__ == "__main__": # is this file being run by itself? if so, we want to run our main function.
    main()
