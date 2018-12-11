import requests

URL = "http://117.56.22.248:8060/AppWebService.svc/getCaseDec?caseId=180101137223"


temp_log_dict = dict
temp_car_dict = dict
CarLog = []
missionLog = []

data_dict = requests.get(URL).json()
if data_dict["d"]["Status"]:
    for temp_dict in data_dict["d"]["list"]:
        status = False
        if "分隊" in temp_dict["Descrip"]:
            status = True
        temp_log_dict = {
            "FocusMark": status,
            "logTime": temp_dict["EditDT"],
            "log": temp_dict["Descrip"]
        }
        if "梯次" in temp_dict["Descrip"]:
            temp_list = temp_dict["Descrip"].split("，")
            cars = temp_list[2].split("：")[1].split("、")
            carDetail = []
            for car_name in cars:
                # 這邊吃判斷消防車種類
                if car_name[-2:]:
                    car_type = "fireTruck"

                temp_car_detail = {
                    "name": car_name,
                    "type": car_type
                }
                carDetail.append(temp_car_detail)
            temp_car_dict = {
                "SeqNo": temp_list[1].split("：")[1],
                "Detail": carDetail
            }
            CarLog.append(temp_car_dict)
        missionLog.append(temp_log_dict)


#print(missionLog)
print(CarLog)
