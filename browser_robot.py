from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime, localtime

import os
def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.mkdir(path)


class Robot():
    def __init__(self, url, try_out_time = 5, time_level = 1, no_head = True, browser_name = 'chrome'):
        '''
        机器人类，用于模拟浏览器操作。

        初始化变量：

        url：链接；
        try_out_time = 5: 各点击、寻找元素等操作尝试的最大次数，超过该次数将报错；
        time_level = 1:强制等待时间倍率；
        no_head = True:无头模式开关；
        browser_name = 'chrome':指定浏览器，不为'firefox'时默认为chrome。
        '''
        self.time_level = time_level
        self.start_time = strftime("%H-%M-%S_%m-%d-%Y", localtime())
        self.try_out_time = try_out_time 
        if(no_head):
            if(browser_name == 'firefox'):
                options = webdriver.FirefoxOptions()
            else:
                options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument('--window-size=1920x1080')
            options.add_argument('--start-maximized')
            if(browser_name == 'firefox'):
                self.browser = webdriver.Firefox(options=options)
            else:
                self.browser = webdriver.Chrome(options=options)
        else:
            if(browser_name == 'firefox'):
                options = webdriver.FirefoxOptions()
            else:
                options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            if(browser_name == 'firefox'):
                self.browser = webdriver.Firefox(options=options)
            else:
                self.browser = webdriver.Chrome(options=options)
        self.browser.get(url)
        self.browser.implicitly_wait(10)

    def get_screen(self, name='screenshot'):
        '''
        截图。
        可指定截图名称前缀'name'，后缀默认为启动时间.png。
        保存路径为相对路径下的'./src_+启动时间'文件夹。
        '''
        mkdir('./scr_'+self.start_time)
        print('get_screen {}'.format(name))
        self.browser.get_screenshot_as_file("./scr_{}/{}.png".format(self.start_time, name))

    def scroll_by_xpath(self, xpath):
        '''
        自动滚动至目标元素可见处。
        注意！对部分内部滚动条可能无效！此时请使用'scroll_div_by_xpath'。
        '''
        self.browser.execute_script("arguments[0].scrollIntoView();", self.browser.find_element_by_xpath(xpath))

    def getting_for_xpath(self, xpath, before_xpath = None):
        '''
        寻找并返回元素。
        可指定获取前必须存在的先决元素'before_xpath'。
        若指定了先决元素，该函数将等待至该元素出现再寻找目标元素。
        '''
        print('getting_for_xpath {}'.format(xpath))
        try_time = 0
        while(1):
            try:
                return self.browser.find_element_by_xpath(xpath)
            except:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('GET_XPATH_TIME_OUT')
                if(before_xpath != None):
                    try_before_time = 0
                    while(len(self.browser.find_elements_by_xpath(before_xpath)) > 0):
                        try_before_time += 1
                        if(try_before_time > self.try_out_time):
                            raise Exception('GET_XPATH_CLICK_BEFORE_TIME_OUT')
                        self.click_by_xpath(before_xpath)
                continue
    def click_by_xpath(self, xpath, next_xpath=None):
        '''
        单击元素。
        可指定单击前必须存在的先决元素'before_xpath'。
        若指定了先决元素，该函数将等待至该元素出现再单击目标元素。
        '''
        self.implicitly_wait()
        print('click_by_xpath {}'.format(xpath))
        elem = self.getting_for_xpath(xpath)
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
        while(elem.get_attribute('disabled')):
            continue
        try_time = 0
        while(1):
            try:
                self.browser.execute_script('arguments[0].click()',elem)
                if(next_xpath != None and len(self.browser.find_elements_by_xpath(next_xpath)) <= 0):
                    elem = self.getting_for_xpath(xpath)
                    try_time += 1
                    continue
                break
            except:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('CLICK_TIME_OUT')
                self.browser.execute_script("arguments[0].scrollIntoView();", elem)

    def send_keys_by_xpath(self, xpath, text, sleep_time=0.1, before_xpath = None,\
                           check_flag = False, with_tab = True):
        '''
        向元素输入文本。
        可指定单击前必须存在的先决元素'before_xpath'。
        若指定了先决元素，该函数将等待至该元素出现再单击目标元素。
        '''
        self.implicitly_wait()
        print('send_keys_by_xpath {}'.format(xpath))
        if(before_xpath == None):
            elem=self.getting_for_xpath(xpath)
        else:
            try:
                elem=self.browser.find_element_by_xpath(xpath)
            except:
                try_time = 0
                while(len(self.browser.find_elements_by_xpath(before_xpath)) > 0):
                    try_time += 1
                    if(try_time > self.try_out_time):
                        raise Exception('SEND_KEY_CLICK_BEFORE_ELEM_TIME_OUT')
                    self.click_by_xpath(before_xpath)
                elem=self.browser.find_element_by_xpath(xpath)
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
        try_time = 0
        while(1):
            try:
                try:
                    elem.send_keys(text)
                except:
                    ActionChains(self.browser).send_keys_to_element(elem,text).perform()
                if(with_tab):
                    try:
                        elem.send_keys(Keys.TAB)
                    except:
                        ActionChains(self.browser).send_keys_to_element(elem,Keys.TAB).perform()
                while(check_flag and elem.text == ''):
                    try:
                        elem.send_keys(text)
                    except:
                        ActionChains(self.browser).send_keys_to_element(elem,text).perform()
                sleep(self.time_level * sleep_time)
                break
            except Exception as e:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('SEND_KEY_TIME_OUT')
                self.browser.execute_script("arguments[0].scrollIntoView();", elem)
    def send_keys_by_id(self, id, text):
        '''
        向元素输入文本。
        '''
        print('send_keys_by_id {}'.format(id))
        try_time = 0
        while(1):
            try:
                elem = self.browser.find_element_by_id(id)
                break
            except:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('SEND_KEY_TIME_OUT')
                continue
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
        elem.click()
        elem.clear()
        elem.send_keys(text)

    def key_down_by_xpath(self, xpath, sleep_time=1):
        '''
        向元素输入方向“下”键。主要用于打开输入框的搜索子页面（非下拉框）。
        '''
        print('key_down_by_xpath {}'.format(xpath))
        elem = self.getting_for_xpath(xpath)
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
        sleep(self.time_level * sleep_time)
        try_time = 0
        while(1):
            try:
                ActionChains(self.browser).click(elem).perform()
                ActionChains(self.browser).send_keys_to_element(elem, Keys.DOWN).perform()
                break
            except:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('KEY_DOWN_TIME_OUT')
                sleep(self.time_level * sleep_time)
                self.browser.execute_script("arguments[0].scrollIntoView();", elem)
                sleep(self.time_level * sleep_time)

    def find_element_by_xpath(self, xpath):
        '''
        用于向外暴露selenium库中用于寻找元素的函数。
        主要用于判断元素是否已存在。
        相比于getting_for_xpath，该函数不会尝试多次寻找。
        '''
        return self.browser.find_element_by_xpath(xpath)

    def num_of_elements_by_xpath(self, xpath):
        '''
        用于返回符合要求的元素数量。
        '''
        return len(self.browser.find_elements_by_xpath(xpath))
    
    def find_elements_by_xpath(self, xpath):
        '''
        用于返回符合要求的元素列表。
        '''
        return self.browser.find_elements_by_xpath(xpath)
    
    def send_keys_by_element(self, elem, text):
        '''
        对目标元素输入文本。
        相比于send_keys_by_xpath，该函数直接以元素本身为输入，而非xpath。
        '''
        print('send_keys_by_element {}'.format(text))
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
        ActionChains(self.browser).click(elem).perform()
        ActionChains(self.browser).send_keys_to_element(elem, text).perform()
        ActionChains(self.browser).key_down(Keys.ENTER).perform()
    
    def sleep(self, sleep_time = 0.5):
        '''
        重新封装的sleep，会加成time_level倍率，默认0.5秒。
        '''
        sleep(self.time_level * sleep_time)
    
    def implicitly_wait(self, th_time = 5):
        '''
        隐式等待，默认时间阈值为5秒。
        该函数会先等待0.5×时间倍率秒，再在五秒内等待页面加载完成。
        若加载时间超过5秒，将报错。
        '''
        self.sleep()
        self.browser.implicitly_wait(th_time)

    def xpath_have_class(self, xpath):
        '''
        用于返回元素所拥有的class。
        将以str格式返回结构，通常通过 'class_name' in return_result来实现是否存在指定class的判断。
        '''
        elem = self.browser.find_element_by_xpath(xpath)
        return str(elem.get_attribute('class'))
    
    def check_msg(self):
        '''
        用于读取在保存或下一步时页面弹出的提示。
        有两个返回值：
        
        第一位为布尔值，成功时返回1。
        第二位为str，不成功时返回提示信息。

        '''
        self.implicitly_wait()
        msg = ''
        try_time = 0
        while(msg == ''):
            try_time += 1
            if(try_time > self.try_out_time):
                raise Exception('CHECK_MSG_TIME_OUT')
            msg = self.browser.find_element_by_xpath("//div[@class='ant-notification-notice-message']").text
            info = self.browser.find_element_by_xpath("//div[@class='ant-notification-notice-description']").text
        if(msg == '操作成功'):
            return 1, ''
        else:
            self.get_screen('check_error')
            return 0, info
    
    def scroll_div_by_xpath(self, xpath, length=1000):
        '''
        用于控制因过长而出现横向滚动条的div元素的滚动条位置。
        '''
        self.browser.execute_script("arguments[0].scrollLeft={};".format(length), self.find_element_by_xpath(xpath))
    
    def get_text_by_xpath(self, xpath):
        '''
        用于获取元素text信息
        '''
        self.implicitly_wait()
        self.scroll_by_xpath(xpath)
        self.implicitly_wait()
        return self.browser.find_element_by_xpath(xpath).text
    
    def get_attribute_by_xpath(self, xpath, att):
        '''
        用于获取元素某attribute信息
        '''
        self.implicitly_wait()
        self.scroll_by_xpath(xpath)
        self.implicitly_wait()
        return self.browser.find_element_by_xpath(xpath).get_attribute(att)
    
    def send_and_click_by_xpath(self, send_xpath, text):
        '''
        用于带放大镜的搜索框内的输入。
        输入文本后会自动选择点击匹配的文本匹配项。
        '''
        try_time = 0
        while(1):
            try:
                self.send_keys_by_xpath(send_xpath, text, with_tab=False)
                self.click_by_xpath("//li[text()='{}']".format(text))
                break
            except:
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('SEND_AND_CLICK_XPATH_TIME_OUT')
                continue
    
    def click_drop_down_by_xpath(self, xpath, click_list, finish_click=False):
        '''
        下拉框选择函数。
        click_list可为list也可为str，及支持多选。
        通常，多选下拉需要将finish_click设为True，使得下拉框能够关闭。
        '''
        if(isinstance(click_list, str)):
            click_list = [click_list]
        self.click_by_xpath(xpath)
        for i in click_list:
            try_time = 0
            while(self.num_of_elements_by_xpath("//li[text()='{}']".format(i)) == 0):
                self.click_by_xpath(xpath)
                try_time += 1
                if(try_time > self.try_out_time):
                    raise Exception('CLICK_DROP_DOWN_XPATH_TIME_OUT')
            self.click_by_xpath("//li[text()='{}']".format(i))
        if(finish_click):
            self.click_by_xpath(xpath)
