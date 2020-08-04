import json

review_list = []
for idx in range(1, 4):
    path = 'review/review_file.json'
    with open(path, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
    for first_list in json_dict['list']:
        for second_list in first_list['review_list']:
            review_list.append(second_list)
print(len(review_list))
save_dict = dict()
save_dict['list'] = review_list
with open('learning/learning_list.json', 'w', encoding='utf-8') as make_file:
    json.dump(save_dict, make_file, indent='\t', ensure_ascii=False)
