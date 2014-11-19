#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author: mawenbao@hotmail.com
# @date: 2014-09-03

'''
将两个libmmseg中文词典合并为一个。
'''

import argparse
from itertools import imap, ifilter

def parse_mmseg_dict(dictPath):
    with open(dictPath, 'r') as f:
        return set(imap(lambda x: x.strip(), ifilter(lambda x: x.strip()[0] != 'x', f)))

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description=u'合并libmmseg中文字典文件，不检查词典文件格式。')
    argParser.add_argument('-a', dest='mainDict', required=True, help=u'mmseg主词典的路径，如果合并时有重复词组，则以主词典为准')
    argParser.add_argument('-b', dest='secondDict', required=True, help=u'被合并mmseg词典的路径')
    argParser.add_argument('-o', dest='output', required=True, help=u'输出文件的路径')
    args = argParser.parse_args()

    mainWordSet = parse_mmseg_dict(args.mainDict)
    mainWordSetLen = len(mainWordSet)
    secondWordSet = parse_mmseg_dict(args.secondDict)
    secondWordSetLen = len(secondWordSet)

    mainWordSet.update(secondWordSet)
    numMergedWords = len(mainWordSet)
    numOmittedWords = mainWordSetLen + secondWordSetLen - numMergedWords

    with open(args.output, 'w') as f:
        for word in mainWordSet:
            f.write('{}\nx:1\n'.format(word))
    print(u'成功合并2个词典文件 {}({}) + {}({}) =>  {}({})'.format(
        args.mainDict, mainWordSetLen, args.secondDict, secondWordSetLen, args.output, numMergedWords))
    if (0 != numOmittedWords):
        print('{}中的{}个重复词组被忽略'.format(args.secondDict, numOmittedWords))