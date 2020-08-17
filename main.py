from crawl import CrawlingNaver
import json

#crawl = CrawlingNaver(url='https://search.shopping.naver.com/search/all?query=탁구&cat_id=&frm=NVSHATC&sort=review&pagingIndex=')
#crawl.start_crawl()
#crawl.shutdown()


with open('review/review_file_deform.json', 'r', encoding='utf-8') as file:
    json_dict = json.load(file)

for l in json_dict['list']:
    review_list = []
    for r in l['review_list']:
        if len(r['word2vec']) == 0:
            continue
        review_list.append(r)
    l['review_list'] = review_list
with open('review/review_file_deform.json', 'w', encoding='utf-8') as make_file:
    json.dump(json_dict, make_file, indent='\t', ensure_ascii=False)