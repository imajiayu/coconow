import os
import json
def walkTree(path,id):
    res = []
    childs = os.listdir(path)
    dirs = []
    files = []
    for child in childs:
        subpath = os.path.join(path,child)
        assert subpath[:5] == "/home"
        if os.path.isdir(subpath):
            s = {'id':id,'label':child,'isopen':False,'path':subpath[5:]}
            id += 1
            s['children'],id = walkTree(subpath,id)
            res.append(s)
        else :
            s = {'id':id,'label':child,'path':subpath[5:]}
            id +=1
            res.append(s)
            
    res.sort(key=lambda x:(not x.has_key('isopen'),x['label']))
    return res,id

res,id = walkTree('/home',1)
print(json.dumps(res))