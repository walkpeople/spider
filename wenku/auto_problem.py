#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 user <user@user-pc>
#
# Distributed under terms of the MIT license.

"""

"""

import urllib.request
import gzip
import io
from bs4 import BeautifulSoup
import re
import json
import itchat
import logging
import time
from  itchat.content import * 



jsList = []

def get_url(url):

    global add,Doc
    headers = """
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    Accept-Encoding: gzip, deflate, br
    """
    headers_dict = parse_header(headers)
    request = urllib.request.Request(url,headers=headers_dict)
    reponse = urllib.request.urlopen(request)
    text = reponse.read()
    
    for header in reponse.getheaders():
        print(header)

    #处理压缩后的页面
    byte_html = io.BytesIO(text)
    gzip_result = gzip.GzipFile(fileobj=byte_html)
    html_result = gzip_result.read()

    text =  html_result.decode('gbk')
    
    #保存结果 非必要
    with open('wenku.html','w') as f:
        f.write(text)

    #分析文档
    soup = BeautifulSoup(text,'lxml')
    #print('编码测试'+str(soup.title))   

    script = soup.find_all('script',attrs={'type':'text/javascript'})
    for i in script:
        if 'WkInfo.htmlUrls' in i.text:
            add = i.text
        if 'WkInfo.Urls' in i.text:
            Doc = i.text
 #           print(itext.split('WkInfo.DocInfo=')[0])
    docInfo = Doc.split('WkInfo.DocInfo=')[0]
    doctype = re.findall(r'\'docType\':\s\'(.*)\'',docInfo)[0]
    title = re.findall(r'\'title\':\s\'(.*)\'',docInfo)[0]
    docId = re.findall(r'\'docId\':\s\'(.*)\'',docInfo)[0]
    
    print('即将获取文章-->'+title)
    print('获取的文章类型是-->'+doctype)
    
    if doctype == 'doc' or doctype == 'txt':
        parserDoc(add,title)


    
# 获取文章
def parserDoc(add,file_name):
    add=add.split(' WkInfo.htmlUrls =')[1].split(';')[0] 
    add = add.replace('\\x22','').replace('\\','')
    add = re.findall(r'pageLoadUrl:.*\W',add)[0].split(',')
    
    #创建txt存储文件
    file = open(file_name+'.txt','w')
    file.close()

    for j in add:
        if 'json' in j:
            jsList.append(j.split(':',1)[1].replace('}','').strip(']'))
        
    print('一共有 %d 页'% len(jsList))
    for i in jsList:
        r = urllib.request.urlopen(i.replace('\\',''))
        result = json.loads(r.read().decode('utf-8').split('(',1)[1].strip(')'))
        body = result['body']

        for i in body:
            if i['t'] == 'word':
                text = i['c']

                if i['ps'] != None and '_enter' in i['ps'].keys():
                    text = '\n'
                
                print(text, end='')
                with open(file_name+'.txt','a+') as f:
                    f.write(str(text))
            

"""
    格式化请求头
    将str转换dictionary
"""
def parse_header(headers):
    he_list = headers.split('\n')[1:-1]
    he_dict = {}
    for he in he_list:
        he_single = he.strip()
        he_dict[he_single.split(':')[0]] = he_single.split(':')[1]

    for key in he_dict.keys():
        he_dict[key] = he_dict[key].strip()

    print(he_dict)

    return he_dict


"""
    提取问题 

"""
def get_question(file_name):
    question_list = []
    with open(file_name,'r') as f:
        while(True):
            text = f.readline()
            if(text):
                 question_list.append(text)
            else:
                 break
    return question_list 




"""
    itchat 注册器
"""
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING, SYSTEM],isMpChat=True)
def reply(msg):
    #logging.warning('来自'+str(msg['FromUserName']))
    
    #print('Msgstr(msg['MsgType']))
    text = msg['Content']
    if not re.search(r"href=\"https",str(text)):
        print('获取答案'+str(msg['Content']).replace('<a href=\"\"></a>',''))
    


def it_solve(file_name):
   # 尔雅答案说  @2b2b80d6b29de21c7fd852491193fb64
    itchat.auto_login(hotReload=True)
    question_list = get_question(file_name)
    mp_name = itchat.search_mps(name='尔雅答案说')
    user = re.findall(r'\'UserName\':\s\'(@[a-z|0-9]*)\'', str(mp_name))[0]
    print("获得公众号ID %s"%user)
    print('开始模拟答题')
    for i in question_list:
        time.sleep(1)
        print('发送题目: %s'%str(i))
        itchat.send_msg(msg=str(i), toUserName=str(user))
    itchat.run()


if __name__ == '__main__':
    
  #  url = input('输入网址:')
    #url = 'https://wenku.baidu.com/view/5c6c96c8227916888586d782.html'
    #get_url(url)
    file_name = 'question.bak'
    it_solve(file_name)

        
    

