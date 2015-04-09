#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author: mawenbao@hotmail.com
# @date: 2014-09-03
# @depends: python2.7+

'''
从搜狗词库中提取中文词组

参考[这篇文章](http://blog.csdn.net/zhangzhenhu/article/details/7014271)中的代码实现。

搜狗词库文件使用小端序，采用UTF-16编码，词组列表从0x2628处开始直到文件结尾。

'''

import argparse
import struct
import codecs

# check python version
import sys
if sys.version_info.major == 2:
    range = xrange

gWordsOffset = 0x2628 # 词组列表的偏移地址

def extract_sougou_words(data):
    '''提取中文词组

    每个列表元素包括一组同音词，格式如下：
        (<同音词数量(2字节)>
        <拼音表长度(2字节)>
        <拼音表>
        [
            (<同音词长度(2字节)><同音词(UTF-16编码)><扩展信息长度(2字节)><扩展信息>),
            ...
        ]),
    '''
    offset = 0
    dataLen = len(data)
    wordList = []

    while offset < dataLen:
        numTongYinCi, pinYinTableLen = struct.unpack('<HH', data[offset:offset+4])
        offset += (4 + pinYinTableLen)

        for i in range(numTongYinCi):
            wordLen = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            word = struct.unpack('<' + str(wordLen) + 's', data[offset:offset+wordLen])[0]
            offset += wordLen
            wordList.append(word.decode('UTF-16'))
            extInfoLen = struct.unpack('<H', data[offset:offset+2])[0]
            offset += (2 + extInfoLen)
    return wordList

def extract_sougou_dict_files(pathList):
    '''
    从多个搜狗词库文件中提取中文词组，并合并重复的词组。
    '''
    wordSet = set()
    for path in pathList:
        with open(path, 'rb') as f:
            wordSet.update(extract_sougou_words(f.read()[gWordsOffset:]))
    return wordSet

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description=u'从搜狗词库中提取中文词组，如果输入文件不止一个，重复的词组会被合并。')
    argParser.add_argument('dictfile', nargs='+', help=u'搜狗词库文件的路径，可以有多个')
    argParser.add_argument('-o', dest='output', required=True, help=u'输出文件的路径，默认情况下每个词组占一行')
    argParser.add_argument('-mmseg', dest='mmseg', action='store_true', help=u'按libmmseg字典文件的格式生成输出文件')
    args = argParser.parse_args()
    
    wordSet = extract_sougou_dict_files(args.dictfile)
    with codecs.open(args.output, 'w', encoding='UTF-8') as f:
        if not args.mmseg:
            f.write(u'\n'.join(wordSet))
        else:
            for word in wordSet:
                f.write(u'{}\t1\nx:1\n'.format(word))
    print(u'成功从{}个搜狗词库中提取出{}个词组  =>  {}'.format(len(args.dictfile), len(wordSet), args.output))
