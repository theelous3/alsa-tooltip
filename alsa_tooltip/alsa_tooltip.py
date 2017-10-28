#!usr/bin/env python3

import subprocess
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class app(Gtk.Window):
    '''Hi'''
    def __init__(self, volume_mod):
        super().__init__()

        self.volume_mod = volume_mod
        self.current_vol = self.poll_volume()
        self.set_size_request(250, 40)

        self.set_resizable(False)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        label = Gtk.Label("VOL")

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_fraction(self.current_vol)

        self.add(self.vbox)
        self.vbox.pack_start(label, True, True, 0)
        self.vbox.pack_start(self.progressbar, True, True, 0)

        self.timeout_lifespan = GObject.timeout_add(500, self.on_timeout, None)
        self.timeout_show_mod = GObject.timeout_add(100, self.modify_volume, None)

    def poll_volume(self):
        alsa_task = subprocess.Popen(['amixer', 'get', 'Master'], stdout=subprocess.PIPE)
        alsa_task.wait()
        result = alsa_task.communicate()[0].decode('utf-8').split()[-3]
        result = int(''.join([x for x in result if (47 < ord(x) < 58)]))
        return result / 100

    def modify_volume(self, _):
        amount = '5%'
        direction = '+'
        command = ['amixer', 'set', 'Master']
        progressbar_current = self.progressbar.get_fraction()

        if self.volume_mod == '-u':
            bar_adjust = 0.05
            if self.current_vol > 0.94:
                command.append('100%')
                progressbar_current = 1
                bar_adjust = 0
            else:
                command.append(amount+direction)
        else:
            direction = '-'
            bar_adjust = (-0.05)
            command.append(amount+direction)
        alsa_task = subprocess.Popen(command, stdout=subprocess.PIPE)
        alsa_task.wait()
        self.progressbar.set_fraction(progressbar_current + bar_adjust)
        print('cmd', command)

    def on_timeout(self, _):
        '''Bye'''
        Gtk.main_quit()


def main(argv):
    try:
        assert(argv in ('-u', '-d'))
    except AssertionError:
        raise ValueError('Bad command line argument: {}'.format(argv))

    win = app(argv)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main(sys.argv[1])
