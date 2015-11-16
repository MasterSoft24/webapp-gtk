#!/usr/bin/env python
# -*- coding: utf-8 -*-


import gi

#gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, WebKit, GdkPixbuf, Gdk
from gi.repository import Soup

import argparse
import sys
import locale
import gettext
import os
import uuid
import shutil
import ntpath

try:
    import ConfigParser
except:
    import configparser as ConfigParser
    
from os.path import expanduser
from os.path import exists
from os import makedirs


def parser():
    pars = argparse.ArgumentParser()
    pars.add_argument("--webapp", action='store_const', const=True, default=False)
    pars.add_argument("--url", nargs="?")
    pars.add_argument("--appname", nargs="?")
    pars.add_argument("--apppath", nargs="?")

    return pars


# -----------------------------------------
#
# def navrequest(thisview, frame, networkRequest):
#     address = networkRequest.get_uri()
#     if not "debian.org" in address:
#         # GTK2 style:
#         #   md = Gtk.MessageDialog(win, Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE, "Not allowed to leave the site!")
#         # GTK3 style :
#         # (however I don't know about " Gtk.DIALOG_DESTROY_WITH_PARENT" ?)
#         md = Gtk.MessageDialog(win, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, ("Not allowed to leave the site!"))
#
#         md.run()
#         md.destroy()
#         view.open("http://www.debian.org")


# ------------------------------------------


def webapp_create(button):
    global app_icon_path, wa_config

    home_dir = expanduser("~")
    work_dir = home_dir + "/.config/webapp/webapp-" + app_name.get_text() + "-" + str((uuid.uuid1()))

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)




    # Copy application icon file to application dir
    if ntpath.basename(app_icon_path) != "wa-logo.png":
        app_icon_path_new = work_dir + "/" + ntpath.basename(app_icon_path)
        shutil.copyfile(app_icon_path, app_icon_path_new)
        app_icon_path = app_icon_path_new

    # Create settings.ini file

    # wa_config.add_section('DEFAULT')
    wa_config.set('DEFAULT', 'icon', app_icon_path)

    with open(work_dir + "/settings.ini", 'w') as configfile:
        wa_config.write(configfile)


    # Create .desktop file
    file = open(work_dir + "/" + app_name.get_text() + ".desktop", "w")
    deskfile = ("[Desktop Entry]\n"
                "Version=1.0\n"
                "Name=" + app_name.get_text() + "\n"
                "Comment=" + description.get_buffer().get_text(description.get_buffer().get_start_iter(),description.get_buffer().get_end_iter(), True) + "\n"
                "StartupNotify=true\n"
                "Icon=" + app_icon_path + "\n"
                "Terminal=false\n"
                "Type=Application\n"
                "Exec=webapp --webapp --url " + url.get_text() + " --appname=\"" + app_name.get_text() + "\" --apppath=\"" + work_dir + "\"\n"
                # "Exec=nemo\r\n"
                "Categories=Web applications\n"
                )
    file.write(deskfile)

    file.close()
    shutil.copyfile(work_dir + "/" + app_name.get_text() + ".desktop", home_dir+"/.local/share/applications/"+app_name.get_text() + ".desktop")

    Gtk.main_quit()


# --------------------------------------------

def select_icon(obj, arg):
    global app_icon_path

    if arg.type == Gdk.EventType.BUTTON_PRESS and arg.button == 1:

        dialog = Gtk.FileChooserDialog(_("Please choose a icon file"), None,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            app_icon = builder.get_object("app_icon")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(dialog.get_filename(), 100, 100)
            app_icon.set_from_pixbuf(pixbuf)
            app_icon_path = dialog.get_filename()

        dialog.destroy()


# --------------------------------------------

def on_wa_quit(w, d):
    global wa_config, namespace
    wpos = w.get_position()
    wsize = w.get_size()
    wa_config.set('DEFAULT', 'xpos', str(wpos[0]))
    wa_config.set('DEFAULT', 'ypos', str(wpos[1]))
    wa_config.set('DEFAULT', 'height', str(wsize[1]))
    wa_config.set('DEFAULT', 'width', str(wsize[0]))

    with open(namespace.apppath + "/settings.ini", 'w') as configfile:
        wa_config.write(configfile)

    Gtk.main_quit()


# --------------------------------------------

def browser_key_press(obj, event):
    global view
    keycode = event.get_keycode()
    if (keycode[1] == 71):
        view.reload()

    print(event.keyval, "  ", event.get_keycode())


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# localize
locale.setlocale(locale.LC_ALL, '')
APP = "webapp"
DIR = "locale"
DATADIR="/usr/share/"+APP

gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

webapp_dir = expanduser("~") + "/.config/webapp"
app_icon_path = webapp_dir + "/wa-logo.png"

if not os.path.exists(webapp_dir):
    os.makedirs(webapp_dir)
    shutil.copyfile("/usr/share/icons/wa-logo.png",app_icon_path)

parser = parser()
namespace = parser.parse_args()

wa_config = ConfigParser.ConfigParser()


if namespace.webapp:# start web application mode

    view = WebKit.WebView()
    #	view.connect("navigation-requested", navrequest)

    browser_settings = view.get_settings()
    #browser_settings.set_property('user-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1')
    browser_settings.set_property("enable-media-stream",True)
    browser_settings.set_property("enable-mediasource",True)
    view.set_settings(browser_settings)

    cookiejar = Soup.CookieJarText.new(namespace.apppath + "/.cookies.txt", False)

    cookiejar.set_accept_policy(Soup.CookieJarAcceptPolicy.ALWAYS)
    session = WebKit.get_default_session()
    session.add_feature(cookiejar)

    sw = Gtk.ScrolledWindow()
    sw.connect("key_press_event", browser_key_press)

    sw.add(view)


    # hbox=Gtk.HBox();
    vbox = Gtk.VBox()
    vbox.add(sw)

    win = Gtk.Window()




    # read config file or set default values
    wa_config.read(namespace.apppath + "/settings.ini")

    try:
        xpos = wa_config.getint('DEFAULT', 'xpos')
    except:
        xpos = 0
    try:
        ypos = wa_config.getint('DEFAULT', 'ypos')
    except:
        ypos = 0
    try:
        height = wa_config.getint('DEFAULT', 'height')
    except:
        height = 600
    try:
        width = wa_config.getint('DEFAULT', 'width')
    except:
        width = 800
    # try:
    #     maximized=wa_config.getboolean('DEFAULT','maximized')
    # except:
    #     maximized=False


    try:
        icon_name = wa_config.get('DEFAULT', 'icon')
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, 255, 255)
        win.set_icon(icon_pixbuf)
    except:
        print("no icon")

    win.move(xpos, ypos)
    # win.set_size_request(width, height)
    win.set_default_size(width, height)

    win.connect("destroy", Gtk.main_quit)
    win.connect("delete_event", on_wa_quit)
    win.set_title(namespace.appname + " - Web application")
    win.add(vbox)
    win.show_all()

    view.open(namespace.url)
    Gtk.main()

    exit()
# ---------------------------------------




# If current mode is WebApp creation

builder = Gtk.Builder()
builder.set_translation_domain(APP)  # for localize
builder.add_from_file(DATADIR+"/create-dlg.glade")

window = builder.get_object("create_dlg")
window.set_size_request(500, 300)
window.connect("destroy", Gtk.main_quit)

app_icon = builder.get_object("app_icon")
try:
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(app_icon_path, 100, 100)
    app_icon.set_from_pixbuf(pixbuf)
except:
    print("no logo file found")




# get UI objects
app_name = builder.get_object("app_name")
url = builder.get_object("url")
description = builder.get_object("description")



# connect UI signals to program
cancel_button = builder.get_object("cancel_button")
cancel_button.connect("clicked", Gtk.main_quit)
ok_button = builder.get_object("ok_button")
ok_button.connect("clicked", webapp_create)

# app_icon=builder.get_object("app_icon")
# pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('t.jpg',100,100)

app_icon_event = builder.get_object("icon_eventbox")
app_icon_event.connect("button-press-event", select_icon)

# app_icon.set_from_pixbuf(pixbuf)


window.show_all()

Gtk.main()
