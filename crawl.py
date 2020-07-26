#-*- coding:utf-8 -*-
import time
import math
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class CrawlingNaver:

    def __init__(self, url):
        path = "./chromedriver84.exe"
        options = Options()
        #options.headless = True
        options.add_extension("./vpn.crx")
        self.url = url
        self.driver = webdriver.Chrome(executable_path=path, options=options)
        self.prd_name = 0
        self.price = 0

    def start_crawl(self):
        self.main_paging()

    def main_paging(self):
        cnt = "1"
        while True:
            self.driver.get(self.url+cnt)
            cnt = int(cnt)+1
            cnt = str(cnt)
            self.main_clicking()

    def main_clicking(self):
        try:
            data = WebDriverWait(self.driver, 30)
        finally:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            data = self.driver.find_elements_by_class_name("basicList_link__1MaTN")
            price = self.driver.find_elements_by_class_name("basicList_price__2r23_")
            for idx in range(0, len(data)):
                self.prd_name = data[idx].text
                self.price = price[idx].text
                print(self.prd_name)
                print(self.price)
                data[idx].click()
                self.review_crawling(positive=True)

    def review_crawling(self, positive=True):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        url = self.driver.current_url
        self.driver.get(url+"#revw")
        try:
            data = WebDriverWait(self.driver, 30)
        finally:
            time.sleep(2)
            if url.find("smartstore") == -1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return
            option = self.driver.find_elements_by_class_name("option_sort")
            review_cnt = self.driver.find_element_by_id("review_preview").find_element_by_class_name("num").text.replace(',', '')

            '''positive가 true일 때 긍정리뷰, false일 때 부정리뷰
            if positive:
                option[2].click()
            else:
                option[3].click()
            time.sleep(1)
            '''
            '''
            idx==현재 리뷰페이지
            total_dix==총 리뷰페이지
            select_btn_idx==페이지당 버튼 클릭 횟수
            '''
            idx = 1
            total_idx = math.ceil(int(review_cnt)/20)
            select_btn_idx = 0
            first_check = True

            review_list = []
            '''리뷰 페이지 클릭하면서 긁어오기'''
            while True:
                data = self.driver.find_element_by_css_selector("#area_review_list > div.detail_list_review._review_list").find_elements_by_tag_name("li")
                '''네이버 쇼핑몰은 두가지 버전이 있음'''
                if self.check_elem("paginate"):
                    if select_btn_idx == 11 and first_check:
                        select_btn_idx = 1
                        first_check = False
                    if select_btn_idx == 12 and not first_check:
                        select_btn_idx = 1
                    if select_btn_idx == 1: select_btn_idx = 2
                    btn_elem = self.driver.find_element_by_class_name("paginate").find_elements_by_tag_name("a")
                else:
                    if select_btn_idx != 0 and (idx % 10) == 1: select_btn_idx = 2
                    if select_btn_idx == 0: select_btn_idx = 1
                    btn_elem = self.driver.find_element_by_class_name("module_pagination")
                    btn_elem = btn_elem.find_elements_by_tag_name("a")

                '''데이터 가져오는 영역'''
                for key in data:
                    if key.get_attribute("id") == '':
                        continue
                    css_name = '#'+key.get_attribute("id")+' > div > div.cell_text._cell_text > div.area_text > p > span.wrap_label > span'
                    temp_dic = dict()
                    temp_dic['평점'] = key.find_element_by_class_name("number_grade").text
                    temp_dic['날짜'] = key.find_elements_by_class_name("text_info")[1].text
                    temp_dic['옵션'] = key.find_elements_by_class_name("text_info")[2].text
                    if self.check_elem_css(css_name=css_name):
                        temp_dic['리뷰형태'] = key.find_element_by_css_selector(css_name).text
                    else:
                        temp_dic['리뷰형태'] = '일반'
                    temp_dic['리뷰'] = key.find_element_by_class_name("text").text
                    temp_dic['좋아요'] = key.find_element_by_class_name("count").text
                    review_list.append(temp_dic)

                '''리뷰 페이지 수 카운트'''
                if idx == total_idx:
                    break
                btn_elem[select_btn_idx].click()
                select_btn_idx += 1
                idx += 1
                time.sleep(1)
            self.json_file_save(review_cnt, review_list)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

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

    def shutdown(self):
        self.driver.quit()

    def json_file_save(self, review_cnt, review_list):
        with open("./review_file.json", "r", encoding='utf-8') as file:
            json_dict = json.load(file)
        add_json = {
            'product_name': self.prd_name,
            'product_price': self.price,
            'review_cnt': review_cnt,
            'review_list': review_list
        }
        json_dict['list'].append(add_json)
        with open("./review_file.json", "w", encoding='utf-8') as make_file:
            json.dump(json_dict, make_file, indent="\t", ensure_ascii=False)

crawl = CrawlingNaver(url="https://search.shopping.naver.com/search/all?query=탁구채&cat_id=&frm=NVSHATC&pagingIndex=")
crawl.start_crawl()
crawl.shutdown()


'''
1.다음버튼 누르면서 데이터 뽑기
2.평점 낮은순, 평점 높은순으로 데이터 뽑기(아니면 별점을 데이터베이스에 같이 집어넣기)
3.뽑는 데이터의 제한
4.시간당 가중치
5.데이터베이스 구현
리뷰내용, 시간, 별점(1~5), 상품옵션, 따봉, 한달사용기유무
https://smartstore.naver.com/dbtak/products/315627908#revw
"https://search.shopping.naver.com/search/all?query=탁구채&cat_id=&frm=NVSHATC&pagingIndex=2"
'''