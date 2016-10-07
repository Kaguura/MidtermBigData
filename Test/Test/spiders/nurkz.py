# -*- coding: utf-8 -*-
import scrapy

from scrapy.spiders import CrawlSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

class Comment:
    def __init__(self, author, text, plus, minus):
        self.author = author
        self.text = text
        self.plus = plus
        self.minus = minus
    

class TengrinewsSpider(CrawlSpider):
    name = "nurkz"
    allowed_domains = ["nur.kz"]
    fieldnames = ['news id', 'title', 'author', 'comment text', 'likes plus', 'likes minus']
    
    def __init__(self):
        self.driver = webdriver.Firefox()
    
    def start_requests(self):
        yield scrapy.Request('https://nur.kz/latest', self.parse)
        
    def parse(self, response):
        with open('nurkz.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
            writer.writeheader()
        self.driver.get(response.url)
        #button = self.driver.find_element_by_xpath('//div[@class="load_more_block"]/a')
        #button.click()
        news = self.driver.find_elements_by_xpath('//a[@class="news__link-overlay js-news-link-overlay"]')
        listLinks = [a.get_attribute('href') for a in news]
        title = [a.text for a in news]
        for i in range(10):
            comments = self.parseANews(listLinks[i])
            self.writeToFile(i, title[i], comments)
    
    def parseANews(self, url):
        self.driver.get(url)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        wait = WebDriverWait(self.driver, 10)
        while True:
            try:
                moreComments = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="news__more"]')))
                moreComments.click()
            except:
                break
        
        comments = []
        comments_body = self.driver.find_elements_by_xpath('//li[@class="answer__item"]')
        for comment in comments_body:
            com_author = comment.find_element_by_xpath('.//span[@class="answer__name"]').text
            com_text = comment.find_element_by_xpath('.//div[@class="answer__text"]').text
            com_plus = comment.find_element_by_xpath('.//div[@class="answer__up"]/span[@class="answer__value"]').text
            com_minus = comment.find_element_by_xpath('.//div[@class="answer__down"]/span[@class="answer__value"]').text
            com = Comment(com_author, com_text, com_plus, com_minus)
            comments.append(com)
        return comments

    def writeToFile(self, i, title, comments):
        with open('nurkz.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
            for comment in comments:
                writer.writerow({self.fieldnames[0]: i, self.fieldnames[1]: title, self.fieldnames[2]: comment.author, self.fieldnames[3]: comment.text, self.fieldnames[4]: comment.plus, self.fieldnames[5]: comment.minus})
