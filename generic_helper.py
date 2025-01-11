import re

def extract_session_id(sesstion_str: str):
    
    match = re.search(r"/sessions/(.*?)/contexts/", sesstion_str)
    if match: # if found
        extracted_string = match.group(1)
        return extracted_string
    return "something wrong"


def get_str_from_food_dict(food_dict: dict):
    return ",".join([f'{int(value)} {key}' for key, value in food_dict.items()]) #list comprehension

if __name__=="__main__":
    sesstion_str = "projects/delchat-kstt/agent/sessions/4a112aa7-80d0-1403-bb97-02d5c945bb77/contexts/ongoing-order"
    # print(extract_session_id(sesstion_str))
    # print(get_str_from_food_dict({'samosa':2,'cholle':1}))