from threading import Timer
import tkinter as tk
from tkinter import ttk
import webbrowser
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json
import pandas
import time
import xlsxwriter

BASE_URL = "https://account.shodan.io"
SEARCH_URL = "https://www.shodan.io/"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() + "\\chromedriver.exe"

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)


# define progress bar
class ProgressBar(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.progress = ttk.Progressbar(main_page, orient="horizontal", length=400, mode="indeterminate")
        self.progress.place(x=100, y=500)
        self.val = 0
        self.maxval = 1
        self.progress["maximum"] = 1

    def updating(self, val):
        self.val = val
        self.progress["value"] = self.val

        if self.val == self.maxval:
            self.destroy()


# totally shut the whole application
def shutdown():
    driver.quit()
    main_page.destroy()


def check_all():
    all_ip_dict = "all_ip_dict_json"
    if os.path.exists("all_ip_dict_json"):
        with open(all_ip_dict, 'r') as input_file:
            ip_dict = json.load(input_file)

    def onselectall(evt):

        w = evt.widget
        index = str(w.curselection()[0])

        detail_dict = ip_dict[index]['detail']
        lb_detail.delete(0, 'end')

        lb_detail.insert('end', ip_dict[index]['ip_name'])
        lb_detail.insert('end', '\n')
        lb_detail.insert('end', "PORTS:")
        port_list = list()
        port_list = ip_dict[index]['ports'].split(', ')
        lb_detail.insert('end', *port_list)
        lb_detail.insert('end', '\n')
        for i in detail_dict:
            lb_detail.insert('end', '{}:{}'.format(i, detail_dict[i]))
        lb_detail.place(x=230, y=30)

    # delete all the data if user click the
    def data_del():
        lb_ip.delete(0, 'end')
        lb_detail.delete(0, 'end')
        if os.path.exists("all_ip_dict_json"):
            os.remove("all_ip_dict_json")

    def data_out():
        if os.path.exists('ip_紀錄.xlsx'):
            os.remove('ip_紀錄.xlsx')
        print('data_out')
        if os.path.exists('all_ip_dict_json'):
            with open('all_ip_dict_json', 'r') as inputfile:
                ipdict = json.load(inputfile)
            workbook = xlsxwriter.Workbook('ip紀錄.xlsx')
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            worksheet.set_column(0, 0, 15)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 40)

            worksheet.write('A1', 'IP位置', bold)
            worksheet.write('B1', 'IP名字', bold)
            worksheet.write('C1', '埠位', bold)
            worksheet.write('D1', '測試', bold)

            row = 1
            col = 0
            for item in ipdict.keys():
                worksheet.write_string(row, col, ipdict[item]['ip_address'])
                worksheet.write_string(row, col + 1, ipdict[item]['ip_name'])
                worksheet.write_string(row, col + 2, ipdict[item]['ports'])
                worksheet.write_string(row, col + 3, "失敗")
            workbook.close()
        else:
            messagebox.showinfo("錯誤!", "沒有紀錄,請先測試過弱密碼測試在做紀錄")

    ip_dict = {}
    chk_ip_page = tk.Toplevel(main_page)
    chk_ip_page.geometry('600x400')
    chk_ip_page.title('檢視歷史所有ip')
    # chk_ip_page.iconbitmap('icon.ico')

    if os.path.exists('all_ip_dict_json'):
        with open('all_ip_dict_json', 'r') as input_file:
            ip_dict = json.load(input_file)

    lb_ip = tk.Listbox(chk_ip_page,
                       width=30, height=18)
    for ip_count in ip_dict.keys():
        lb_ip.insert(ip_count, ip_dict[ip_count]['ip_address'])
    lb_detail = tk.Listbox(chk_ip_page, width=50, height=18)
    lb_ip.place(x=0, y=30)
    lb_ip.bind('<<ListboxSelect>>', onselectall)

    btn_out = tk.Button(chk_ip_page, text='匯出', command=data_out, width=50)
    btn_out.place(x=110, y=330)

    btn_del = tk.Button(chk_ip_page, text='刪除', command=data_del, width=50)
    btn_del.place(x=110, y=360)


def onselect(evt):
    ip_json = "ip_json"
    with open(ip_json, 'r') as inputfile:
        ipdict = json.load(inputfile)

    w = evt.widget
    index = str(w.curselection()[0])

    detail_dict = ipdict[index]['detail']

    lb_detail = tk.Listbox(main_page, width=50, height=20)
    lb_detail.insert('end', ipdict[index]['ip_name'])
    lb_detail.insert('end', '\n')
    ports_list = ipdict[index]['ports'].split(', ')
    for i in detail_dict:
        lb_detail.insert('end', '{}:{}'.format(i, detail_dict[i]))
    lb_detail.insert('end', '\n')
    lb_detail.insert('end', 'ports:')
    for i in ports_list:
        lb_detail.insert('end', i)
    lb_detail.place(x=230, y=100)


login_state = 0


# login function is successed, use webdriver to open shodan
#   then check the user's account is correct or not
#   and then change the global var. which is login_status
def func_login():
    sign_up_page = tk.Toplevel(main_page)
    sign_up_page.geometry('350x200')
    sign_up_page.title('登入畫面')

    # sign_up_page.iconbitmap('icon.ico')

    def func_login_action():
        input_account = input_user_name.get()
        input_password = input_user_password.get()

        driver.get(BASE_URL + "/login")
        driver.find_element_by_xpath("//input[@id='username']").send_keys(input_account)
        driver.find_element_by_xpath("//input[@id='password']").send_keys(input_password)
        driver.find_element_by_xpath("//input[@name='login_submit']").submit()

        if driver.current_url == "https://account.shodan.io/login":
            messagebox.showinfo('錯誤!', "請重新確認您的帳號密碼是否輸入正確")
        else:
            messagebox.showinfo('成功!', '你已經成功登入shodan!')
            global login_state
            login_state = 1

        if login_state == 1:
            driver.get("https://developer.shodan.io/dashboard")
            page_html = driver.page_source
            page_soup = BeautifulSoup(page_html, 'html.parser')
            user_state = page_soup.find("h2").text
            login_status.config(text="登入狀況:成功" + '\n' +
                                     "登入者帳號為:" + input_account + '\n' +
                                     "此帳號為" + user_state)
            sign_up_page.destroy()

    #    #l.config(text='登入畫面跳出')

    input_user_name = tk.StringVar()
    input_user_name.set('')
    tk.Label(sign_up_page,
             text='請輸入帳號: ').place(x=50, y=10)
    entry_new_name = tk.Entry(sign_up_page,
                              textvariable=input_user_name)
    entry_new_name.place(x=150, y=10)

    input_user_password = tk.StringVar()
    input_user_password.set('')
    tk.Label(sign_up_page, text='請輸入密碼: ').place(x=50, y=40)
    entry_new_password = tk.Entry(sign_up_page,
                                  textvariable=input_user_password,
                                  show="*")
    entry_new_password.place(x=150, y=40)

    btn_confirm_sign_up = tk.Button(sign_up_page,
                                    text='確定輸入',
                                    command=func_login_action)
    btn_confirm_sign_up.place(x=150, y=130)


# just show out the submit page of shodan
def func_submit():
    url = 'https://account.shodan.io/register'
    webbrowser.open_new(url)


# to parse the shodan and make it to the
def func_filter():
    print("開始作業")

    def func_test():
        # writing new ip into all ip_dict_json which record the history ip address and detail
        if os.path.exists("all_ip_dict_json"):
            with open("all_ip_dict_json", 'r') as inputfile:
                allipdict = json.load(inputfile)
            total_len = len(allipdict)
            for i in range(0, len(ip_dict)):
                allipdict[i + total_len] = ip_dict[i]
            with open("all_ip_dict_json", 'w') as outfile:
                json.dump(allipdict, outfile)
        else:
            with open("all_ip_dict_json", 'w') as outfile:
                json.dump(ip_dict, outfile)

    new_filter = input_filter.get()
    temp_time_filter = input_time.get()
    time_filter = int(temp_time_filter)
    ip_dict = {}
    port_list = list()
    ip_list = list()
    ip_name_list = list()
    global login_state

    if os.path.exists("all_ip_dict_json"):
        with open("all_ip_dict_json", 'r') as inputfile:
            allipdict = json.load(inputfile)
    else:
        allipdict = {}

    if login_state == 1:  #
        driver.get(SEARCH_URL)
        # input filter and search in shodan
        driver.find_element_by_xpath("//input[@id='search_input']").send_keys(new_filter)
        driver.find_element_by_xpath("//Button[@class='btn btn-primary btn-small submit']").submit()

        # because everypage have 10 datasets so divide 10 to count how many pages need to be crawl
        for times in range(0, int(time_filter / 10)):
            # just crawling
            page_html = driver.page_source
            page_soup = BeautifulSoup(page_html, 'html.parser')
            page_findTAG = page_soup.find_all(class_="search-result")

            # because we have 10 datasets of every pages then we need to get everyone's ip address
            # so use double loop and using ip_list to record the ip_address
            for i in range(0, 10):
                for j in page_findTAG[i].find_all(class_="search-result-summary"):
                    if j.find(class_="details"):
                        ip_link = j.find(class_='details').get('href')
                        ip_list.append(ip_link.split('/')[2])
                str_ip_name = page_findTAG[i].find(class_="ip").text
                ip_name_list.append(str_ip_name)
            next_page = driver.find_element_by_link_text('Next')
            next_page.click()
        # crawling for ips' ports
        for j in range(0, time_filter):
            driver.get(SEARCH_URL + "/host/" + ip_list[j])
            page_html = driver.page_source
            page_soup = BeautifulSoup(page_html, 'html.parser')
            page_findIP = page_soup.find_all("meta", attrs={'name': 'twitter:description'}, content=True)
            port_list = list()

            page_findDT = page_soup.find("table", attrs={"class": "table"})
            td_list = list()
            th_list = list()
            for td_tags in page_findDT.find_all("td"):
                td_list.append(td_tags.get_text())
            for th_tags in page_findDT.find_all("th"):
                th_list.append(th_tags.get_text())

            dt_dict = dict(zip(td_list, th_list))
            for i in page_findIP:
                temp = str(i)
                step_1 = temp.split('Ports open: ')
                ports = step_1[1].split('"')
                port_list.append(ports[0])
            ip_dict[j] = {
                "ip_address": ip_list[j],
                "ip_name": ip_name_list[j],
                "detail": dt_dict,
                "ports": port_list[0],
            }
    else:
        messagebox.showinfo("警告!", "請先確認是否有登入成功!")

    with open("ip_json", 'w') as outfile:
        json.dump(ip_dict, outfile)

    lb_ip = tk.Listbox(main_page,
                       width=30, height=20)
    for ip_count in ip_dict.keys():
        lb_ip.insert('end', ip_dict[ip_count]['ip_address'])
    lb_ip.place(y=100)
    lb_ip.bind('<<ListboxSelect>>', onselect)

    btn_test = tk.Button(main_page,
                         text='進行測試',
                         command=func_test)
    btn_test.place(x=515, y=75)
    messagebox.showinfo("搜尋完成!", "搜尋完成囉!")


# let user can do the
def auto_filter():
    new_filter = input_filter.get()
    temp_time_filter = input_time.get()
    time_filter = int(temp_time_filter)

    if state.get() == 1:
        if input_auto_time.get():
            left_time = int(input_auto_time.get())
            if new_filter and time_filter:
                go_filter = Timer(left_time * 60, func_filter)
                go_filter.start()
            #                    func_filter()

            #            if input_time.get():
            #                schedule.every(int(input_time.get())).minutes.do(func_filter)
            else:
                messagebox.showinfo("警告", "沒輸入查詢關鍵字")
        else:
            messagebox.showinfo("警告!", "請確認是否有輸入正確資料")


if __name__ == '__main__':
    # calling tk function to create a now geometry
    main_page = tk.Tk()
    main_page.title('主畫面')
    main_page.geometry('600x600')
    # mainpage.iconbitmap('icon.ico')

    # global login status record the user is login or not
    login_status = 0

    # show the user is login or not
    # if user input correct api then show login success
    # else if user doesn't login success or haven't input user api then show login unsuccess

    tk.Label(main_page, text='登入狀況:失敗').pack()

    # main page show a listbox record the filter which user input
    # havn't done:
    # first:user input the filter,
    # second:record the filters which user input in the past
    # third:record api and users relevance
    input_filter = tk.StringVar()
    input_time = tk.StringVar()
    input_filter.set('')
    input_time.set('')
    tk.Label(main_page,
             text="請輸入要篩選之資料:").place(x=60, y=50)
    entry_filter = tk.Entry(main_page,
                            textvariable=input_filter,
                            width=25).place(x=180, y=50)
    input_auto_time = tk.StringVar()
    input_new_time = tk.Entry(main_page,
                              textvariable=input_auto_time,
                              width=3)

    lb_time = tk.Label(main_page,
                       text="分")
    input_new_time.place(x=180, y=75)
    lb_time.place(x=210, y=75)

    tk.Label(main_page,
             text="遞迴搜尋:").place(x=225, y=75)
    state = tk.IntVar()
    loop_ck_btn = tk.Checkbutton(main_page,
                                 variable=state,
                                 command=auto_filter)

    loop_ck_btn.place(x=285, y=73)

    tk.Label(main_page,
             text="請輸入要搜尋之資料量:").place(x=350, y=50)

    entry_filter = tk.Entry(main_page,
                            textvariable=input_time,
                            width=5).place(x=480, y=50)

    btn_filter = tk.Button(main_page,
                           text="送出",
                           command=func_filter).place(x=525, y=47)

    lb_filter = tk.Listbox(main_page,
                           width=50, height=8)
    lb_filter.place(x=120, y=440)

    lb_filter.insert('end', '1.搜尋特定ip(以中國杭州某廣告公司為例):')
    lb_filter.insert('end', 'net:"121.42.78.115"')
    lb_filter.insert('end', '2.搜尋特定國家(以中國大陸為例):')
    lb_filter.insert('end', 'country:"CN"')
    lb_filter.insert('end', '3.搜尋特定port(以80為例):')
    lb_filter.insert('end', 'port:"80"')
    lb_filter.insert('end', '4.搜尋某os系統(以Windows XP為例):')
    lb_filter.insert('end', 'os:"Windows XP"')
    lb_filter.insert('end', '5.搜尋特定城市(以北京為例):')
    lb_filter.insert('end', 'city:"Beijing"')
    lb_filter.insert('end', '6.搜尋特定網域(以edu為例):')
    lb_filter.insert('end', 'hostname:"edu"')
    lb_filter.insert('end', '7.搜尋特定產品(以mongodb為例):')
    lb_filter.insert('end', 'product:"mongodb"')

    # create menubar

    menu_bar = tk.Menu(main_page)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='檢視', menu=file_menu)
    file_menu.add_command(label='所有IP', command=check_all)
    file_menu.add_separator()
    file_menu.add_command(label='關閉', command=shutdown)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='設定', menu=edit_menu)
    edit_menu.add_command(label='登入', command=func_login)
    edit_menu.add_separator()
    edit_menu.add_command(label='註冊', command=func_submit)

    main_page.config(menu=menu_bar)

    main_page.mainloop()
