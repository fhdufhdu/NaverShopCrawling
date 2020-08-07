# -*- coding:utf-8 -*-
import time
import math
import json
import random
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class CrawlingNaver:

    def __init__(self, url):
        # options.headless = True
        # options.add_extension('./vpn.crx')

        path = 'driver/chromedriver83.exe'
        options = Options()
        self.driver = webdriver.Chrome(executable_path=path, options=options)

        self.url = url
        self.prd_name = 0
        self.price = 0
        self.last_cnt = '1'
        self.last_list_idx = 0

    def start_crawl(self):
        self.json_start_load()
        self.main_paging()

    def main_paging(self):
        cnt = self.last_cnt
        while True:
            self.driver.get(self.url + cnt)
            self.json_start_save_cnt(cnt)

            self.main_clicking()

            cnt = int(cnt) + 1
            cnt = str(cnt)

    def main_clicking(self):
        data_chk = True
        while data_chk:
            self.driver.get(self.driver.current_url)
            try:
                data = WebDriverWait(self.driver, 30)
            finally:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

                time.sleep(5)

                data = self.driver.find_elements_by_class_name('basicList_link__1MaTN')
                price = self.driver.find_elements_by_class_name('basicList_price__2r23_')

                list_idx = self.last_list_idx
                self.last_list_idx = 0

                print(len(data))

                if len(data) == 40:
                    for idx in range(list_idx, len(data)):
                        self.json_start_save_idx(idx)

                        self.prd_name = data[idx].text
                        self.price = price[idx].text
                        data[idx].click()

                        print(self.prd_name)
                        print(self.price)

                        self.review_crawling(positive=True)
                    data_chk = False

    def review_crawling(self, positive=True):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        while True:
            time.sleep(1)
            url = self.driver.current_url
            if url.find('cr.shopping.naver.com/adcr.nhn') == -1:
                url = 'http://itempage3.auction.co.kr/DetailView.aspx?ItemNo=A105368416&frm3=V2'
                self.driver.get(url)
                break
        try:
            data = WebDriverWait(self.driver, 30)
        finally:
            if url.find('smartstore') > -1:
                self.naver_crawling(url)
            elif url.find('auction') > -1:
                self.auction_crawling(url)
            elif url.find('coupang') > -1:
                self.coupang_crawling(url)
            else:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return
            '''elif url.find('11st') > -1:
                            self.eleven_crawling(url)'''
            '''
            elif url.find('gmarket') == -1:
            '''

    def naver_crawling(self, url):
        self.driver.get(url + '#revw')

        self.random_time_sleep(3, 6)

        option = self.driver.find_elements_by_css_selector(
            '#area_review_list > div.header_review._review_list_header > ul > li:nth-child(2) > a')
        review_cnt = self.driver.find_element_by_css_selector(
            '#area_review_list > div.header_review._review_list_header > strong > span').text.replace(',', '')

        print(review_cnt)

        if review_cnt == '0':
            self.json_file_save(url, '네이버쇼핑', review_cnt, [])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return

        '''positive가 true일 때 긍정리뷰, false일 때 부정리뷰
        if positive:
            option[2].click()
        else:
            option[3].click()
        self.random_time_sleep(3, 6)
        '''

        '''
        idx==현재 리뷰페이지
        total_dix==총 리뷰페이지
        select_btn_idx==페이지당 버튼 클릭 횟수
        '''
        idx = 1
        total_idx = math.ceil(int(review_cnt) / 20)
        select_btn_idx = 0
        first_check = True

        review_list = []
        '''리뷰 페이지 클릭하면서 긁어오기'''
        while True:
            li = self.driver.find_element_by_css_selector(
                '#area_review_list > div.detail_list_review._review_list').find_elements_by_tag_name('li')

            '''네이버 쇼핑몰은 두가지 버전이 있음'''
            if self.check_elem_css('#area_review_list > div.paginate._review_list_page'):
                if select_btn_idx == 11 and first_check:
                    select_btn_idx = 1
                    first_check = False
                if select_btn_idx == 12 and not first_check:
                    select_btn_idx = 1
                if select_btn_idx == 1:
                    select_btn_idx = 2
                btn_elem = self.driver.find_element_by_css_selector(
                    '#area_review_list > div.paginate._review_list_page').find_elements_by_tag_name('a')
            else:
                if select_btn_idx != 0 and (idx % 10) == 1:
                    select_btn_idx = 2
                if select_btn_idx == 0:
                    select_btn_idx = 1
                btn_elem = self.driver.find_element_by_css_selector(
                    '#area_review_list > nav').find_elements_by_tag_name('a')

            '''데이터 가져오는 영역'''
            cnt = 1
            for li_elem in li:
                try:
                    temp_dic = dict()

                    if li_elem.get_attribute('id') == '':
                        continue

                    li_id = '#' + li_elem.get_attribute('id')
                    css_name = li_id + ' > div > div.cell_text._cell_text > div.area_text > p > span.wrap_label > span'

                    temp_dic['grade'] = self.driver.find_element_by_css_selector(
                        li_id + ' > div > div.cell_text._cell_text > div.area_text'
                                ' > div.area_star_small > span.number_grade').text
                    if int(temp_dic['grade']) > 3:
                        cnt += 1
                        continue
                    temp_dic['date'] = self.driver.find_element_by_css_selector(
                        li_id + ' > div > div.cell_text._cell_text > div.are'
                                'a_text > div:nth-child(2) > div > span:nth-child(2)').text
                    if self.check_elem_css(
                            li_id + ' > div > div.cell_text._cell_text > div.area_text > div:nth-child(2) > div > p'):
                        temp_dic['option'] = self.driver.find_element_by_css_selector(
                            li_id + ' > div > div.cell_text._cell_text > div.area_text > div:nth-child(2) > div > p').text
                    else:
                        temp_dic['option'] = 'null'
                    if self.check_elem_css(css_name=css_name):
                        temp_dic['review_type'] = self.driver.find_element_by_css_selector(css_name).text
                    else:
                        temp_dic['review_type'] = '일반'
                    temp_dic['review'] = self.driver.find_element_by_css_selector(
                        li_id + ' > div > div.cell_text._cell_text > div.area_text > p > span').text
                    temp_dic['good'] = self.driver.find_element_by_css_selector(
                        li_id + ' > div > div.cell_recommend._cell_recommend > div > div > button > span').text
                    review_list.append(temp_dic)
                    cnt += 1
                except NoSuchElementException:
                    cnt += 1
                    continue

            '''리뷰 페이지 수 카운트'''
            if idx == total_idx:
                break
            btn_elem[select_btn_idx].click()
            select_btn_idx += 1
            idx += 1
            self.random_time_sleep(3, 6)
        self.json_file_save(url, '네이버쇼핑', review_cnt, review_list)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def eleven_crawling(self, url):
        prd_no = url[url.find('prdNo=') + 6:url.find('&NaPm')]
        review_cnt = self.driver.find_element_by_css_selector('#reviewTo > em').text.replace(',', '')
        review_cnt = review_cnt[1:len(review_cnt) - 1]
        review_max = math.ceil(int(review_cnt) / 10)

        if review_cnt == '0':
            self.json_file_save(url, '11번가', review_cnt, [])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return

        review_list = []
        for idx in range(1, review_max + 1):
            self.driver.get('http://www.11st.co.kr/product/SellerProductDetail.tmall?method=getProductReviewList&prdNo='
                            + prd_no + '&page=' + str(idx))
            self.random_time_sleep(3, 6)

            li = self.driver.find_element_by_css_selector('body > div > div.review_list').find_elements_by_tag_name(
                'li')
            cnt = 1

            for li_elem in li:
                try:
                    temp_dic = dict()
                    review_css = 'body > div > div.review_list > ul > li:nth-child(' + str(cnt)
                    grade = self.driver.find_element_by_css_selector(
                        review_css + ') > div > div.bbs_top > div.top_l > div > p > span').get_attribute('class')[-2:]
                    if grade == '00':
                        grade = '100'

                    temp_dic['grade'] = str(int(grade) // 20)
                    if int(temp_dic['grade']) > 3:
                        cnt += 1
                        continue
                    temp_dic['date'] = self.driver.find_element_by_css_selector(
                        review_css + ') > div > div.bbs_top > div.top_r > span').text[2:]
                    temp_dic['option'] = self.driver.find_element_by_css_selector(
                        review_css + ') > div > div.bbs_cont_wrap > div > p.option_txt').text
                    temp_dic['review_type'] = '일반'
                    temp_dic['review'] = self.driver.find_element_by_css_selector(
                        review_css + ') > div > div.bbs_cont_wrap > div > p.bbs_summary > span').text
                    if not self.check_elem_css(review_css + ') > div > div.btnwrap > p > a:nth-child(1) > span.cnt'):
                        cnt += 1
                        continue
                    temp_dic['good'] = self.driver.find_element_by_css_selector(
                        review_css + ') > div > div.btnwrap > p > a:nth-child(1) > span.cnt').text
                    review_list.append(temp_dic)
                    cnt += 1
                except NoSuchElementException:
                    cnt += 1
                    continue
        self.json_file_save(url, '11번가', review_cnt, review_list)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def auction_crawling(self, url):
        self.random_time_sleep(3, 6)
        review_btn = self.driver.find_element_by_css_selector('#tap_moving_2 > a')
        review_btn.click()

        review_cnt = self.driver.find_element_by_css_selector('#spnTotalItemTalk_display').text.replace(',', '')

        if review_cnt == '0':
            self.json_file_save(url, '옥션', review_cnt, [])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return

        page_max = int(self.driver.find_element_by_css_selector('#divVipReview > div > div > span > em').text)

        review_list = []
        for page_idx in range(1, page_max + 1):
            self.random_time_sleep(3, 6)
            page_num = self.driver.find_element_by_css_selector('#reviewPageNumber')
            page_next_btn = self.driver.find_element_by_css_selector('#divVipReview > div > div > a')

            page_num.send_keys(Keys.BACKSPACE)
            page_num.send_keys(str(page_idx))
            page_next_btn.click()
            self.random_time_sleep(3, 6)
            li = self.driver.find_element_by_css_selector('#divVipReview > ul').find_elements_by_class_name('list-item')
            cnt = 1

            for li_elem in li:
                try:
                    temp_dic = dict()
                    review_css = '#divVipReview > ul > li:nth-child(' + str(cnt) + ') '
                    if not self.check_elem_css(
                            review_css +
                            '> div > div.box__content > div.box__review-text > p'):
                        cnt += 1
                        continue
                    grade = self.driver.find_element_by_css_selector(
                        review_css +
                        '> div > div.box__content > div.box__info > div > span > span.sprite__vip.image__star-fill') \
                                .get_attribute('style')[-4:].replace('%;', '')
                    if grade == '00':
                        grade = '100'
                    temp_dic['grade'] = str(int(grade) // 20)
                    if int(temp_dic['grade']) > 3:
                        cnt += 1
                        continue
                    temp_dic['date'] = self.driver.find_element_by_css_selector(
                        review_css + '> div > div.box__content > div.box__info > p.text__date').text[2:]
                    temp_dic['option'] = self.driver.find_element_by_css_selector(
                        review_css + '> div > div.box__content > div.text__option > span').text
                    temp_dic['review_type'] = '일반'
                    temp_dic['review'] = self.driver.find_element_by_css_selector(
                        review_css + '> div > div.box__content > div.box__review-text > p').text
                    temp_dic['good'] = self.driver.find_element_by_css_selector(
                        review_css + '> div > div.box__helpful > button > span.text__count').text
                    review_list.append(temp_dic)
                    cnt += 1
                except NoSuchElementException:
                    cnt += 1
                    continue
        self.json_file_save(url, '옥션', review_cnt, review_list)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def coupang_crawling(self, url):
        self.random_time_sleep(3, 6)

        review_cnt = self.driver.find_element_by_css_selector(
            '#btfTab > ul.tab-titles > li:nth-child(2) > span').text.replace(',', '')
        review_cnt = review_cnt[1:len(review_cnt) - 1]
        
        if review_cnt == '':
            review_cnt = '0'
            self.json_file_save(url, '쿠팡', review_cnt, [])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return

        review_list = []

        review_btn = self.driver.find_element_by_css_selector('#btfTab > ul.tab-titles > li:nth-child(2)')
        review_btn.click()

        page_max = math.ceil(int(review_cnt)/5)
        page_cnt = 1
        page_idx = 2
        while True:
            self.random_time_sleep(3, 6)
            review_css = '#btfTab > ul.tab-contents > li.product-review > div > ' \
                         'div.sdp-review__article.js_reviewArticleContainer > section.js_reviewArticleListContainer'
            articles = self.driver.find_element_by_css_selector(review_css).find_elements_by_tag_name('article')
            cnt = 3
            for article in articles:
                try:
                    temp_dic = dict()
                    review_xpath_2 = review_css + ' > article:nth-child(' + str(cnt) + ') '
                    grade = self.driver.find_element_by_css_selector(
                        review_xpath_2 + '> div.sdp-review__article__list__info > div.sdp-review__article__list__info__'
                                         'product-info > div.sdp-review__article__list__info__product-info__star-gray > div'
                    ).get_attribute('style')[-4:].replace('%;', '')
                    if grade == '00':
                        grade = '100'

                    temp_dic['grade'] = str(int(grade) // 20)
                    if int(temp_dic['grade']) > 3:
                        cnt += 1
                        continue
                    temp_dic['date'] = self.driver.find_element_by_css_selector(
                        review_xpath_2 + '> div.sdp-review__article__list__info > div.sdp-review__article__list__info__'
                                         'product-info > div.sdp-review__article__list__info__product-info__reg-date').text[
                                       2:]
                    temp_dic['option'] = self.driver.find_element_by_css_selector(
                        review_xpath_2 + '> div.sdp-review__article__list__info > div.sdp-review__article__list__info__'
                                         'product-info__name').text
                    temp_dic['review_type'] = '일반'
                    if not self.check_elem_css(
                            review_xpath_2 + '> div.sdp-review__article__list__review.js_reviewArticleContentContainer'):
                        cnt += 1
                        continue
                    temp_dic['review'] = self.driver.find_element_by_css_selector(
                        review_xpath_2 + '> div.sdp-review__article__list__review.'
                                         'js_reviewArticleContentContainer > div').text
                    temp_dic['good'] = self.driver.find_element_by_css_selector(
                        review_xpath_2 + '> div.sdp-review__article__list__help.js_reviewArticleHelpfulContainer'
                    ).get_attribute('data-count')
                    cnt += 1
                    review_list.append(temp_dic)
                except NoSuchElementException:
                    cnt += 1
                    continue
            if page_idx == 12:
                page_idx = 2

            page_div = '#btfTab > ul.tab-contents > li.product-review > div > ' \
                       'div.sdp-review__article.js_reviewArticleContainer > section.js_reviewArticleListContainer > ' \
                       'div.sdp-review__article__page.js_reviewArticlePagingContainer'
            if page_cnt == page_max:
                break
            page_btn = self.driver.find_element_by_css_selector(page_div).find_elements_by_tag_name('button')
            page_btn[page_idx].click()
            page_idx += 1
            page_cnt += 1

        self.json_file_save(url, '쿠팡', review_cnt, review_list)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    '''def gmartket_crawling(self, url):
        self.random_time_sleep(3, 6)

        review_cnt = self.driver.find_element_by_css_selector('#txtReviewTotalCount').text

        review_btn = self.driver.find_element_by_css_selector(
            '#container > div.vip-tabwrap.uxetabs > div.vip-tabnavi.uxeposfix.fixed > ul > li.uxetabs_menu.on > a')
        review_btn.click()

        page_max = int(self.driver.find_element_by_css_selector(
            '#text-pagenation-wrap > div.board_paging > span > em').text)
        page_select_btn = self.driver.find_element_by_css_selector(
            '#text-pagenation-wrap > div.board_paging > div > button')
        page_select_btn.click()

        self.random_time_sleep(1, 3)

        pages = self.driver.find_element_by_css_selector(
            '#text-pagenation-wrap > div.board_paging > div > ul').find_elements_by_tag_name('li')
        for page in pages:
            page.click()
            self.random_time_sleep(3, 6)
       '''

    def check_elem(self, class_name):
        try:
            self.driver.find_element_by_class_name(class_name)
        except NoSuchElementException:
            return False
        return True

    def check_elem_css(self, css_name):
        try:
            self.driver.find_element_by_css_selector(css_name)
        except NoSuchElementException:
            return False
        return True

    def check_elem_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def shutdown(self):
        self.driver.quit()

    def json_file_save(self, url, type, review_cnt, review_list):
        with open('review/review_file_negative.json', 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
        add_json = {
            'product_name': self.prd_name,
            'product_price': self.price,
            'url': url,
            'type': type,
            'review_cnt': review_cnt,
            'review_list': review_list
        }
        json_dict['list'].append(add_json)
        json_dict['review_total'] = str(int(json_dict['review_total']) + int(review_cnt))
        with open('review/review_file_negative.json', 'w', encoding='utf-8') as make_file:
            json.dump(json_dict, make_file, indent='\t', ensure_ascii=False)

    def json_start_load(self):
        with open('restart/restart.json', 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
        self.last_cnt = json_dict['cnt']
        self.last_list_idx = int(json_dict['idx'])

    def json_start_save_cnt(self, cnt):
        with open('restart/restart.json', 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
        json_dict['cnt'] = cnt
        with open('restart/restart.json', 'w', encoding='utf-8') as make_file:
            json.dump(json_dict, make_file, indent='\t', ensure_ascii=False)

    def json_start_save_idx(self, idx):
        with open('restart/restart.json', 'r', encoding='utf-8') as file:
            json_dict = json.load(file)
        json_dict['idx'] = str(idx)
        with open('restart/restart.json', 'w', encoding='utf-8') as make_file:
            json.dump(json_dict, make_file, indent='\t', ensure_ascii=False)

    def random_time_sleep(self, start, stop):
        time.sleep(random.randrange(start, stop))

'''
1.다음버튼 누르면서 데이터 뽑기
2.평점 낮은순, 평점 높은순으로 데이터 뽑기(아니면 별점을 데이터베이스에 같이 집어넣기)
3.뽑는 데이터의 제한
4.시간당 가중치
5.데이터베이스 구현
리뷰내용, 시간, 별점(1~5), 상품옵션, 따봉, 한달사용기유무
https://smartstore.naver.com/dbtak/products/315627908#revw
'https://search.shopping.naver.com/search/all?query=탁구채&cat_id=&frm=NVSHATC&pagingIndex=2'
'''
