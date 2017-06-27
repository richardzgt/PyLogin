# -*- set coding:utf-8 -*-
'''
Created on 2014��6��19��

@author: Administrator
'''
import sys

def GoodPrint(args):
    content = []
    mylen2 = []
    conjust = ''
    maxlen1 = 0
    maxlen2 = 0
    maxlenlist = []
    ilist = [ [] for i in range(len(args))]
    
    #将元祖转化为list类型，形成content二维数组,并且根据空格每一个字符串都是子列表的项
    for i,char in enumerate(args):      
        if isinstance(char,(tuple,list)):
            ilist[i]=char
        elif isinstance(char,str):
            ilist[i]=char.split()
        else:
            sys.exit()    
            
        content.append(ilist[i])
        
        #取得最大子列表的长度
        if maxlen1 > len(ilist[i]):
            pass
        else:
            maxlen1 = len(ilist[i])
    
#    print content,maxlen1,'maxlen'

    
    #取得最大的字符串长度
    for n2 in range(maxlen1):
        for n1 in range(len(content)):
            try:
                if maxlen2 > len(str(content[n1][n2])):
                    pass
                else:
                    maxlen2 = len(str(content[n1][n2]))
            except IndexError:
                pass
            
        maxlenlist.append(maxlen2)
            
#    print maxlenlist,'maxlenlenlist'
    
    for y1 in range(len(content)):
        for y2 in range(maxlen1):
            try:
                conjust +=  str(content[y1][y2]) + ' '*(maxlenlist[y2]+2-len(str(content[y1][y2])))
            except IndexError:
                pass
        conjust += '\n'
    
    print conjust

def Align(filename):
    with open(filename) as f:
        words = {}
        for i in f:
            linelist = i.split()
            linelen=len(linelist)
            for j in range(linelen):
                wordlen = len(linelist[j])
                if j not in words:
                    words[j] = wordlen
                elif words[j] < wordlen:
                    words[j] = wordlen
        f.seek(0)
        lineslen = len(f.readlines())
        f.seek(0)
        b = 1
        while b < lineslen+1:
            tjust = ''
            fn = f.readline().strip().split()
            wordlen = len(fn)
            for i in range(wordlen):
                tjust += fn[i].ljust(words[i]+1)
            print tjust
            b += 1
    

if __name__ == '__main__':
    
    file='D:\jee-kepler\workspace\PythonLearn\Project\PyLogin\z1.txt'
    
    with open(file) as fobj:
        lines = fobj.readlines()
        GoodPrint(lines)
    
    #阴风做的
#    Align(raw_input("enter a file of full path: ").replace('\\','\\\\'))
    
    

    