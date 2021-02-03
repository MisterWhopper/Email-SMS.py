import receiver as sms
import win32clipboard as clip
from PIL import Image
from io import BytesIO
from time import sleep
from win10toast import ToastNotifier
from os import remove, system

def sendClip(clip_type,data):
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(clip_type,data)
    clip.CloseClipboard()

def copyImageToClip(f):
    im = Image.open(f)
    out = BytesIO()
    im.convert("RGB").save(out,"BMP")
    data = out.getvalue()[14:]
    out.close()
    sendClip(clip.CF_DIB,data)

def main():
    acceptable = ["bmp","jpg","jpeg"]
    tn = ToastNotifier()
    hostname = 'gmail-imap.l.google.com'
    port = 993
    username = 'who_you_want_to_send_it_to@gmail.com'
    password = 'p@55w0rd!'
    act_on = False
    while True:
        with sms.createConnection(hostname,port,username,password) as con:
            messages = [m for m in sms.getAllMessages(con)] # get all of the messages in the inbox
            if messages == []:
                print("No new messages!")
                sleep(5)
                continue
            messages.sort(key=lambda m: m.when,reverse=True) # sort by most recent messages
            # check if the data in the latest message is of a type that we accept
            act_on = (messages[0].isbin and messages[0].file.split(".")[1] in acceptable) or (isinstance(messages[0].data,str))
            if act_on:
                sms.deleteAllEmails(con)
        if act_on:
            if messages[0].isbin:
                with open(messages[0].file, "wb") as f:
                    f.write(messages[0].data)
                copyImageToClip(messages[0].file)
                remove(messages[0].file)
                tn.show_toast("Phone2Board","New image added to clipboard from phone!")
            else:
                # the lazy method of getting text onto the clipboard. I'm not responsible if someone rm -rfs your machine
                # system("echo " + messages[0].data + " | clip")
                # I guess I will fix this 
                clip.SetClipboardText(messages[0].data, clip.CF_UNICODETEXT)
                tn.show_toast("Phone2Board", "Text on clipboard replaced w/ data from SMS")
        else:
            print("No new messages!")
            sleep(5)
            continue

if __name__ == "__main__":
    main()
