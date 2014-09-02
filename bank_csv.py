from __future__ import print_function
import bank
import time
import web

def update():
    date = time.strftime("%d/%m/%Y")
    values = bank.main()
    values.insert(0, date)

    new_content = ','.join([str(x) for x in values]) + "\r\n"
    new_content.encode("ascii")
    with open(web.get_path(), "ab+") as f:
        f.write(new_content)

def open_browser():
    import webbrowser
    webbrowser.open("http://{}:{}".format(web.IP_ADDR, web.PORT))

def main():
    update()
    print("Starting webserver...")
    import threading
    threading.Timer(2, open_browser).start()
    web.main()

if __name__ == '__main__':
    main()
