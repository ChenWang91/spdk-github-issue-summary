#!/usr/bin/env python

import sys
from subprocess import call, check_output, Popen
from multiprocessing import Pool
proxy = 'http://child-proxy.intel.com:913'

try:
    import argparse
    import requests
    import xlwt
    import gevent
    from lxml import etree
    from pprint import pprint
except ImportError as e:
    print("This machine can't install the package will install it.")
    call("pip install argparse --proxy {0}".format(proxy), shell=True)
    call("pip install requests --proxy {0}".format(proxy), shell=True)
    call("pip install lxml --proxy {0}".format(proxy), shell=True)
    call("pip install xlwt --proxy {0}".format(proxy), shell=True)
    call("pip install gevent --proxy {0}".format(proxy), shell=True)
    try:
        import argparse
    except ImportError as e:
        print(e.message)

def issue_link_spider(args):
    mes = requests.get(base_url)
    element = etree.HTML(mes.text)
    number = [i for i in element.xpath('//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div/div[4]/div/a/text()')]
    number.remove('Next')
    max_num = int(max(number))
    #issue_num = []
    for i in range(1, max_num + 1):
        mes = requests.get(base_url + page_url.format(i))
        element = etree.HTML(mes.text)
    #*************************
        #issue_num += [i for i in element.xpath('//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div/div[3]/ul/li//@id')]
    #return [i.split('_')[1] for i in issue_num]
    #*************************

        # Use generate to replace the list.
        for i in element.xpath('//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div/div[3]/ul/li//@id'):
            yield i.split('_')[1]

def generate_xls(issue_info):
    elements = ["url","title","author","assignees","labels"]
    f = xlwt.Workbook()
    table = f.add_sheet("results", cell_overwrite_ok=True)
    table.write(0, 0, "ISSUE-URL")
    table.write(0, 1, "TITLE")
    table.write(0, 2, "AUTHOR")
    table.write(0, 3, "ASSIGNNEES")
    table.write(0, 4, "LABELS")
    for k, v in enumerate(issue_info):
        for i in elements:
            if i != "url" and len(v[i]) >= 2:
                content = [j+"  " for j in v[i]]
            else:
                content = v[i]
            table.write(k+1, elements.index(i), content)
        print "Number {0} has done".format(k+1)

    f.save("spdk_issue_summary.xls")

def issue_info_spider(link):
    issue_info = {}
    main_link = base_url + "/" + link
    mes = requests.get(main_link)
    element = etree.HTML(mes.text)
    issue_info["url"] = main_link
    issue_info["title"] = element.xpath('//*[@id="partial-discussion-header"]/div[1]/h1/span[1]/text()')
    issue_info["author"] = element.xpath('//*[@id="partial-discussion-header"]/div[2]/div[2]/a/text()')
    issue_info["assignees"] = element.xpath('//*[@id="partial-discussion-sidebar"]/div[1]/form/span/p/span/a[2]/span/text()')
    issue_info["labels"] = element.xpath('//*[@id="partial-discussion-sidebar"]/div[2]/div[2]/div/a/span/text()')
    return issue_info


def main():
    parse = argparse.ArgumentParser(description="Git hub issue")
    parse.add_argument("--labels",
                        default = "All",
                        help = "The label for issues, Example: bug, high, low... default is All.")
    args = parse.parse_args()
    issue_link = issue_link_spider(args.labels)
    tasks = []
    p = Pool(50)
    for i in issue_link:
    #*************************
    #    tasks.append(gevent.spawn(issue_info_spider, i))
    #gevent.joinall(tasks)
    #*************************
    #    p = Process(target=issue_info_spider, args=(i,))
    #    p.start()
    #************************
        tasks.append(p.apply_async(issue_info_spider,(i,)))
    p.close()
    p.join()
    for i in tasks:
        yield i.get()

if __name__ == "__main__":
    base_url = "https://github.com/spdk/spdk/issues"
    page_url = "?page={0}&q=is%3Aissue+is%3Aopen"
    issue_info = main()
    generate_xls(issue_info)
