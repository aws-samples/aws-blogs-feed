import os
import pytz
import requests
import re
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
import time


def clean_html(raw_html):
    reg1 = re.compile('<.*?>')
    reg2 = re.compile('&nbsp;')
    clean_text = re.sub(reg1, '', raw_html)
    cleaner_text = re.sub(reg2, '', clean_text)
    return cleaner_text


def lambda_handler(event, context):
    # The below is done in such a way because it was easier for me to test.
    FEED_PAGES = {1: "https://aws.amazon.com/blogs/architecture/feed/",
                  2: "https://aws.amazon.com/blogs/aws-cost-management/feed/",
                  3: "https://aws.amazon.com/blogs/apn/feed/",
                  4: "https://aws.amazon.com/blogs/awsmarketplace/feed/",
                  5: "https://aws.amazon.com/blogs/big-data/feed/",
                  6: "https://aws.amazon.com/blogs/business-productivity/feed/",
                  7: "https://aws.amazon.com/blogs/compute/feed/",
                  8: "https://aws.amazon.com/blogs/contact-center/feed/",
                  9: "https://aws.amazon.com/blogs/database/feed/",
                  10: "https://aws.amazon.com/blogs/desktop-and-application-streaming/feed/",
                  11: "https://aws.amazon.com/blogs/developer/feed/",
                  12: "https://aws.amazon.com/blogs/devops/feed/",
                  13: "https://aws.amazon.com/blogs/enterprise-strategy/feed/",
                  14: "https://aws.amazon.com/blogs/gametech/feed/",
                  15: "https://aws.amazon.com/blogs/infrastructure-and-automation/feed/",
                  16: "https://aws.amazon.com/blogs/iot/feed/",
                  17: "https://aws.amazon.com/blogs/machine-learning/feed/",
                  18: "https://aws.amazon.com/blogs/mt/feed/",
                  19: "https://aws.amazon.com/blogs/media/feed/",
                  20: "https://aws.amazon.com/blogs/messaging-and-targeting/feed/",
                  21: "https://aws.amazon.com/blogs/mobile/feed/",
                  22: "https://aws.amazon.com/blogs/networking-and-content-delivery/feed/",
                  23: "https://aws.amazon.com/blogs/opensource/feed/",
                  24: "https://aws.amazon.com/blogs/publicsector/feed/",
                  25: "https://aws.amazon.com/blogs/awsforsap/feed/",
                  26: "https://aws.amazon.com/blogs/security/feed/",
                  27: "https://aws.amazon.com/blogs/startups/feed/"}

    POST_HEADERS = {"Content-Type": "application/json"}
    GET_HEADERS = {"Accept": "application/xml", "Content-Type": "application/xml"}
    ADDRESS = os.environ['WEBHOOK_URL']
    LIST_OF_BLOGS = os.environ['BLOGS']

    if LIST_OF_BLOGS == "0" or not LIST_OF_BLOGS:
        LIST_OF_BLOGS = "1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,26,27,28"

    blogs = LIST_OF_BLOGS.split(",")

    blog_urls = []

    for num in blogs:
        if not num.isnumeric():
            continue
        index = int(num.strip())
        if index not in FEED_PAGES.keys():
            continue
        blog_urls.append(FEED_PAGES[index])

    blog_urls = set(blog_urls)
    for url in blog_urls:
        xml = requests.get(url, headers=GET_HEADERS)
        root = ET.fromstring(xml.text)
        for entry in root.iter('item'):

            published_datetime = datetime.strptime(entry.find(
                'pubDate').text, '%a, %d %b %Y %H:%M:%S %z')
            yesterday_datetime = datetime.now(pytz.utc) - timedelta(days=1)

            if published_datetime < yesterday_datetime:
                continue
            description = clean_html(entry.find('description').text)
            payload = "{\"Content\":\"BLOG\\n\\n" + entry.find(
                'title').text + "\\n\\n" + entry.find(
                'pubDate').text + "\\n\\n" + description + "\\n\\n" + entry.find(
                'link').text + "\"}"
            printable = "\\n".join(payload.split("\n"))
            response = requests.post(ADDRESS, data=printable.encode('utf-8'),
                                     headers=POST_HEADERS)
            print(response.status_code)
            print()
            time.sleep(1)

    return "Done"
