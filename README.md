````
##    ## ########  ##    ## ######## ######## ##    ## 
##   ##  ##     ##  ##  ##     ##    ##       ###   ## 
##  ##   ##     ##   ####      ##    ##       ####  ## 
#####    ########     ##       ##    ######   ## ## ## 
##  ##   ##   ##      ##       ##    ##       ##  #### 
##   ##  ##    ##     ##       ##    ##       ##   ### 
##    ## ##     ##    ##       ##    ######## ##    ##
> That's easy for you to say, Mr David, you're a human
````

## What is Kryten?

[Here](http://vimeo.com/20743963) is a presentation made with Kryten.

Kryten is Unix Shell tool that makes terminal-based presentations a snap to write, present, and share.

Kryten takes it's name from Kryten of the British television series [Red Dwarf](http://en.wikipedia.org/wiki/Red_Dwarf)

![Kryten](http://homepages.nildram.co.uk/~polymorp/txt/kryten.gif)

## Why Kryten?

Kryten allows presenters to focus on the presentation without having to type code. It types the code for you and runs it. With Kryten, you present live code demos from prewritten presentation files. Write the presentation beforehand, and play it, step-by-step with Kryten. You can pause the presentation at any time, play backwards, and forward. It also edit files for you using a built-in editor.

When running on Mac, Kryten has the ability of reading comments in the code using text-to-speech. 
This allows turning a code into a video tutorial without human intervention.

## Installing Kryten  
	
    pip install kryten

or download [kryten.py](https://github.com/mdipierro/kryten/blob/master/kryten.py) from this repo.
	

## Usage

### Writing a presentation

Kryten works with .play files.

**Syntax**

Start comments with a #

Mark file edits with `@@UPDATE@@ path.to/file.ext`, followed by the new file contents, ending with `@@END@@`.

Try an play an existing file:

    >>> python kryten.py -d 0.05 -n -p python101.play

**A simple example**

This example presentation presents a couple Python loops.
    
`python.play`

```
# a simple loop
for i in range(5):
    print i

# another loop
for i in range(5):
    for j in range(3):
        print i+j

# print something
print 'hello world'

quit
```

**Example with file edits**

Kryten uses diff comparison to update files on the system. Use `@@UPDATE@@ path.to/file` to start a file edit block. Write how the file should look post-edit and end with `@@END@@`.

`file_edit.play`

```
# create a file

@@UPDATE@@ file_edit.txt
a sample presentation
@@END@@

# update the file

@@UPDATE@@ file_edit.txt
a sample presentation
with another line
@@END@@

quit
```

### Playing a presentation

To load a presentation, use the -p[lay] argument to pass in a .play file.

## Command Line arguments:

In addition to the standard -p[lay] argument, there a few more advanced arguemnts to be used during the initialization of a presentation.

-h[help]
-n[onblock]  
-d[elay]  
-i[nput]  
-o[utput]  
-s[peak]  
-d[ebug]  
-m[arkmin]

## Interactive Commands

__Commands in shell:__  
SPACE execute and move to next line  
q quit  
p previous  
n next without execue  
x quickly execute and move to next line  

__Commands in editor:__  
SPACE next line  
UP, DOWN for moving highlited line  
q quit  
b previous  
n next  
s save partial  
x quickly execute end exit  
(i intrecative mode - not yet suported sorry)
	
## License

Copyright © 2012 Massimo DiPierro.  
Licensed under the BSD license.
<http://opensource.org/licenses/BSD-2-Clause>

## Thanks

Thanks for Devon Blandin for help with the docs and text alignment. 