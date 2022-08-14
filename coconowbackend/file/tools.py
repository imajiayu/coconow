from click import command
from accounts.models import Project
from coconow.settings import TEMP_EDITFILE_PATH
import os
from django.test import TestCase

def dockeropen(pid,path):
    dockername=Project.objects.get(id=pid).pname
    filename=tmppath(pid,path)
    command='docker cp '+dockername+':/home'+path+' '+filename
    os.system(command)
    # print(filename)
    print(command)
    return filename

def dockersave(pid,path):
    dockername=Project.objects.get(id=pid).pname
    filename=tmppath(pid,path)
    command='docker cp '+filename+' '+dockername+':/home'+path
    os.system(command)
    # print(filename)
    print(command)

def removetmp(pid,path):
    filename=tmppath(pid,path)
    command='rm -f '+filename
    os.system(command)
    print(command)

def tmppath(pid,path):
    return os.path.join(TEMP_EDITFILE_PATH,(str(pid)+str(path).replace('/','_')))