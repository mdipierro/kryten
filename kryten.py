#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################
# created by Massimo Di Pierro
# this program takes its name from Kryten
# http://www.youtube.com/watch?v=CrUuuyg0Y54
# license: http://opensource.org/licenses/BSD-2-Clause
#
# Commands in shell:
#   SPACE execute and next line
#   q quit
#   p previous
#   n next without execue
#   x quickly execute and move to next line
# Commends in editor:
#   SPACE next line
#   UP, DOWN for moving highlited line
#   q quit
#   b previous
#   n next
#   s save partial
#   x quickly execute end exit
#   (i intrecative mode - not suported sorry)
##############################################################

QUOTE1 = """
##    ## ########  ##    ## ######## ######## ##    ## 
##   ##  ##     ##  ##  ##     ##    ##       ###   ## 
##  ##   ##     ##   ####      ##    ##       ####  ## 
#####    ########     ##       ##    ######   ## ## ## 
##  ##   ##   ##      ##       ##    ##       ##  #### 
##   ##  ##    ##     ##       ##    ##       ##   ### 
##    ## ##     ##    ##       ##    ######## ##    ##
> That's easy for you to say, Mr David, you're a human
"""

QUOTE2 = """
> Oh, it's not the end for me, sir, it's just the beginning.
> I have served my human masters, now I can look forward to my reward in silicon heaven. 
"""

DEMO = """
# the line below shoud print hello world
print 'hello world'

# the line below should print 'hello world'
echo 'hello world'

# the line below should print 'hello world'
$ echo 'hello world'

# the lines below should be hidden but print 'hello world'
% this line should be hidden

## title
### paragraph
#### subparagraph

@@SHELL@@
echo 'these are hidden shell commands'
@@END@@

@@PYTHON@@
print 'this is hidden python code'
@@END@@

@@TEXT@@
this will be markmin code to be used verbatim
@@END@@

@@READ@@
this text must be read aloud
@@END@@

@@UPDATE@@ test.test.py
print 'hello world'
@@END@@

quit
"""

import difflib
import time
import os
import sys
import logging
import types
import re
import optparse
import glob
import sys
import traceback
import cStringIO
import pickle
import subprocess
import math
import random
import readline
import rlcompleter
import curses
import time
import sys
import traceback
import termios
import shutil 
import fcntl
import struct

BORDER = 6
TEMPFILENAME = '/tmp/kryten.txt'
CORRECTIONS = {'web2py':'web-2-pie', 
               '(':', ',
               ')':', ',
               '@':' at ',
               '[':' of ',
               '+':' plus ',
               '-':' minus ',
               '_':' underscore ',
               '*':' times ', '/':' over ', '\\':' backslash ', '=':' equal ', '^':' to power ', '&':', and, ',
               ' sin ':' sign ',
               ' cos ':' cosign ',
               ' tan ':' tangent ',
               ' exp ':' exponential '}

regex_shell = re.compile('^[\w/]+\s*(?![,\=\[\(\:])')

def is_shell_command(command):
    PYCOMMANDS = ('for','if','def','class','elif','else','pass','try','except','finally','from','import','print','raise','del','while','with','lambda','and','or','conitnue','break','yield','as','assert','exec','is','global','not')
    if command[:1] in ('/','.','~','$'): return True
    return regex_shell.match(command) and not command.split(' ')[0] in PYCOMMANDS

def say(text):
    for key, value in CORRECTIONS.items(): text = text.replace(key,value)
    os.system('say "%s"' % text.replace('"','\\"').replace("'","\\'"))

def press_key():
    fd = sys.stdin.fileno()
    termios.tcflush(fd, termios.TCIFLUSH)
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    key = None
    try:
        key = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    return key

class Document:
    def __init__(self, screen, filename, options={}):
        self.filename = filename
        code = open(filename,'r').read()
        self.screen = screen
        self.lines = code.split('\n')+['']
        self.speak = options.speak
        self.delay = options.delay
        self.nonblock = options.nonblock
        self.highlight = 0
        self.before = 12
        self.history = []
        self.diff = []
    def save(self,filename=None):
        if not filename:
            filename = self.filename
        open(filename,'w').write('\n'.join(self.lines).strip())
    def up(self):
        self.moveto(self.highlight-1)
    def down(self):
        self.moveto(self.highlight+1)
    def pause(self,n=1):
        time.sleep(self.delay*random.random()*n)
    def revert(self):
        if len(self.history):
            command,r,old = self.history[-1]
            del self.history[-1]
            self.moveto(r)
            if command == 'delete_line':
                self.lines.insert(r,old)
            elif command == 'insert_line':
                del self.lines[r]
            else:
                self.lines[r] = old
            self.render()
    def insert_line(self,r,text):
        while len(self.lines)<r+1: self.lines.append('')
        self.history.append(('insert_line',r,self.lines[r]))
        self.moveto(r)
        self.lines.insert(r,'')
        self.type(r,0,text)
    def insert_text(self,r,c,text):
        while len(self.lines)<r+1: self.lines.append('')
        self.history.append(('insert_text',r,self.lines[r]))
        self.moveto(r)
        self.type(r,c,text)
    def type(self,r,c,text):
        for k,x in enumerate(text):
            line = self.lines[r]
            pre = line[:c+k]
            self.lines[r] = pre+' '*(c+k-len(pre))+x+line[c+k:]
            self.render()
            if text[:k].strip(): self.pause(2)
            if text[k]==' ': self.pause(2)
        if self.speak and text.lstrip()[:2]=='# ': say(text.lstrip()[2:])

    def delete_line(self,r):
        self.moveto(r)
        self.history.append(('delete_line',r,self.lines[r]))
        del self.lines[r]
        self.render()
    def delete_text(self,r,c,length):
        self.moveto(r)
        self.history.append(('delete_text',r,self.lines[r]))
        for i in range(length):
            line = self.lines[r]
            self.lines[r] = line[:c]+line[c+1:]
            self.render()
            self.pause(1)
    def moveto(self,r):
        r = max(0,min(r,len(self.lines)-1))
        while r>self.highlight:
            self.highlight+=1
            self.render()
            self.pause(1)
        while r<self.highlight:
            self.highlight-=1
            self.render()
            self.pause(1)
    def render(self):
        screen = self.screen
        screen.clear()
        ROWS, COLS = screen.getmaxyx()
        COLS = COLS - BORDER - 1
        ROWS = ROWS - 1
        header = 'File: %s | Row: %s | Step: %s/%s | Speed: %s' % \
            (self.filename, self.highlight, len(self.history), len(self.diff), self.delay)
        screen.addstr(0,0,header+' '*(BORDER+COLS-len(header)), curses.A_REVERSE)
        r = 1
        i = min(max(0,self.highlight + r - 1 - self.before),len(self.lines)-1)
        while r<ROWS and i<len(self.lines):
            k=0
            line = self.lines[i]
            while r<ROWS:
                if k==0:
                    label = ' '*(BORDER-len(str(i+1)))+str(i+1)
                    screen.addstr(r,0,label, curses.A_REVERSE)
                else:
                    screen.addstr(r,0,' '*BORDER, curses.A_REVERSE)
                if i==self.highlight:
                    screen.addstr(r,BORDER,line[:COLS-1],curses.A_BOLD)
                else:
                    screen.addstr(r,BORDER,line[:COLS-1])
                r=r+1
                if len(line)<=COLS: break
                line=line[COLS:]
                k=1
            i=i+1
        screen.refresh()

def compute_diff(output,input):
    lines1=open(output,'r').read().split('\n')
    lines2=open(input,'r').read().split('\n')
    diff = difflib.ndiff(lines1,lines2)
    commands=[]
    k=0
    for line in diff:
        if line.startswith(' '):
            k+=1
        elif line.startswith('-'):
            commands.append(('delete_line',k,0,line[2:]))
        elif line.startswith('+'):
            commands.append(('insert_line',k,0,line[2:]))
            k+=1
    return commands

def editor(options):
    output = options.output
    input = options.input or output
    if not os.path.exists(output):
        open(output,'w').write('')
    if input and not os.path.exists(input):
        open(input,'w').write('')
    diff = compute_diff(output,input)
    delay = options.delay
    nonblock = options.nonblock

    if delay>0 and nonblock: 
        time.sleep(min(delay*5,2))

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    save = True

    try:
        d=Document(screen, output, options=options)
        d.render()
        d.step = 0
        d.diff = diff
        while True:
            if nonblock:
                if d.step>=len(diff):
                    char=ord('x')
                else:
                    char = 32
            else:
                char = screen.getch()
            if char==curses.KEY_UP:
                d.up()
            elif char==curses.KEY_DOWN:
                d.down()
            elif (char==curses.KEY_RIGHT or char==32) and d.step<len(diff):
                command, r, c, text = diff[d.step]
                if command=='insert_line':
                    d.insert_line(r,text)
                elif command=='delete_line':
                    d.delete_line(r)
                elif command=='insert_text':
                    d.insert_text(r,c,text)
                elif command=='delete_text':
                    d.delete_text(r,c,int(text))
                d.step+=1
                # d.delete(random.randint(0,20),random.randint(0,20),10)
            elif char==curses.KEY_LEFT or char==ord('b'):
                d.revert()
                d.step=max(0,d.step-1)
            elif char==ord('+'):
                d.delay*=2
            elif char==ord('-'):
                d.delay/=2
            elif char==ord('n'):                
                d.delay=0
            elif char==ord('x'):
                break
            elif char==ord('q'):                
                save = False
                break
            elif char==ord('s'):
                if input!=output: d.save(output)

        if input!=output and save:
            shutil.copyfile(input,output)
    finally:
        if delay>0 and nonblock:
            time.sleep(max(delay*5,2))
        screen.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        curses.nl()


def fast_print(input, pad='     | '):
    input = str(input).strip()
    if not input: return
    for line in input.split('\n'):
        sys.stdout.write(pad+line+'\n')
        time.sleep(0.02)

def set_color(color):
    ansi_foreground = curses.tigetstr('setaf')
    if(ansi_foreground):
        code = getattr(curses, 'COLOR_%s' % color.upper())
        sys.stdout.write(curses.tparm(ansi_foreground, code))

def slow_print(prefix,postfix,options):
    if not postfix:
        sys.stdout.write('\n')
    else:
        for i in range(len(postfix)+1):
            if i>0: sys.stdout.write(curses.tigetstr('cuu1'))
            set_color('yellow')
            sys.stdout.write(prefix)
            if postfix[:2]=='# ': set_color('cyan')
            else: set_color('green')
            sys.stdout.write(postfix[:i]+'\n')
            time.sleep(options.delay*2*random.random())
            if not options.nonblock and postfix and i==0:
                press_key()
            if postfix[i:i+1]==' ':
                time.sleep(options.delay*2)
        set_color('black')
        if options.speak and postfix[:2]=='# ': say(postfix[2:])

def get_long_text(fileobj):
    code = ''
    while True:
        line = fileobj.readline()
        if line.startswith('@@END@@'): break
        else: code=code+line
    return code

def read_command(i,fileobj,options):
    command = ''
    multiline = False
    while True:        
        prompt = '%i' % i
        prompt = '.'*(5-len(prompt))+prompt+'> '
        if fileobj:
            new_line = fileobj.readline()
            if new_line == None:
                return '', 'quit'
            new_line = new_line.rstrip()
            postfix=new_line.replace('@@UPDATE@@','edit')
            if not postfix.startswith('@@') and not postfix.startswith('%'):                
                line_width = len(postfix) + len(prompt)
                (console_width, console_height) = getTerminalSize()
                print console_width, console_height
                h = '# ' if postfix.startswith('# ') else ''
                while line_width > console_width:
                    shift = console_width-len(prompt)-1
                    if postfix.startswith('`'):
                        slow_print(prompt,postfix[2:shift],options)
                    else:
                        slow_print(prompt,postfix[:shift],options)
                    postfix = h+postfix[shift:]
                    line_width -= shift
                if postfix.startswith('`'):
                    slow_print(prompt,postfix[2:],options)
                else:
                    slow_print(prompt,postfix,options)
            time.sleep(options.delay)            
        else:
            if not multiline:
                new_line = raw_input(prompt)
            else:
                new_line = raw_input('.'*len(prompt))
        spaces = len(new_line)-len(new_line.lstrip())
        if not new_line.strip():
            break
        if new_line.strip().endswith(':') or \
                new_line.strip().count('"""') % 2 == 1 or \
                new_line.strip().count("'''") % 2 == 1 or \
                new_line.strip().endswith(',') or \
                new_line.strip().endswith('\\'):
            multiline = True
        command = command +'\n'+new_line
        if not multiline:
            break
    if fileobj and command.strip() and not options.nonblock: 
        key = press_key()
    else:
        key = None
    return key, command.lstrip()

_env = {}

OS_COMMANDS = ['ls','rm','echo','mkdir','rmdir','find','open','say','cp','mv',
               'ssh','scp','ftp','grep','set','export','hg','diff','patch',
               'wget','curl','zip','unzip','tar','python','ps','kill','nohup','sudo','make']


def getTerminalSize():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])

def actor(command,code,history,options):
    try: meta,other= command.split(' ',1)
    except: meta, other = command, ''
    if meta=='#':
        pass
    elif meta=='`':
        pass
    elif meta=='quit' and not other.startswith('='):
        return False
    elif meta=='cd' and not other.startswith('='):
        os.chdir(other)        
    elif meta=='save' and not other.startswith('='):
        pass
    elif meta=='load' and not other.startswith('='):
        pass
    elif meta=='edit' and not other.startswith('='):
        raise RuntimeError
    elif meta=='commit' and not other.startswith('='):
        raise RuntimeError
    elif is_shell_command(command):
        ocommand = command
        if meta.startswith('$'): command=command[1:]
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        if not command.endswith('&'):
            output = proc.communicate()[0]
            history.append((ocommand,output))
            fast_print(output)
    elif meta=='@@SHELL@@':
        command = code
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        history.append((command,output))
    elif meta=='@@TEXT@@':
        pass
    elif meta=='@@READ@@':
        say(code)
    elif meta=='@@UPDATE@@':
        filename = other
        options.input = TEMPFILENAME
        open(options.input,'w').write(code)
        options.output = filename
        if sys.argv[0].startswith('/'):
            path = sys.argv[0]
        else:
            path = '%s/%s' % (options.path,sys.argv[0])
        os.system('%s -d %s %s %s -i %s -o %s' % (path,options.delay,
                                                  '-n' if options.nonblock else '',
                                                  '-s' if options.speak else '',
                                                  options.input,options.output))
    else:
        if meta == '@@PYTHON@@':
            command = code
        STDOUT = sys.stdout
        STDERR = sys.stderr
        sys.stdout = sys.stderr = cStringIO.StringIO()
        exec(command,_env)
        output = sys.stdout.getvalue()
        sys.stdout, sys.stderr = STDOUT, STDERR
        history.append((command,output))
        fast_print(output)
    return True


def typist(command,code,history,options):
    try: meta,other= command.split(' ',1)
    except: meta, other = command, ''
    if meta=='#':
        history.append(('#',other))
    elif meta=='quit' and not other.startswith('='):
        return False
    elif meta=='cd' and not other.startswith('='):
        os.chdir(other)
        history.append((command,''))
    elif meta=='save' and not other.startswith('='):
        if not other:
            other = raw_input('filename: ')
        pickle.dump(history,open(other+'.pickle','wb'))
        f = open(other+'.play','wb')
        for k in history:
            f.write(k[0]+'\n')
            if k[0].startswith('@@UPDATE@@ '):
                f.write(k[1]+'@@END@@\n\n')
            f.write('quit\n')
    elif meta=='load' and not other.startswith('='):
        history = pickle.dump(open(other,'wb'))
    elif meta=='edit' and not other.startswith('='):
        filename = command[5:]
        if not os.path.exists(filename):
            open(filename,'w').write('')
            os.system('emacs %s' % filename)
            lastfilename = filename
    elif meta=='commit' and not other.startswith('='):
        filename = command[7:]
        code = open(filename,'rb').read()
        history.append(('@@UPDATE@@ %s' % filename,code))
    elif is_shell_command(command):
        ocommand = command
        if meta.startswith('$'): command=command[1:]
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        if not command.endswith('&'):
            output = proc.communicate()[0]
            history.append((ocommand,output))
            fast_print(output)
    elif meta=='@@UPDATE@@':
        raise RuntimeError    
    else:
        if meta == '@@PYTHON@@':
            raise RuntimeError
            command = code
        STDOUT = sys.stdout
        STDERR = sys.stderr
        sys.stdout = sys.stderr = cStringIO.StringIO()
        exec(command,_env)
        output = sys.stdout.getvalue()
        sys.stdout, sys.stderr = STDOUT, STDERR        
        history.append((command,output))
        fast_print(output)
    return True

def actor_markmin(command,code,history,options):
    # this needs work
    if command.startswith('%'):
        pass
    elif command.startswith('#'):
        options.markmin_file.write(command[1:]+'\n')
    elif command=='quit':
        return False
    elif code:
        if command.startswith('@@TEXT@@'):
            options.markmin_file.write(code+'\n\n')
        if command.startswith('@@READ@@'):
            options.markmin_file.write(code+'\n\n')
        if command.startswith('@@UPDATE@@'):
            options.markmin_file.write('\nFILE: %s\n' % other)
            options.markmin_file.write('``\n%s\n``\n\n' % code.strip())
    elif is_shell_command(command):
        options.markmin_file.write('``\n$ %s\n``:shell\n\n' % command)
    else:
        options.markmin_file.write('``\n%s\n``:python\n\n' % command)
    return True

class Lines:
    def __init__(self,filename):
        self.lines = open(filename,'rb').readlines()
        self.i = 0 
        self.history = []
    def readline(self):
        if self.i>=len(self.lines):
            return None
        self.i += 1
        return self.lines[self.i-1]


def play(options,actor=actor):
    curses.setupterm()
    options.path = os.getcwd()
    filename = options.play
    delay = options.delay
    nonblock = options.nonblock
    i=0
    counters = {}
    history = []
    STDOUT = sys.stdout
    STDERR = sys.stderr
    if not filename: #interactive
        readline.set_completer(rlcompleter.Completer(_env).complete)
        readline.parse_and_bind('tab:complete')
        fileobj=None
    else:
        fileobj=Lines(filename)
    while True:
        try:
            # key, command = None, None # in case error below
            key, command = read_command(i,fileobj,options)
            code = ''
            if command == None:
                break
            elif command:
                i+=1
            if delay != options.delay:
                options.delay = delay
            if not command.strip() or command.lstrip().startswith('## '):
                continue
            elif command.startswith('@@'):
                code = get_long_text(fileobj)            
            if not actor(command,code,history,options):
                break
        except KeyboardInterrupt:
            sys.stdout, sys.stderr = STDOUT, STDERR
            if raw_input('\n\nkill kryten (y/n)?')[0].lower()=='y':
                if not options.input: print QUOTE2
                sys.exit(0)
        except EOFError:
            sys.stdout.write('\n')
            sys.stdout, sys.stderr = STDOUT, STDERR
        except:
            sys.stdout, sys.stderr = STDOUT, STDERR
            set_color('red')
            input = traceback.format_exc()            
            if command: history.append((command,input))
            fast_print(input)
            set_color('white')
            if options.debug: press_key()

def main():
    usage = '''
    play                              (record mode)"
    play [options] -p filename.play   (playback mode)"
    play [options] -i input -o output (editor mode)"
    '''
    version= "0.1"
    parser = optparse.OptionParser(usage, None, optparse.Option, version)

    parser.add_option("-n", "--nonblock", dest="nonblock",default=False,
                      action='store_true',
                      help="do not ask for intput")

    parser.add_option("-d", "--delay", dest="delay",default='0.05',
                      help="typing delay")

    parser.add_option("-p", "--play", dest="play",default=None,
                      help="file to play (play mode)")

    parser.add_option("-i", "--input", dest="input",default=None,
                      help="input file (editor mode)")

    parser.add_option("-o", "--output", dest="output",default=None,
                      help="output file (editor mode)")

    parser.add_option("-s", "--speak", dest="speak",default=False, action="store_true",
                      help="read comments, mac only")

    parser.add_option("-D", "--debug", dest="debug",default=False, action="store_true",
                      help="stops on tracbacks")
    
    parser.add_option("-m", "--markmin", dest="markmin",default=None,
                      help="saves markmin output")

    (options, args) = parser.parse_args()
    options.delay=float(options.delay) # important!
    if not options.input: print QUOTE1
    if options.output:
        editor(options)
    elif options.markmin:
        options.markmin_file = open(options.markmin,'w')
        play(options,actor_markmin)
    elif options.play:
        play(options,actor)
    else:
        play(options,typist)

if __name__=='__main__':
    main()


