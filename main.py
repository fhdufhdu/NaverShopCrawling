from crawl import CrawlingNaver

crawl = CrawlingNaver(url='https://search.shopping.naver.com/search/all?query=탁구&cat_id=&frm=NVSHATC&sort=review&pagingIndex=')
crawl.start_crawl()
crawl.shutdown()
