#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversor universal do Reino de Deus (curd)

Copyleft (CC) 2007 Fernando Henrique R Silva

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Autores: liquuid - pontape inicial
     nighto  - alinhamento geral

"""



#
# Declaracao dos headers usados pelo programa
#

# pygtk usado para desenhar a gui do programa
import gtk

#idem
import gobject

import os 
# imagem da flechinha
from flecha import *

# Lista com os formatos compativeis
from formatos import *


# Variaveis globais usadas no sistema de drag n drop
TARGET_STRING = 0
TARGET_ROOTWIN = 1

target = [
   ('STRING', 0, TARGET_STRING),
   ('text/plain', 0, TARGET_STRING),
   ('application/x-rootwin-drop', 0, TARGET_ROOTWIN)
]
# Funcao para desenhar imagens usando codigo xpm

def create_pixmap(widget, xpm_data):
   return \
       gtk.gdk.pixmap_colormap_create_from_xpm_d(
           None, widget.get_colormap(), None, xpm_data)


# Classe principal do programa

class Curd(gtk.Window):
    flecha_xpm = None
    flecha_xpm_mask = None
    have_drag = False
    popped_up = False
    in_popup = False
    popup_timer = 0
    popdown_timer = 0
    popup_win = None


    def __init__(self, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        
        # cria janela principal e suas divisoes para os widgets

        table = gtk.Table(2,3)
        self.set_resizable(False)
        self.add(table)
        # desenha flecha
        self.flecha, self.flecha_mask = \
            create_pixmap(self, flecha_xpm)
        self.filein = ''
        # Define imagem da flechinha que ficara dentro da caixa sensivel ao drag n drop
        image = gtk.Image()
        image.set_from_pixmap(self.flecha, self.flecha_mask)
        image.drag_dest_set(0, [], 2)
        table.attach(image, 0, 2, 0, 1)

        # Conecta as funcoes da imagem e dnd a acoes

        image.connect('drag_leave', self.target_drag_leave)
        image.connect('drag_motion', self.target_drag_motion)
        image.connect('drag_drop', self.target_drag_drop)
        image.connect('drag_data_received', self.target_drag_data_received)

        # Combo box para os formatos !

        menu = gtk.combo_box_new_text()
        menu.set_wrap_width(1)

        for item in formatos:
                menu.append_text(item)

        menu.set_active(0)
        menu.connect('changed', self.get_active_text)
        self.codec  = menu.get_active_text()
        table.attach(menu,0 , 1 , 1, 2)

        # desenha botao "Converte"

        self.b = gtk.Button("Converte")
        # Conecta botao a uma acao ... afinal queremos que ele faca alguma coisa

        self.b.connect_object("clicked", self.converte, self.window)
        # Gruda o botao na janela
        table.attach(self.b, 1 , 2 , 1 , 2)

        # Caixa com opcoes extras alem das jah existentes nos presets

        expander = gtk.Expander("Opcoes avancadas")
        table.attach(expander, 0, 2, 2, 3)
        content = gtk.Label('"Ele pediu pro sr. Jesus ajudar ele ali naquela hora porque ele sabia que era uma peleja travada."')
        expander.add(content)

        # titulo da janela

        self.set_title("curd 0.03a")
        # borda entre os widgets e a borda da janela
        self.set_border_width(10)
        # Desenha tudo...

        self.show_all()

    def converte(self,nome):
        # Ajuste fino das opcoes a partir do item selecionado do menu
        cformat = formatos[self.codec]

        ### Backend: ffmpeg
        if cformat == '3gp':
            formato = cformat
            screen_size = '176x144'
            ext = formato
            backend = "ffmpeg"

        elif cformat == 'pal-dv':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'pal-dvd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'pal-vcd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'pal-svcd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'ntsc-dv':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'ntsc-dvd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'ntsc-vcd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'ntsc-svcd':
            backend = "ffmpeg"
            target = cformat
        elif cformat == 'flvmpg':
            backend = "ffmpeg"
            audiobitrate = "56"
            audiofrequency = "22050"
            videobitrate = "500"
            screen_size = "320x240"

        ### Backend: transcode
        elif cformat == 'mov':
            psw = '--uyvy'  ## psw = pre-first switch, antes do input
            ssw = '-F yv12' ## depois seria interessante setar estes parametros especificos com alguma logica
            tsw = '-r 2'    ## eu nao faco ideia da funcao deles, so sei que sao necessarios para o PDP.
            ext = "mov"
            backend = "transcode"

        ### Backend: maluco
        else:
            cformat = "deconhecido"
            fsw = "nulo"
            ext = "null"


        ### Determinando flags
        if backend == "ffmpeg":
            backend = backend+" -y"
            inputflag = "-i"
            try:
                if ext:
                    pass
            except NameError:
                ext = "mpeg"
        elif backend == "transcode":
            inputflag = "-i"
            outputflag = "-o"
        elif backend == "mencoder":
            outputflag = "-o"

        comando = []
        comando.append(backend)
        try:
            if psw:
                comando.append(psw)
        except NameError:
            pass
        try:
            if inputflag:
                comando.append(inputflag)
        except NameError:
            pass
        # TODO: Se o arquivo tiver ' ', ele le como '%20' e da pau. '-' tambm. Alguma ideia?
        comando.append(self.filein.split('\r')[0])
        try:
            if formato:
                if backend == "ffmpeg":
                    comando.append("-f")
                comando.append(formato)
        except NameError:
            pass
        try:
            if target:
                comando.append("-target")
            comando.append(target)
        except NameError:
            pass
        try:
               if audiobitrate:
                       if backend == "ffmpeg":
                               comando.append("-ab")
                       comando.append(audiobitrate)
        except NameError:
            pass
        try:
            if audiofrequency:
                if backend == "ffmpeg":
                    comando.append("-ar")
                comando.append(audiofrequency)
        except NameError:
            pass
        try:
            if videobitrate:
                if backend == "ffmpeg":
                    comando.append("-b")
                comando.append(videobitrate)
        except NameError:
            pass
        try:
            if screen_size:
                if backend == "ffmpeg":
                    comando.append("-s")
                comando.append(screen_size)
        except NameError:
            pass
        try:
            if outputflag:
                comando.append(outputflag)
        except NameError:
            pass

        # TODO: Seria interessante tirar a extensao original
        comando.append(self.filein.split('\r')[0]+"."+ext)
        try:
            if ssw:
                comando.append(ssw)
        except NameError:
            pass
        try:
            if tsw:
                comando.append(tsw)
        except NameError:
            pass

        # os.system é mais simples de lidar, e permite que eu faça fork do ffmpeg , assim não trava
        # a interface durante a conversao e pode ser o ponta-pe inicial para uma barra de progresso

        scomando = " ".join(comando)
        print scomando
        os.system(scomando+" &")
        # nao tenho a manha com o subprocess :(

        #saida = subprocess.Popen(comando, stdout=subprocess.PIPE).communicate()[0]
        #print saida


    def get_active_text(self, menu):
        print menu.get_active_text()
        self.codec = menu.get_active_text()
        return menu.get_active_text()

# Funcoes drag n drop tiradas dos exemplos do tutorial oficial pygtk

    def label_drag_data_received(self, w, context, x, y, data, info, time):
       if data and data.format == 8:
           print 'Recebido \n "%s"' % data
           context.finish(True, False, time)
       else:
           context.finish(False, False, time)

    def popsite_motion(self, w, context, x, y, time):
       if not self.popup_timer:
           self.popup_timer = gobject.timeout_add(500, self.popup_cb)
       return True

    def popsite_leave(self, w, context, time):
       if self.popup_timer:
           gobject.source_remove(self.popup_timer)
           self.popup_timer = 0

    def popup_motion(self, w, context, x, y, time):
       print 'popup_motion'
       if not self.in_popup:
           self.in_popup = True
           if self.popdown_timer:
               print 'removed popdown'
               gobject.source_remove(self.popdown_timer)
               self.popdown_timer = 0
       return True

    def popup_leave(self, w, context, time):
       print 'popup_leave'
       if self.in_popup:
           self.in_popup = False
           if not self.popdown_timer:
               print 'added popdown'
               self.popdown_timer = gobject.timeout_add(500, self.popdown_cb)

    def popup_cb(self):
       if not self.popped_up:
           if self.popup_win is None:
               self.popup_win = gtk.Window(gtk.WINDOW_POPUP)
               self.popup_win.set_position(gtk.WIN_POS_MOUSE)
               table = gtk.Table(3, 3)
               for k in range(9):
                   i, j = divmod(k, 3)
                   b = gtk.Button("%d,%d" % (i,j))
                   b.drag_dest_set(gtk.DEST_DEFAULT_ALL, target[:-1],
                       gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
                   b.connect('drag_motion', self.popup_motion)
                   b.connect('drag_leave', self.popup_leave)
                   table.attach(b, i, i+1, j, j+1)
               table.show_all()
               self.popup_win.add(table)
           self.popup_win.present()
           self.popped_up = True
       self.popdown_timer = gobject.timeout_add(500, self.popdown_cb)
       print 'added popdown'
       self.popup_timer = 0
       return False

    def popdown_cb(self):
       print 'popdown'
       #if self.in_popup:
       #    return True
       self.popdown_timer = 0
       self.popup_win.hide()
       self.popped_up = False
       return False

    def target_drag_leave(self, img, context, time):
       print 'leave'
       self.have_drag = False
       img.set_from_pixmap(self.flecha, self.flecha_mask)

    def target_drag_motion(self, img, context, x, y, time):
       if self.have_drag is False:
           self.have_drag = True
           img.set_from_pixmap(self.flecha, self.flecha_mask)
       source_widget = context.get_source_widget()
    #       print 'motion, source ',
    #        if source_widget:
    #            print source_widget.__class__.__name__
    #        else:
    #           print 'unknown'
       context.drag_status(context.suggested_action, time)
       return True

    def target_drag_drop(self, img, context, x, y, time):
       print 'drop'
       self.have_drag = False
       img.set_from_pixmap(self.flecha, self.flecha_mask)
       if context.targets:
           img.drag_get_data(context, context.targets[0], time)
           return True
       return False

    def target_drag_data_received(self, img, context, x, y, data, info, time):
       if data.format == 8:
           self.filein = data.data
           context.finish(True, False, time)
       else:
           context.finish(False, False, time)

    def source_drag_data_get(self, btn, context, selection_data, info, time):
       if info == TARGET_ROOTWIN:
           print 'I was dropped on the rootwin'
       else:
           selection_data.set(selection_data.target, 8, "I'm Data!")

    def source_drag_data_delete(self, btn, context, data):
       print 'Delete the data!'

def main():
    Curd()
    gtk.main()

if __name__ == '__main__':
    main()
