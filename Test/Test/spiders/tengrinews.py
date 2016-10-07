# -*- coding: utf-8 -*-
import scrapy

from scrapy.spiders import CrawlSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

class Comment:
    def __init__(self, author, text, rating):
        self.author = author
        self.text = text
        self.rating = rating
    

class TengrinewsSpider(CrawlSpider):
    name = "tengrinews"
    allowed_domains = ["tengrinews.kz"]
    fieldnames = ['news url', 'author', 'comment text', 'rating']
    
    def __init__(self):
        self.driver = webdriver.Firefox()
    
    def start_requests(self):
        yield scrapy.Request('https://tengrinews.kz/news/', self.parse)
        
    def parse(self, response):
        with open('comments.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
            writer.writeheader()
        self.driver.get(response.url)
        #button = self.driver.find_element_by_xpath('//div[@class="load_more_block"]/a')
        #button.click()
        listLinks = [a.get_attribute('href') for a in self.driver.find_elements_by_xpath('//div[@class="news clearAfter pl mb"]/a')]
        for url in listLinks:
            comments = self.parseANews(url)
            self.writeToFile(url, comments)
    
    def parseANews(self, url):
        self.driver.get(url)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        wait = WebDriverWait(self.driver, 10)
        while True:
            try:
                moreComments = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@id="jsBtn"]/span')))
                moreComments.click()
            except:
                break
        
        buttons = self.driver.find_elements_by_xpath('//span[@class="more"]')
        for i in range(len(buttons)):
            try:
                wait.until(EC.visibility_of(buttons[i]))
                buttons[i].click()
            except Exception as e:
                with open('except.txt', 'a') as f:
                    f.write('{0}:#{1}\n{2}\n'.format(url,i,str(e)))
        comments = []
        comments_body = self.driver.find_elements_by_xpath('//div[@class="comment"]')
        for comment in comments_body:
            com_author = comment.find_element_by_xpath('./div[@class="user"]/span').text
            com_text = comment.find_element_by_xpath('./div[@class="comment_text"]/span').text
            com_rating = comment.find_element_by_xpath('./div[@class="rating"]/span[contains(@class,rate)]').text
            com = Comment(com_author, com_text, com_rating)
            comments.append(com)
        return comments

    def writeToFile(self, url, comments):
        with open('comments.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
            for comment in comments:
                writer.writerow({self.fieldnames[0]: url, self.fieldnames[1]: comment.author, self.fieldnames[2]: comment.text, self.fieldnames[3]: comment.rating})
