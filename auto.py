import cv2
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# import shutil
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
from tkinter import messagebox
import threading
from time import sleep

from db_course import *
from db_answer import *
from crawl_answer import *

# 多线程global list
videolist=[]
# global driver_state
# driver_state = True
class LazyChangeWorld():
    userphone = None
    userpassword = None
    def __init__(self,userphone,userpassword):
        self.userpassword = userpassword
        self.userphone = userphone

    # @staticmethod
    # def updateEdgeDriver():
    #     '''
    #     自动更新Edge驱动
    #     :return:
    #     '''
    #     global driver_state
    #     if (driver_state):
    #         print(".........正在更新驱动.........")
    #
    #         def delete_directory(target_directory):
    #             # 检查目标目录是否存在
    #             if os.path.exists(target_directory):
    #                 try:
    #                     # 使用rmtree删除目录及其所有内容
    #                     shutil.rmtree(target_directory)
    #                     print(f"{target_directory} 已成功删除。")
    #                 except Exception as e:
    #                     print(f"删除 {target_directory} 时出错: {e}")
    #             else:
    #                 print(f"{target_directory} 不存在。")
    #
    #         driver_path = EdgeChromiumDriverManager().install()
    #         print(f"正在下载驱动，默认位置:\n{driver_path}")
    #         # 获取驱动程序所在的文件夹路径
    #         driver_directory = os.path.dirname(driver_path)
    #         # 获取当前工作目录
    #         current_directory = os.getcwd()
    #         # 构建目标文件夹路径
    #         target_directory = os.path.join(current_directory, "drive")
    #         # 将驱动程序文件夹移动到目标文件夹
    #         if os.path.exists(target_directory):
    #             shutil.rmtree(target_directory)
    #         shutil.move(driver_directory, target_directory)
    #         print(f"正在从\n{driver_path}\n移动驱动至\n{target_directory}")
    #         # 更新驱动程序路径为目标文件夹下的路径
    #         driver_path = os.path.join(target_directory, os.path.basename(driver_path))
    #         # 从driver_directory变量中截取.wdm的路径
    #         wdm_directory = os.path.join(*driver_directory.split(os.sep)[:3], ".wdm")
    #         # 删除驱动目录与缓存目录
    #         print(f"正在删除驱动目录{wdm_directory}")
    #         delete_directory(wdm_directory)
    #         selenium_cache_directory = os.path.join(*driver_directory.split(os.sep)[:3], ".cache", "selenium")
    #         print(f"正在删除缓存目录{selenium_cache_directory}")
    #         delete_directory(selenium_cache_directory)
    #         # 多线程废弃
    #         # 初始化webdriver
    #         # driver = webdriver.Edge(executable_path=driver_path)
    #         # return driver
    #         driver_state = False
    #         print(".........更新驱动完毕.........")
    #     else:
    #         print("驱动已更新")
    def getImg(self,url, name):
        '''
        向图片所在url获取图片到本地
        :param url:
        :param name:
        :return:
        '''
        content = requests.get(url=url).content
        with open(name, 'wb') as fp:
            fp.write(content)
            print("获取验证码图片成功")

    def getXDistance(self,bgimg_name,brokenimg_name):
        '''
        获取验证滑块与缺口距离
        :param bgimg_name:
        :param brokenimg_name:
        :return:
        '''
        bg_img = cv2.imread(bgimg_name)  # 背景图片
        tp_img = cv2.imread(brokenimg_name)  # 缺口图片
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        cv2.imwrite("./img/black_bgimg.jpg", bg_pic)
        cv2.imwrite("./img/black_tpimg.jpg", tp_pic)
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
        X = max_loc[0]
        th, tw = tp_pic.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite('./img/out.jpg', bg_img)  # 保存在本地
        return X
    def login(self,driver,action):
        '''
        登录
        :param driver:
        :param action:
        :return:
        '''
        folder = "./img"
        if not os.path.exists(folder):  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(folder)
        driver.get('https://onlineweb.zhihuishu.com/onlinestuh5')
        sleep(2)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.ID, 'lUsername')))
        username = driver.find_element(By.ID, 'lUsername')
        username.send_keys(self.userphone)
        sleep(1)
        password = driver.find_element(By.ID, 'lPassword')
        password.send_keys(self.userpassword)
        sleep(1)
        login = driver.find_element(By.CLASS_NAME, "wall-sub-btn")
        login.click()
        sleep(2)
        i = 0#变化滑动，逃逸验证
        while 1:
            WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[31]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]")))
            yidun_bg_img_url = driver.find_element(By.XPATH,"/html/body/div[31]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]").get_attribute("src")
            yidun_jigsaw_url = driver.find_element(By.XPATH, "/html/body/div[31]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[2]").get_attribute("src")
            bg_img_name = "./img/bgimg_src.jpg"
            broken_img_name = "./img/brokenimg_src.jpg"
            self.getImg(yidun_bg_img_url, bg_img_name)
            self.getImg(yidun_jigsaw_url, broken_img_name)
            sleep(1)
            move_x = self.getXDistance(bg_img_name, broken_img_name)
            print("验证码拖动的距离:" + str(move_x) + "px")
            # 选择拖动滑块的节点
            drag_element = driver.find_element(By.CLASS_NAME, 'yidun_slider.yidun_slider--hover')
            action.click_and_hold(drag_element)
            # # 第二步：相对鼠标当前位置进行移动

            if i == 0:
                action.move_by_offset(move_x+10, 0)
                i = 1
            else:
                action.move_by_offset(move_x / 3 , 0)
                action.move_by_offset(move_x / 3, 0)
                action.move_by_offset(move_x / 3 + 10, 0)
                i = 0
            # # 第三步：释放鼠标
            action.release()
            # # 执行动作
            action.perform()
            sleep(3)
            if self.checkElement(driver, By.XPATH, "/html/body/div[31]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]") is False:
                print("滑块验证码通过！")
                break
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='sharingClassed']/div[2]/ul/div/dl/dt/div[1]/div[1]")))
    def videoAction(self, driver):
        '''
        播放视频行为链
        :param driver:
        :return:
        '''
        t = "-1"
        # 总时长
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "duration")))
        duration = driver.find_element(By.CLASS_NAME, "duration").text
        while 1:
            # 当前时长
            WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "currentTime")))
            currentTime = driver.find_element(By.CLASS_NAME, "currentTime").text
            print("currentTime:",currentTime)
            if (currentTime >= duration):
                print("播放完毕")
                break
            if(t == currentTime):
                print("视频暂停")
                self.videoQuestion(driver)
                # 继续播放
                WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "videoArea")))
                videoArea = driver.find_element(By.CLASS_NAME, "videoArea")
                try:
                    videoArea.click()
                except Exception as e:
                    print('element <div class="v-modal v-modal-leave"> obscures')
                    WebDriverWait(driver, 20, 0.5).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.v-modal.v-modal-leave')))
                    videoArea.click()
                # 执行JavaScript脚本点击元素
                # script = "document.getElementsByClassName('videoArea')[0].click();"
                # driver.execute_script(script)

                sleep(1)
            t = currentTime
            print("t : " + t + "  duration : " + duration)

            # 让视频下方的进度条一直出现
            js = "document.getElementsByClassName('controlsBar')[0].style.display='block'"
            driver.execute_script(js)
            sleep(0.5)
            box_right = driver.find_element(By.CLASS_NAME,"box-right")
            ActionChains(driver).move_to_element(box_right)
            # 检测间隔时间
            sleep(5)
            driver.execute_script(js)

    def runVideo(self, driver):
        '''
        播放视频
        :param driver:
        :return:
        '''
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "controlsBar")))
        js = "document.getElementsByClassName('controlsBar')[0].style.display='block'"
        driver.execute_script(js)
        sleep(0.5)

        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "speedBox")))
        speedBox = driver.find_element(By.CLASS_NAME, "speedBox")

        speedBox.click()
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "controlsBar")))
        driver.execute_script(js)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "speedTab.speedTab15")))
        speed = driver.find_element(By.CLASS_NAME, "speedTab.speedTab15")
        sleep(1)
        speed.click()
        # 再点击播放
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "videoArea")))
        videoArea = driver.find_element(By.CLASS_NAME, "videoArea")
        videoArea.click()
        sleep(1)
        # # 进入播放系统
        # self.videoAction(driver)

    def checkElement(self, driver, by, path):
        '''
        查找页面是否有指定元素
        :param driver:
        :param by:
        :param path:
        :return:
        '''
        try:
            sleep(1)
            driver.find_element(by,path)
            return True
        except :
            return False

    def videoQuestion(self, driver):
        '''
        回答视频途中出现的问题
        :param driver:
        :return:
        '''

        # 开始答题
        right_list = driver.find_elements(By.CLASS_NAME, "topic-item")

        try:
            for j,i in enumerate(right_list):
                if j == 0:
                    print("答题弹出")
                    print("开始答题")
                right_class = "iconfont.iconzhengque1"
                print("查找正确标签")
                if (self.checkElement(driver, By.CLASS_NAME, right_class)):
                    print("当前答题正确")
                    print("答题结束")
                    break
                error_class = 'iconfont.iconcuowu1'
                print("查找错误标签")
                if(self.checkElement(driver, By.CLASS_NAME, error_class)):
                    print("当前答题错误")
                i.click()
                sleep(2)
        except Exception:
            pass

        sleep(1)
        try:
            cancle_test = driver.find_element(By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")
            cancle_test.click()
            sleep(1)
        except Exception:
            pass
    def videoPageInit(self, driver):
        '''
        视频页面跳转初始化操作,关闭答题界面、广告
        :param driver:
        :return:
        '''
        # 检验刚进页面是否跳转答题
        if (self.checkElement(driver, By.XPATH, "//*[@id='playTopic-dialog']/div/div[3]/span/div")):
            self.videoQuestion(driver)
        # 取消广告界面
        sleep(2)
        if(self.checkElement(driver, By.CLASS_NAME, "iconfont.iconguanbi")):
            # 这里必须抛出异常，经过检验，广告弹窗元素一直处于界面中，
            # 只不过被display:none隐藏起来，若不弹出，能查找到，但不能点击则会报错
            try:
                cancel_target = driver.find_element(By.CLASS_NAME, "iconfont.iconguanbi")
                sleep(0.5)
                print("广告弹出")
                cancel_target.click()
                sleep(0.5)
            except Exception:
                pass
            print("广告关闭")
    def seprateNum(self,N, threadcount):
        '''
        划分线程区间
        :param N:
        :param threadcount:
        :return:
        '''
        # 对整个数字空间N进行分段CPU_COUNT
        selist = []
        n = int(N / threadcount) + 1;
        for i in range(threadcount - 1):
            right = N
            N = N - n
            if (N < 0):
                N = 0
            left = N
            s = (left, right)
            selist.append(s)
        right = N
        left = 0
        s = (left, right)
        selist.append(s)
        return selist
    def videolistThread(self, percent_elements, numlist):
        '''
        检查在numlist区间视频列表是否观看，初始化videolist
        :param percent_elements: numlist区间的视频元素
        :param numlist: 区间
        :return:
        '''
        t = numlist[0]
        for percent_element in percent_elements :
            video_text_xpath = percent_element.find_element(By.CLASS_NAME,'catalogue_title')
            # 打印当前元素名称
            video_text = video_text_xpath.text
            global videolist
            if(self.checkElement(percent_element,By.CSS_SELECTOR,"b.fl.time_icofinish")):
                video = {
                    'index':t,
                    'name':video_text,
                    'isStudies':1
                }
                videolist.append(video)
                print(video_text_xpath.text+"已经观看完毕")
            else:
                video = {
                    'index': t,
                    'name':video_text,
                    'isStudies': 0
                }
                videolist.append(video)
                print(video_text_xpath.text+"未观看完毕")
            print(video)
            t = t + 1


    def addDb(self, db, list):
        '''
        数据库增
        :param db:
        :param list:
        :return:
        '''
        for item in list:
            db.addItem(item=item)
    # 爬取章节名称
    def videolistInit(self, driver, db_mysql):
        '''
        多线程获取所有视频名称与是否观看完毕
        :param driver:
        :param db_mysql:
        :return:
        '''
        percent_elements = driver.find_elements(By.CLASS_NAME,'clearfix.video')
        n = len(percent_elements)
        print("n : "+str(n))
        threadcount = 10
        numlist = self.seprateNum(n,threadcount)
        print(numlist)
        global videolist
        threads = []
        for i in numlist[0:len(numlist)]:
            print(i[0], i[1])
            split_elements = percent_elements[i[0]:i[1]]
            t = threading.Thread(target=self.videolistThread, args=(split_elements, i))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        for video in videolist:
            db_mysql.addItem(video)
        print("videolist")
        videolist = db_mysql.selectAll()
        print(videolist)
        return videolist

    def doTest(self, driver, db_answer):
        '''
        根据Answer.db的答案做测试Test
        :param driver:
        :param db_answer:
        :return:
        '''
        print("开始做本章单元测试")
        sleep(1)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/h1')))
        answer_choose = {
            "A":0,
            "B":1,
            "C":2,
            "D":3,
            "E":4,
            "F":5,
            "G":6,
        }
        #判断题转换
        judge_dict={
            "√": "对",
            "X": "错"
        }
        chapter = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div/h1')
        chapter_text = chapter.text
        print("单元章节 : " + chapter_text)
        chapter_text = chapter_text.replace("测试","")
        # 总答案
        answers = db_answer.selectAll(chapter_text)
        print(answers)
        # 总题数
        # WebDriverWait(driver, 10, 0.5).until(
        #     EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/ul/li[2]/span')))
        # requestions = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/ul/li[2]/span')
        # requestions = requestions.text
        # 页面中总选项父节点
        choose_targets_xpath = driver.find_elements(By.CLASS_NAME,'subject_node')
        # 页面中总题目类型节点
        subject_types = driver.find_elements(By.CLASS_NAME,"subject_type")
        #记录做题数
        record = 0
        for (index,answer) in enumerate(answers):
            record=index
            # 题目类型标签
            subject_type = subject_types[index].find_element(By.XPATH,'.//span[1]')
            type_text = subject_type.text
            print("type_text : "+type_text)
            choose_targets = choose_targets_xpath[index].find_elements(By.CLASS_NAME, "label.clearfix")
            # 多选题
            if ("多选" in type_text):
                print("进入多选")
                # 所有的选项
                print("答案为 : " + answer)
                # 如果答案是ABCD类型的选项直接点
                if 'A' in answer or 'B' in answer or 'C' in answer or 'D' in answer or 'E' in answer:
                    for i in answer:
                        choose_targets[answer_choose[i]].click()
                # 如若不是则遍历选项
                else:
                    for choose_target in choose_targets:
                        choose = choose_target.find_element(By.XPATH, ".//div[2]")
                        choose = choose.text
                        print("选项为 : " + choose_target.text)
                        if(choose in answer):
                            choose_target.click()
                            print("多选选中")
            # 单选题
            else:
                if '√' in answer or 'X' in answer:
                    answer=judge_dict[answer]
                for choose_target in choose_targets:
                    choose = choose_target.find_element(By.XPATH,".//div[2]")
                    choose = choose.text
                    print("选项为 : " + choose)
                    print("答案为 : " + answer)
                    if choose in answer:
                        print("选中")
                        choose_target.click()
                        break
                    sleep(1)
            # 下一题的选项
            next_button = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[3]/button[2]')
            next_button.click()
            sleep(0.5)
        print(chapter.text+"已经做完")
        if record >= 5:
            submit = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div/div/button[1]')
            submit.click()
            sleep(0.5)
            WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="提示"]/div/div[3]/button[2]')))
            confirm=driver.find_element(By.XPATH,'//div[@aria-label="提示"]/div/div[3]/button[2]')
            confirm.click()
            sleep(2)



    def main(self,is_watch,is_dotest,name="",mode=0):
        '''
        行为链全流程
        :param is_watch: 是否观看
        :param is_dotest: 是否答题
        :param name: 指定课程
        :param mode:答案网址选择
        :return:
        '''
        try:
            if is_watch is False and is_dotest is False:
                print("目前选择为不观看、不答题")
                return
            # LazyChangeWorld.update_driver()
            # driver_path = os.path.join(os.getcwd(), "drive", "msedgedriver.exe")
            # s=Service("msedgedriver.exe")
            # driver = webdriver.Edge(service=s)
            s = Service("geckodriver.exe")

            # # 使用该路径初始化webdriver
            driver = webdriver.Firefox(service=s)
            # 初始化selenium行为
            action = ActionChains(driver)
            # driver.get('about:preferences#searchResults')
            # WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.ID, 'pictureInPictureToggleEnabled')))
            # pictureInPictureToggleEnabled = driver.find_element(By.ID, 'pictureInPictureToggleEnabled')
            # pictureInPictureToggleEnabled.click()

            # 初始化videolist
            global videolist
            # 登录智慧树
            try:
                self.login(driver, action)
            except Exception as e:
                print(e)
                messagebox.showerror(title="出现异常", message="登录失败！请检查手机号与密码是否正确！")
                return
            for i in range(1,100):
                # print(f'//*[@id="sharingClassed"]/div[2]/ul[{i}]/div/dl/dt/div[1]/div[1]')
                if self.checkElement(driver, By.XPATH, f'//*[@id="sharingClassed"]/div[2]/ul[{i}]/div/dl/dt/div[1]/div[1]'):
                    coursename_element = driver.find_element(By.XPATH, f'//*[@id="sharingClassed"]/div[2]/ul[{i}]/div/dl/dt/div[1]/div[1]')
                    coursename = coursename_element.text
                    print(f"该用户第{i}个课程为：{coursename}")
                    if coursename==name:
                        print("选中课程：",coursename)
                        # 初始化Course.db
                        table_name = 'user_' + self.userphone + '_' + name
                        db_course = Course(table_name)
                        # 初始化Answer.db
                        db_answer = Answer(coursename)
                        # 初始化答案爬虫
                        crawl_answer = CrawlAnswer(coursename)
                        coursename_element.click()
                        break
                else:
                    if i == 1:
                        print("该用户没有课程！")
                        # 关闭浏览器
                        driver.quit()
                        break
                    print("未找到课程："+name)
                    coursename_element = driver.find_element(By.XPATH, '//*[@id="sharingClassed"]/div[2]/ul[1]/div/dl/dt/div[1]/div[1]')
                    coursename = coursename_element.text
                    print("选择默认课程：",coursename)
                    table_name = 'user_' + self.userphone + '_' + coursename
                    db_course = Course(table_name)
                    # 初始化Answer.db
                    db_answer = Answer(coursename)
                    # 初始化答案爬虫
                    crawl_answer = CrawlAnswer(coursename)
                    coursename_element.click()
                    break
            sleep(2)
            # 打开视频页面的初始化
            self.videoPageInit(driver)
            if (is_watch):
                # 爬取数据的初始化,判断当前表是否有数据,若有则不爬取
                if (db_course.checkTableEmpty()):
                    self.videolistInit(driver, db_course)
                else:
                    videolist = db_course.selectAll()
                self.videoPageInit(driver)
                video_elements = driver.find_elements(By.CLASS_NAME, 'clearfix.video')
                print("视频数量 : "+str(len(video_elements)))
                for (i,item) in enumerate(video_elements):
                    if (db_course.findById(i)["isStudies"] == int(1)):
                        print(str(i) +"号视频" + db_course.findById(i)["name"] + "已经看过")
                        continue
                    # 点击当前需要看的界面
                    print("当前观看网课名称:" + db_course.findById(i)["name"])
                    sleep(1)
                    item.click()
                    sleep(0.5)
                    # 进入页面初始化
                    self.videoPageInit(driver)
                    self.runVideo(driver)
                    # 进入播放系统
                    self.videoAction(driver)
                    # 结束播放,提交数据至数据库
                    db_course.updataById(i)
                    sleep(1)
                driver.quit()
                print("视频全部播放完毕")
                messagebox.showinfo(message="视频全部播放完毕")
            if (is_dotest):
                self.videoPageInit(driver)
                print("开始做测试")
                if(db_answer.checkTableEmpty()):
                    answerlist = crawl_answer.getAnswer(mode=mode);
                    self.addDb(db_answer, answerlist)
                test_elements = driver.find_elements(By.CLASS_NAME, 'chapter-test')
                for test in test_elements:
                    test.click()
                    sleep(0.5)
                    if (self.checkElement(driver, By.XPATH, '//*[@id="app"]/div/div[7]/div/div[3]/span/button[2]')):
                        print("当前测试已经做过")
                        cancle_test = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[7]/div/div[3]/span/button[2]')
                        cancle_test.click()
                        continue
                    sleep(2.5)
                    # 切换到第二个标签页
                    driver.switch_to.window(driver.window_handles[1])
                    print("切换至第二个标签页")
                    # 在第二个标签页中执行操作
                    # ...
                    self.doTest(driver, db_answer)

                    # 切换回第一个标签页
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    print("切换回第一个标签页")
                driver.quit()
                print("已全部作答完毕")
                messagebox.showinfo(message="已全部作答完毕")
            return
        except Exception as e:
            print(e)
            messagebox.showerror(title="出现异常",message="1、请尝试重新启动\n2、请手动登录检查验证码是否手动点击！\n3、检查网速是否过慢\n4、请检查是否挂载在VPN")
            return
#测试
if __name__ == "__main__":
    auto = LazyChangeWorld("手机号","密码")
    auto.main(0,1)







