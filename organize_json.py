import json
from konlpy.tag import Okt

okt = Okt()

with open('review/review_file_negative_deform.json', 'r', encoding='utf-8') as file:
    json_dict = json.load(file)

for prod_list in json_dict['list']:
    r_list = []
    cnt = 0
    for review in prod_list['review_list']:
        review['id'] = cnt
        cnt += 1
        pos = okt.pos(review['review'], norm=True, stem=True)
        pos_str = ''
        word2vec = []
        for pos_elem in pos:
            if pos_elem[1] == 'Punctuation' or pos_elem[1] == 'KoreanParticle' or pos_elem[1] == 'Alpha':
                continue
            if pos_elem[0] == '\n':
                continue
            pos_str += ' ' + pos_elem[0]
            word2vec.append(pos_elem[0])
        review['tf-idf'] = pos_str
        review['word2vec'] = word2vec
        '''if review['review'] == '잘 받았습니다. 많이 파세요 ^^' or \
            review['review'] == '완전 강추합니다.' or \
            review['review'] == '가격대비 괜찮네요~~' or \
            review['review'] == '잘 받았습니다. 많이 파세요^^' or \
            review['review'] == '잘받았습니다. 마음에 들어요.' or\
            review['review'] == '한달사용기' or\
            review['review'] == '한달사용기BEST' or\
            review['review'] == '한달사용기재구매' or\
            review['review'] == '정말 마음에 쏙 들어요!':
            continue
        r_list.append(review)
    prod_list['review_list'] = r_list'''

with open('review/review_file_negative_deform.json', 'w', encoding='utf-8') as make_file:
    json.dump(json_dict, make_file, indent='\t', ensure_ascii=False)
