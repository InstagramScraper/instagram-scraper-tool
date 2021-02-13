import os
import time
import json
import requests
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class InstagramScraper:
    def __init__(self, webdriver_path, instagram_url="http://www.instagram.com", output_folder="output"):
        self.instagram_url=instagram_url
        self.webdriver_path=webdriver_path
        self.getDriver()
        self.driver.get(self.instagram_url)
        self.output_folder=output_folder
        self.makeDir(self.output_folder)
        self.currentPage=""
        self.all_posts_comments=[]
        self.all_posts_likes=[]
        self.all_posts_captions=[]
        self.all_posts_hashtag = []
        self.all_posts_captions_without_hashtags = []

    def makeDir(self,folder_name): 
        '''Make a dir'''
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    
    def getDriver(self):
        '''Load the webdriver for Selenium'''
        self.driver = webdriver.Chrome(self.webdriver_path)

    def openWebPage(self,url):
        '''Surf to a webpage'''
        try:
            self.driver.get(url) 
            return True
        except:
            return False

    def acceptCookies(self, button_class_name="bIiDR"):
        '''Accept the Cookies clicking on the related button'''
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, button_class_name))).click()
            return True
        except:
            return False

    def login(self,username,password):
        '''Login to Instagram'''
        try:
            username_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
            password_box = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
            username_box.clear()
            username_box.send_keys(username)
            password_box.clear()
            password_box.send_keys(password)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            self.notNow()
            return True
        except:
            return False

    def notNow(self):
        ''' '''      
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        except:
            pass

    def clean(self):
        self.all_posts_comments=[]
        self.all_posts_likes=[]
        self.all_posts_captions=[]
        self.all_posts_hashtag = []

    def openInstagramPage(self,page_name):
        '''Surf to an Instagram page'''
        self.currentPage=page_name
        self.clean()
        return self.openWebPage(self.instagram_url + "/" + page_name + "/")

    def getNumberOfPosts(self, page_name=None):
        '''Return the number of posts of an Instagram page'''
        if page_name!=None:
            self.openInstagramPage(page_name)
            time.sleep(3)
        return int((self.driver.find_element_by_xpath("//span[text() = ' posts']/span").text).replace(",",""))
    
    def getPostsUrls(self, limit = None, page_name=None):
        '''Return a list containing the url of all the posts of an Instagram page'''
        self.clean()
        if page_name!=None:
            self.openInstagramPage(page_name)
        time.sleep(3)
        if (limit == None or limit>self.getNumberOfPosts()):
            limit = self.getNumberOfPosts()
        posts_urls =list()
        while (len(posts_urls) < limit):
            try:
                elems = self.driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG  _bz0w']/a")
                for elem in elems:
                    url = elem.get_attribute('href')
                    if url not in posts_urls:
                        posts_urls.append(url)
                self.scrollDownPage()
            except:
                pass
        return posts_urls

    def scrollDownPage(self):
        '''Scroll down a webpage'''
        html = self.driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
    
    def getPageBody(self,url):
        '''Return the html body of a webpage'''
        self.driver.get(url)
        return self.driver.find_element_by_tag_name('body').text

    def getPostData(self,post_url):
        '''Return a dictionary containing these keys:
            - "caption" = (str) caption of the post
            - "number_of_comments" = (int) number of comments
            - "is_video" = (bool) it is True if the media is a video else it is False if it is an image
            - "comments" = (list) list containing all the comments
            - "number_of_likes" = (int) number of like
            - "media_url" = (str) url of the media (image or video)
            - "hashtags" = (list) list containing all the hashtags
            for a specific post specified througt post_url parameter
        '''
        self.openWebPage(post_url)
        text = self.getPageBody(post_url+"?__a=1&max_id=endcursor")
        data = json.loads(text)
        post_data = dict()
        
        try:
            post_data["caption"] = data["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"]["text"] 
            post_data["caption_without_hashtags"]=""
            tmp=""
            for w in post_data["caption"].split(" "):
                if len(w)>0:
                    if w[0]!="#":
                        tmp=tmp+' '+w
            for w in tmp.split("\n"):
                if len(w)>0:
                    if w[0]!="#":
                        post_data["caption_without_hashtags"]=post_data["caption_without_hashtags"]+'\n'+w
            
        except:
            post_data["caption"]=""
            post_data["caption_without_hashtags"]=""

        if post_data["caption"]!="":
            tmp1 = []
            for w in post_data["caption"].split(" "):
                if len(w)>0:
                    if w[0]=="#":
                        tmp1.append(w)
            tmp2 = []
            for w in post_data["caption"].split("\n"):
                if len(w)>0:
                    if w[0]=="#":
                        tmp2.append(w)
            post_data["hashtags"] = list(set(tmp1+tmp2))
        else:
            post_data["hashtags"] = []
        post_data["number_of_comments"] = int(data["graphql"]["shortcode_media"]["edge_media_to_parent_comment"]["count"])
        post_data["is_video"] = data["graphql"]["shortcode_media"]["is_video"]
        post_data["comments"] = data["graphql"]["shortcode_media"]["edge_media_to_parent_comment"]["edges"]
        post_data["number_of_likes"] = int(data["graphql"]["shortcode_media"]["edge_media_preview_like"]["count"])
        if (post_data["is_video"]):
            post_data["media_url"] = data["graphql"]["shortcode_media"]["video_url"]
        else:
            post_data["media_url"] = data["graphql"]["shortcode_media"]["display_url"]
        self.all_posts_likes.append(post_data["number_of_likes"])
        self.all_posts_comments.append(post_data["comments"])
        self.all_posts_captions.append(post_data["caption"])
        self.all_posts_captions_without_hashtags.append(post_data["caption_without_hashtags"])
        self.all_posts_hashtag.append(post_data["hashtags"])
        return post_data
    
    def saveMediaToFile(self, media_url, is_video,output_filename_without_format):
        '''Save the media of a post to file'''
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage) 
        self.makeDir(self.output_folder + os.sep + self.currentPage + os.sep + "media") 
        reponse = requests.get(media_url)
        if reponse.status_code == 200:
            if (is_video):
                file_format = ".mp4"
            else:
                file_format=".jpg"
            with open(self.output_folder + os.sep + self.currentPage + os.sep + "media" + os.sep + output_filename_without_format +file_format,"wb") as file:
                file.write(reponse.content)
            return True
        else:
            return False

    def saveAllCommentsToExcel(self, output_filename_without_format):
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage)
        workbook = xlsxwriter.Workbook(self.output_folder + os.sep + self.currentPage + os.sep + output_filename_without_format + ".xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for comments in self.all_posts_comments:
            col = 0
            for comment in comments:
                worksheet.write(row, col, comment["node"]["text"])
                col += 1
            row+=1
        workbook.close()

    def saveAllCaptionsToExcel(self, output_filename_without_format):
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage)
        workbook = xlsxwriter.Workbook(self.output_folder + os.sep + self.currentPage + os.sep + output_filename_without_format + ".xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for caption in self.all_posts_captions:
            worksheet.write(row, 0, caption)
            row += 1
        workbook.close()

    def saveAllCaptionsWithoutHashtagsToExcel(self, output_filename_without_format):
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage)
        workbook = xlsxwriter.Workbook(self.output_folder + os.sep + self.currentPage + os.sep + output_filename_without_format + ".xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for caption in self.all_posts_captions_without_hashtags:
            worksheet.write(row, 0, caption)
            row += 1
        workbook.close()
    
    def saveAllHashtagsToExcel(self, output_filename_without_format):
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage)
        workbook = xlsxwriter.Workbook(self.output_folder + os.sep + self.currentPage + os.sep + output_filename_without_format + ".xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for hs in self.all_posts_hashtag:
            col = 0
            for h in hs:
                worksheet.write(row, col, h)
                col += 1
            row+=1
        workbook.close()
    
    def saveAllLikesToExcel(self, output_filename_without_format):
        self.makeDir(self.output_folder)
        self.makeDir(self.output_folder + os.sep + self.currentPage)
        workbook = xlsxwriter.Workbook(self.output_folder + os.sep + self.currentPage + os.sep + output_filename_without_format + ".xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for likes in self.all_posts_likes:
            worksheet.write(row, 0, likes)
            row += 1
        workbook.close()
        
