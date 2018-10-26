#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from ConfigParser import ConfigParser

import gi
import re

gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, WebKit2, GdkPixbuf, GObject, Gdk
import argparse
import sys
import locale
import gettext
import os
import uuid
import shutil
import ntpath
import cairo
import pystray
from PIL import Image

try:
    import ConfigParser
except:
    import configparser as ConfigParser

from os.path import expanduser


def parser():
    pars = argparse.ArgumentParser()
    pars.add_argument("--webapp", action='store_const', const=True, default=False)
    pars.add_argument("--url", nargs="?")
    pars.add_argument("--appname", nargs="?")
    pars.add_argument("--apppath", nargs="?")

    return pars

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
                                                "Comment=" + description.get_buffer().get_text(
        description.get_buffer().get_start_iter(), description.get_buffer().get_end_iter(), True) + "\n"
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
    shutil.copyfile(work_dir + "/" + app_name.get_text() + ".desktop",
                    home_dir + "/.local/share/applications/" + app_name.get_text() + ".desktop")

    Gtk.main_quit()


# --------------------------------------------

def select_icon(obj, arg):
    global app_icon_path

    if arg.type == Gdk.EventType.BUTTON_PRESS and arg.button == 1:

        dialog = Gtk.FileChooserDialog(_("Please choose an icon file"), None,
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

def on_wa_close_window(w):
    print('Close window destroy')
    # return True

# --------------------------------------------

def on_wa_quit(w,d):
    global wa_config, namespace, win, iicon

    if g_cfg_toTrayWhenCloseWindow == True:
        win.hide()
        return True

    wpos = w.get_position()
    wsize = w.get_size()
    wa_config.set('DEFAULT', 'xpos', str(wpos[0]))
    wa_config.set('DEFAULT', 'ypos', str(wpos[1]))
    wa_config.set('DEFAULT', 'height', str(wsize[1]))
    wa_config.set('DEFAULT', 'width', str(wsize[0]))

    with open(namespace.apppath + "/settings.ini", 'w') as configfile:
        wa_config.write(configfile)

    iicon.visible = False
    Gtk.main_quit()

    # Gtk.destroy()


# --------------------------------------------

def browser_key_press(obj, event):
    global view
    keycode = event.get_keycode()
    if (keycode[1] == 71):
        view.reload()

    print(event.keyval, "  ", event.get_keycode())

# --------------------------------------------
#
# Check for unread messages by test page title
#
def on_title_changed(a, title):

    global g_cfg_useUMIndicator

    if g_cfg_useUMIndicator == False:
        # if g_cfg_useTrayIcon == True:
        set_app_icon()
        return

    t = a.get_property("title")

    # detect a (x) pattern in the title
    r = re.search("\\(\d+\\)", t)
    if r is not None:
        # print(r.pos)
        if r.pos == 0:
            # print(r.group(0))

            m = r.group(0)
            cnt = m[r.pos + 1:m.__len__() - 1]
            # print(title)
            set_app_icon(True)
        else:
            set_app_icon(False)
    else:
        set_app_icon(False)

# --------------------------------------------

def set_app_icon(alerted=False):
    global iicon, win, wa_config, g_cfg_useUMIndicator
    try:

        icon_name = wa_config.get('DEFAULT', 'icon')
        icon_pixbuf_1 = GdkPixbuf.Pixbuf.new_from_file(icon_name)

        mode = "RGB"
        if icon_pixbuf_1.props.has_alpha == True:
            mode = "RGBA"
        format = mode
        iwidth = icon_pixbuf_1.get_width()
        iheight = icon_pixbuf_1.get_height()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, iwidth, iheight)

        context = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(context, icon_pixbuf_1, 0, 0)
        context.paint()  # paint the pixbuf

        if alerted == True:
            context.set_source_rgba(255, 0, 0, 1)

            cd = surface.get_width() / 4.7
            ih = surface.get_height()
            iw = surface.get_width()
            context.arc(iw / 2 + cd / 2, iw / 2 + cd / 2, cd, 0, 2 * math.pi)
            context.fill()

        surface = context.get_target()
        icon_pixbuf_2 = Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

        data = icon_pixbuf_2.get_pixels()
        w = icon_pixbuf_2.props.width
        h = icon_pixbuf_2.props.height
        stride = icon_pixbuf_2.props.rowstride

        im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)

        win.set_icon(icon_pixbuf_2)

        if g_cfg_useTrayIcon == True:
            if iicon is None:
                iicon = pystray.Icon('WebAppSystray')
                iicon._status_icon.connect('button-press-event', on_status_icon_click)

            iicon.icon = im
            iicon.visible = True
            # iicon._status_icon.connect('button-press-event', on_status_icon_click)
    except:
        print("no icon")

# --------------------------------------------

def on_status_icon_click(icon, event):
    global win
    c = event.get_click_count()[1]
    if c == 1 or c > 2:
        return

    isVisible = win.get_property("visible")
    if (isVisible):
        win.hide()
    else:
        win.show()

    print('click ',c)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# GLOBAL VARS
g_cfg_useTrayIcon = True
g_cfg_useUMIndicator = True  # use Unread Meassages indicator
g_cfg_raiseOnUMArrived = False
g_cfg_toTrayWhenCloseWindow = True
g_cfg_startMinimizedOnTray = False
iicon = None
win = None  # Main window

# localize
locale.setlocale(locale.LC_ALL, '')
APP = "webapp"
DIR = "locale"
DATADIR = "/usr/share/" + APP

gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

webapp_dir = expanduser("~") + "/.config/webapp"
app_icon_path = webapp_dir + "/wa-logo.png"

if not os.path.exists(webapp_dir):
    os.makedirs(webapp_dir)
    shutil.copyfile("/usr/share/icons/wa-logo.png", app_icon_path)

parser = parser()
namespace = parser.parse_args()

wa_config = ConfigParser.ConfigParser()  # type: ConfigParser

if namespace.webapp:  # start web application mode

    view = WebKit2.WebView()

    browser_settings = view.get_settings()
    browser_settings.set_property('user-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0')
    browser_settings.set_property("enable-media-stream", True)
    browser_settings.set_property("enable-mediasource", True)
    browser_settings.set_property('enable-xss-auditor', False)
    view.set_settings(browser_settings)

    # view.connect("title-changed", on_title_changed)

    # cookiejar = Soup.CookieJarText.new(namespace.apppath + "/.cookies.txt", False)
    #
    # cookiejar.set_accept_policy(Soup.CookieJarAcceptPolicy.ALWAYS)
    # session = WebKit2.get_default_session()
    # session.add_feature(cookiejar)

    cm = view.get_context().get_cookie_manager()
    cm.set_persistent_storage(namespace.apppath + "/.cookies.txt", WebKit2.CookiePersistentStorage.TEXT)
    cm.set_accept_policy(WebKit2.CookieAcceptPolicy.ALWAYS)

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


    # set_app_icon()

    win.move(xpos, ypos)
    # win.set_size_request(width, height)
    win.set_default_size(width, height)

    # win.connect("destroy", Gtk.main_quit)
    win.connect("destroy", on_wa_close_window)
    win.connect("delete-event", on_wa_quit)
    win.set_title(namespace.appname + " - Web application")
    win.add(vbox)

    win.show_all()


    if g_cfg_startMinimizedOnTray == True:
        win.hide()

    # view.open(namespace.url)
    view.load_uri(namespace.url)

    view.connect("notify::title", on_title_changed)

    tt = view.get_title()

    # icon.run()

    Gtk.main()
    # icon.stop()

    exit()
# ---------------------------------------


# If current mode is WebApp creation

builder = Gtk.Builder()
builder.set_translation_domain(APP)  # for localize
builder.add_from_file(DATADIR + "/create-dlg.glade")

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
