import requests
from lxml import etree
import re
from pprint import pprint
from urllib.parse import urljoin

class CrawlAnswer(object):
    coursename=None
    __answer_url=None
    html=None
    text=None
    cookies = {
            'verifiedCode': 'verified',
            'ASPSESSIONIDACQQQQBQ': 'DLKFJAPCPHDALMBFLMKIJPJG'
        }
    def __init__(self,coursename):
        self.coursename=coursename
    def searchAnswerUrl(self):
        '''
        根据self.coursename课程名称搜索answer_url
        :return:
        '''
        url = "http://www.jhq8.cn/s/{}/".format(self.coursename)
        root_url = "http://www.jhq8.cn"

        response = requests.get(url=url, cookies=self.cookies)
        self.html = response.text
        # print(self.html)
        # 使用lxml解析HTML
        tree = etree.HTML(self.html)
        # 使用XPath提取标题内容
        title = tree.xpath('//title/text()')
        #print(title)

        if title[0]=="安全检查中...":
            print("安全检查中...")
            self.cookies.clear()
            self.cookies = requests.utils.dict_from_cookiejar(response.cookies)
            print("新cookies:", self.cookies)
            self.cookies['verifiedCode']='verified'
            print("新cookies:", self.cookies)
            response = requests.get(url=url, cookies=self.cookies)
            self.html = response.text
            # print(self.html)

        tree = etree.HTML(self.html)
        relative_answer_url = tree.xpath('.//div[@class="lift_remen-list"]/ul/li/a/@href')[0]
        __answer_url = root_url + relative_answer_url
        print(f"{self.coursename}答案网址：",__answer_url)
        return __answer_url
    def __requestHtml(self,url,mode = 0):
        '''
        向url请求发起请求获取响应报文html(str类型)
        :param url:
        :param mode:0代表gbk解码html
        :return:响应报文html(str类型)
        '''
        response = requests.get(url)
        html = response.text
        #print(html)
        if mode == 0:
            html = html.encode('iso-8859-1').decode('gbk')
        return html

    def __getText(self,url, xpath,mode=0):
        '''
        获取响应报文html(str类型)中指定xpath的text
        :param url:
        :param xpath:
        :param mode:
        :return: 指定xpath的text(list类型)
        '''
        html = self.__requestHtml(url,mode=mode)
        tree = etree.HTML(html)
        text = tree.xpath(xpath + 'text()')
        return text

    def __getPages(self,url, relative_path):
        '''
        获取url上级目录（相对路径relative_path）下的所有pages的url
        :param url:
        :param relative_path:
        :return: pages_list(list类型)
        '''
        tree = etree.HTML(self.__requestHtml(url))
        pages = tree.xpath('.//ul[@class="pagination-list"]/a')
        pages_list = [url]
        for i in range(2, len(pages)):
            text = tree.xpath('.//a[text()="{}"]/@href'.format(i))[0]
            pages_list.append(relative_path + text)
        return pages_list

    def __num_to_chinese(self,num):
        '''
        阿拉伯数字转中文数字
        :param num:
        :return:中文数字(str类型)
        '''
        chinese_dict = {
            0: '零', 1: '一', 2: '二', 3: '三', 4: '四',
            5: '五', 6: '六', 7: '七', 8: '八', 9: '九',
            10: '十', 11: '十一', 12: '十二', 13: '十三', 14: '十四',
            15: '十五', 16: '十六', 17: '十七', 18: '十八', 19: '十九',
            20: '二十', 21: '二十一', 22: '二十二', 23: '二十三', 24: '二十四',
            25: '二十五', 26: '二十六', 27: '二十七', 28: '二十八', 29: '二十九',
        }
        num = int(num)
        return chinese_dict[num]

    def getAnswer(self,mode=0):
        '''
        爬取答案
        :param mode: :答案网址选择
        :return:
        '''
        if mode == 0:
            self.__answer_url = self.searchAnswerUrl()
            root_path = urljoin(self.__answer_url+"/", "../")
            print("答案网址上级目录：",root_path)
            answer_pages_list = self.__getPages(self.__answer_url, root_path)
            print("答案分页网址：",answer_pages_list)
            texts = []
            for item in answer_pages_list:
                texts += self.__getText(item, './/div[@class="content"]/div/div/p/')
            print("答案：",texts)

            chapter = "绪论"
            self_answer = {
                "title": "",
                "answer": "",
                "chapter": chapter
            }
            choose = {}
            answerlist = []
            # 题目下标
            title_num = 1
            # 章节下标
            chapter_num = 0
            for text in texts:
                # 去除空格
                text = text.strip()
                # print(text)
                # 答案
                if "我的答案:" in text or "我的答案：" in text:
                    # print(text)
                    text = text[5:]
                    # print(text)
                    self.text = text.strip()
                    self.text = re.sub("[^ABCDE√X]", "", self.text)
                    if ('A' in text or 'B' in text or 'C' in text or 'D' in text or 'E' in text):
                        newstr = ""
                        if (len(text) >= 1 and len(text) < len(choose)):
                            # print(text)
                            for i in text:
                                try:
                                    newstr += choose[i] + ","
                                except Exception:
                                    pass
                            self.text = newstr
                    self_answer["answer"] = self.text
                    # print(self_answer)
                    answerlist.append(self_answer)
                    self_answer = {
                        "title": "",
                        "answer": "",
                        "chapter": chapter
                    }
                    choose = {}
                elif "第" in text and "章" in text:
                    chapter_num = chapter_num + 1
                    title_num = 1
                    chapter = "第" + self.__num_to_chinese(chapter_num) + "章"
                    self_answer = {
                        "title": "",
                        "answer": "",
                        "chapter": chapter
                    }
                # 答案标题
                elif (text[0].isdecimal()):
                    # print("标题 : "+text)
                    num_regex = re.compile(r'^(\d+)')
                    # 使用正则表达式提取数字
                    match1 = num_regex.match(text)
                    title_num_current = match1.group(1)
                    if (int(title_num_current) < int(title_num)):
                        chapter_num = chapter_num + 1
                        chapter = "第" + self.__num_to_chinese(chapter_num) + "章"
                        print("当前爬取答案章节号有误，已自动修正")
                        print("可能有误章节号 : " + chapter)
                        self_answer = {
                            "title": "",
                            "answer": "",
                            "chapter": chapter
                        }
                        title_num = int(title_num_current)
                    title_num = title_num + 1
                    self_answer["title"] = text[::]
                # 答案选项
                elif ("." in text or ":" in text or (
                        ("A、" in text) or ("E、" in text) or ("B、" in text) or ("C、" in text) or ("D、" in text))):
                    # print("答案选项")
                    if ("." in text):
                        parts = text.split(".")
                    elif (":" in text):
                        parts = text.split(":")
                    else:
                        parts = text.split("、")
                    choose[parts[0]] = parts[1]
            pprint(answerlist)
            return answerlist
        if mode == 1:
            html = self.__requestHtml('https://zhihuishu.wangkebaohe.com/?cat=&s=' + self.coursename,mode=1)
            # print(html)
            tree = etree.HTML(html)
            url = tree.xpath('//h2[@class="entry-title"]/a/@href')[0]
            print(url)
            # url='https://zhihuishu.wangkebaohe.com/4125/'
            chapter_list = self.__getText(url, './/div[@class="entry-content u-text-format u-clearfix"]/h2/',mode=1)
            texts = self.__getText(url, './/div[@class="entry-content u-text-format u-clearfix"]/p/',mode=1)
            print(texts)
            if not chapter_list:
                print("h2没内容,转为h2/span")
                chapter_list = self.__getText(url, './/div[@class="entry-content u-text-format u-clearfix"]/h2/span/',mode=1)
            print(chapter_list)
            for i in range(len(chapter_list)):
                chapter_list[i] = chapter_list[i].split()[0]
            print(chapter_list)

            i = -1
            chapter = ''
            self_answer = {
                "title": "",
                "answer": "",
                "chapter": ""
            }
            answerlist = []
            for text in texts:
                # 去除空格
                text = text.strip()
                # print(text)
                if text == '':
                    continue
                # 答案
                if "正确答案:" in text or "正确答案：" in text:
                    # print(text)
                    text = text[5:]

                    self.text = text.strip()
                    self_answer["answer"] = self.text
                    self_answer['chapter'] = chapter
                    answerlist.append(self_answer)
                    self_answer = {
                        "title": "",
                        "answer": "",
                        "chapter": ""
                    }
                elif (text[0].isdecimal()):
                    if text[0:2:] == '1、':
                        i += 1
                        chapter = chapter_list[i]
                    self_answer["title"] = text[::]

            pprint(answerlist)
            return answerlist
#测试
if __name__ == "__main__":
    c=CrawlAnswer("保险与生活")
    #c.searchAnswerUrl()
    c.getAnswer(mode=0)
