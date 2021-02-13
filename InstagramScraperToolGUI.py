import os
import json
import requests
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from lib import instagram_scraper as insta

class InstagramScraperToolGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('InstagramScraperTool')
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        label_page = QLabel('<font size="4"> Instagram page </font>')
        self.lineEdit_page = QLineEdit()
        self.lineEdit_page.setPlaceholderText('Please enter the Instagram page')
        layout.addWidget(label_page, 2, 0)
        layout.addWidget(self.lineEdit_page, 2, 1)

        self.button_run = QPushButton('Run')
        self.button_run.clicked.connect(self.scrape)
        layout.addWidget(self.button_run, 3, 0, 1, 3)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def scrape(self):
        try:
            #self.button_run.setEnabled(False) 
            instagram_page=self.lineEdit_page.text()
            print( '\\'.join(__file__.split('\\')[:-1]) + "\\drivers\\chromedriver.exe")
            try:
                isc = insta.InstagramScraper( '\\'.join(__file__.split('\\')[:-1]) + "\\drivers\\chromedriver.exe", output_folder='\\'.join(__file__.split('\\')[:-1]) + "\\output")
            except:
                isc = insta.InstagramScraper( '\\'.join(__file__.split('\\')[:-1]) + "drivers\\chromedriver.exe", output_folder='\\'.join(__file__.split('\\')[:-1]) + "\\output")
            r = isc.acceptCookies()
            if (r==False):
                print("Error accepting cookies")
                return
                
            r = isc.login(self.lineEdit_username.text(),self.lineEdit_password.text())
            if (r==False):
                print("Login failed")
                return

            r = isc.openInstagramPage(instagram_page)
            if (r==False):
                print("Error opening " + instagram_page)
                return

            
            posts_urls = isc.getPostsUrls()
            
            count=1
            for post_url in posts_urls:
                try:
                    output_filename_without_format = "{:06n}".format(count)
                    post_data = isc.getPostData(post_url)
                    '''
                    print("Caption = " + post_data["caption"])
                    print("Number of comments = " + str(post_data["number_of_comments"]))
                    print("Number of likes = " + str(post_data["number_of_likes"]))
                    print("Is video = " + str(post_data["is_video"]))
                    print("Media url = " + post_data["media_url"])
                    print("Hashtags:")
                    
                    for h in post_data["hashtags"]:
                        print(h)
                    '''
                    media_url = post_data["media_url"]
                    is_video = post_data["is_video"]
                    isc.saveMediaToFile(media_url,is_video, output_filename_without_format + "_media")    
                    count+=1
                except:
                    break

            isc.saveAllLikesToExcel("likes")
            isc.saveAllCommentsToExcel("comments")
            isc.saveAllHashtagsToExcel("hashtags")
            isc.saveAllCaptionsToExcel("captions")
            isc.saveAllCaptionsWithoutHashtagsToExcel("captions_without_hashtags")
        except:
            pass    

if __name__ == '__main__':
    app = QApplication(sys.argv)

    form = InstagramScraperToolGUI()
    form.show()

    sys.exit(app.exec_())
