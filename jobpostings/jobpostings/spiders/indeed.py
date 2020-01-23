# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Response
from colorama import init
from termcolor import colored
import logging


class IndeedSpider(scrapy.Spider):
    init()
    name = "indeed"
    allowed_domains = ["www.indeed.com"]
    start_urls = ["https://www.indeed.com/jobs?q=c%23+net+developer&l=Roseville%2C+CA"]

    def parse(self, response):
        """
        :type response: Response
        """
        posts = response.xpath(
            "//td[@id='resultsCol']/child::div[contains(@class,'jobsearch-SerpJobCard')]"
        )
        for post in posts:
            url = response.urljoin(
                post.xpath(".//a[contains(@class,'jobtitle')]/@href").get()
            )
            location = post.xpath(".//*[contains(@class,'location')]/text()").get()
            company = "".join(
                post.xpath(
                    ".//*[contains(@class, 'company')]/descendant-or-self::text()"
                ).getall()
            )
            yield response.follow(
                url=url,
                callback=self.parse_posting,
                meta={"posting_url": url, "location": location, "company": company},
            )
        next_page = response.urljoin(
            response.xpath(
                "//div[@class='pagination']/a[position() = last() and descendant::span[@class='np']]/@href"
            ).get()
        )
        logging.info(colored({"next_page": next_page}, "red"))
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_posting(self, response):
        """
        :type response: Response
        """
        posting_url = response.request.meta["posting_url"]
        location = response.request.meta["location"]
        company = response.request.meta["company"]
        posting_title = response.xpath(
            "//h3[contains(@class,'jobsearch-JobInfoHeader-title')]/text()"
        ).get()
        posting_text = "".join(
            response.xpath(
                "//div[@id='jobDescriptionText']/descendant-or-self::text()"
            ).getall()
        )
        yield {
            "posting_title": posting_title,
            "posting_url": posting_url,
            "posting_text": posting_text,
            "location": location,
            "company": company,
        }
