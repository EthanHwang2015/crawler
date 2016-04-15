#encoding=utf8
'''
Created on 2016年4月13日

@author: yongsheng.huang
'''
import os
import re
from bs4 import BeautifulSoup
import multiprocessing
import traceback
import time

class WriteBuf:
    def __init__(self, outputFile):
        self.outputFile = outputFile
        self.buffer = []
        self.maxSize = 1024
        
    def putBuf(self, msg):
        self.buffer.append(msg)
        if len(self.buffer) > self.maxSize:
            self.appendBufToFile()
            self.buffer = []
    def appendBufToFile(self):
        if self.empty():
            return
        writeContent = ""
        for line in self.buffer:
            writeContent += line
        with open(self.outputFile, "a") as output:
                output.write(writeContent)
    def empty(self):
        return len(self.outputFile) == 0

def extractYx129(html, keywords, prefix, writeBufer):
    with open(html) as doc:
        soup = BeautifulSoup(doc, from_encoding='utf8')
        #print soup.prettify()
        '''
        for li in soup.find('div', 'binglContent').ul.find_all('li'):
                print li.span.string
                break
        '''
        content = prefix
        for keyword in keywords:
            span = soup.find('span', text=re.compile(keyword))
            if span is not None:
                content += '\001' + span.find_parent().p.string.strip().replace('\n', '')
                
        if content != prefix:
            #print content
            if writeBufer is not None and not writeBufer.empty():
                writeBufer.putBuf('\n'+content.encode('utf8'))
            else:
                print content

def multiRun(inputPath, inputFiles, keywords, outputFile):
    for html in inputFiles:
        #print html
        prefix = html.split('.')[0]
        try:
            extractYx129(inputPath+"/"+html, keywords, prefix, outputFile)
        except:
            print traceback.format_exception()
                       
def mainExtractYx129():                
    keywords=[u'医学检查', u'现在病史']
    path = u"E:/项目/医疗/内容提取/yx_data/data/"
    outputFile = u'E:/项目/医疗/内容提取/yx_data/output'
    files = []
    for f in  os.listdir(path):
        files.append(f)
    fileMap = {}
    workNum = 5
    writeBufers = []
    for i in range(workNum):
        fileMap[i] = []
        writeBufers.append(WriteBuf(outputFile+str(i)))
    for i in range(len(files)):
        fileMap[i%workNum].append(files[i])
    pool = multiprocessing.Pool(processes=workNum)
    for i in range(workNum):
        pool.apply_async(func=multiRun, args=(path, fileMap[i], keywords, writeBufers[i], ))
    pool.close()
    pool.join() 
    
def debugYx129():
    keywords=[u'医学检查', u'现在病史']
    path = u"E:/项目/医疗/内容提取/yx_data/data/"
    case = '10047.html'
    prefix = case.split('.')[0]
    extractYx129(path+case, keywords, prefix, None)
 
class BaiduSearchPage:
    def __init__(self):
        pass
        
    def extractTerm(self, html):
        '''
         #提取title和abstract中飘红的词
         #输出格式： term1 \002 term2 \002 term3 ...

        '''
        terms = set()
        validTag = ['a', 'div', 'p']
        with open(html) as doc:
            soup = BeautifulSoup(doc, from_encoding='utf8')
            for em in soup.find_all('em'):
                if em.find_parent().name in validTag:
                    '''
                    if em.em is None:
                        terms.add(em.string)
                    else :
                        #处理特性结果
                        term = em.get_text()
                        """
                        for child in em.children:
                            if child.name == 'em':
                                term += child.string
                        """
                        if len(term) > 0:
                            terms.add(term)    
                    '''
                    txt = em.get_text()
                    if txt is not None:
                        terms.add(txt)                        
        return terms    
            
    def testExtractTerm(self):
        name = u'胸闷_0'
        path = u'E:/项目/医疗/内容提取/直肠癌/'
        inputPath = path + 'input/'
        for term in self.extractTerm(inputPath + name):
            print term
        
    
    def extractTitleAbstract(self, html):
        '''
        #提取title和摘要
        #输出格式： title \001 abstract
        #百度知道  op_zhidaokv_answers
        #百度百科  op-medbaike-summary
        #自然结果  c-abstract
        #百度健康问答  wenda-content
        '''
        abstractTag = ['op_zhidaokv_answers', 'op-medbaike-summary', 'c-abstract', 'wenda-content', 'c-row']
        needGrandPa = ['op-medbaike-summary', 'wenda-content' ]
        result = []
        with open(html) as doc:
            soup = BeautifulSoup(doc, from_encoding='utf8')
            for tag in abstractTag:
                
                for abstract in soup.find_all('div', re.compile('^'+tag+'$')):
                    #只有tag这一个属性
                    content = ""
                    if ''.join(abstract['class']) in tag:
                        try:
                            if tag in needGrandPa:                            
                                title = abstract.find_parent().find_parent().h3.a
                                content += '\001' + title.get_text().strip().replace('\n', '')
                                    
                            else:
                                title = abstract.find_parent().a
                                content += '\001' + title.get_text().strip().replace('\n', '')
                            content += '\001' + abstract.get_text().strip().replace('\n', '')
                            result.append(content)
                        except:
                            print traceback.format_exc()
                            pass
        return result
    def testExtractTitleAbstract(self):
        name = u'癌性发热_0'
        for line in self.extractTitleAbstract(self.input + name):
            print line
        
        
    def extractRelevant(self, html):
        '''
        #提取相关搜索
        #输出格式: term1 \002 term2 \002 term3 ...
        '''
        terms = set()
        with open(html) as doc:
            soup = BeautifulSoup(doc, from_encoding='utf8')
            div = soup.find('div', text=u'相关搜索')
            for tr in div.find_parent().table.children:
                for th in tr.children:
                    terms.add(th.get_text()) 
        return terms
    def testExtractRelevant(self):
        name = u'癌性发热_0'
        path = u'E:/项目/医疗/内容提取/直肠癌/'
        inputPath = path + 'input/'
        terms =  self.extractRelevant(inputPath + name)
        for term in terms:
            print term
        


def runZhichangai():
    path = u'E:/项目/医疗/内容提取/直肠癌/'
    inputPath = path + 'input/'
    words = []
    with open(path + 'zhichangai_symp.txt', 'r') as f:
        for line in f.readlines():
            words.append(line.strip().decode('utf8'))
    maxLoop = 3
    baidu = BaiduSearchPage()
    #extract terms    
    output = path + 'terms'
    with open(output, 'a') as o:
        for word in words:
            terms = set()
            for i in xrange(maxLoop):
                html = inputPath + word + '_' + str(i)
                oneResult = baidu.extractTerm(html)
                terms = terms.union(oneResult)
            content = word.encode('utf8') + '\001'
            for term in terms:
                content += term.encode('utf8') + '\002'
            #print content
            o.write(content + '\n') 
               
    #extract title & abstract
    titleAbstract = []
    output = path + 'titleAbstract'
    with open(output, 'a') as o:
        for word in words:
            for i in xrange(maxLoop):
                html = inputPath + word + '_' + str(i)
                titleAbstract = baidu.extractTitleAbstract(html)
                content = word.encode('utf8') + '\001'
                for term in titleAbstract:
                    content += term.encode('utf8')
                    o.write(content + '\n') 
                    content = word.encode('utf8') + '\001'
    
    #extract relevant     
    output = path + 'relevant'
    with open(output, 'a') as o:
        for word in words:
            terms = set()
            for i in xrange(maxLoop):
                html = inputPath + word + '_' + str(i)
                oneResult = baidu.extractRelevant(html)
                terms = terms.union(oneResult)
            content = word.encode('utf8') + '\001'
            for term in terms:
                content += term.encode('utf8') + '\002'
            #print content
            o.write(content + '\n') 
    
    
if __name__ == '__main__':
    print time.asctime()
    #mainExtractYx129()
    runZhichangai()
    print time.asctime()
    #debugYx129()
   
       
