
# import
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime

# Go
class MagtiFun:
    '''
        კლასი საშუალებას გვაძლევს Magtifun.ge-ის გამოყენებით
        შეტყობინებები გავგზავნოთ ინტერნეტ ბრაუზერის გარეშე.
        
        არგუმენტები ობიექტის შექმნისას:
            1. მოხმარებლის სახელი ავტორიზაციისთვის
            2. მომხმარებლის პაროლი ავტორიზაციისთვის
            3. log-ის ფაილის მდებარეობა - (არასავალდებულო) - 
            სად შევინახოთ log-ი.
            თუ არ არის მითითებული, არსებულ საქაღალდეში იქმნება log.txt ფაილი.
    '''

    # all instances will have access to these links
    urls = {  
        'login'        :'http://www.magtifun.ge/',
        'login_proc'   :'http://www.magtifun.ge/index.php?page=11&lang=ge',
        'sms_page'     :'http://www.magtifun.ge/index.php?page=2&lang=ge',
        'message_send' :'http://www.magtifun.ge/scripts/sms_send.php'
    }


    def __init__(self, username, password, log_file = None):
        self.username = username
        self.password = password
        self.log_file = "log.txt" if log_file is None else log_file


    def update_login_log(self, status):
        '''
            შევიტანოთ ინფორმაცია ავტორიზაციის შესახებ ლოგის ფაილში
            ფორმატით:
                დრო, მომხმარებლის ნომერი, 
                ავტორიზაციის სტატუსი(+/-  ---  წარმატებული/წარუმატებელი),
                ბალანსი('N/A', თუ სტატუსია -)
        ''' 
        with open(self.log_file, "ba") as f:
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S") 

            text = (time + f"| ავტორიზაცია მომხმარებლისთვის {self.username} "
                           f"|{'+' if status else '-'}|"
                           f" ბალანსი: {self.balance if status else 'N/A'}")

            f.write((text + "\r\n").encode("utf-8"))  


    def update_messages_log(self, number, message, server_resp):
        ''' 
            ჩავწეროთ ლოგის ფაილში ინფორმაცია შეტყობინების შესახებ 
            ფორმატით:
                გაგზავნის დრო, ნომერი, სერვერისგან მიღებული პასუხი, 
                დარჩენილი ბალანსი(გაგზავნის შემდეგ), გაგზავნილი შეტყობინების ტექსტი
        ''' 
        with open(self.log_file, "ba") as f:
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            f.write(
                    (time +
                    "| ნომერი: " + number                         + 
                    " | სტატუსი: " + server_resp.center(10)        + 
                    " | ბალანსი: " + str(self.balance)             +
                    " | sms: " + message                           +
                    "|\r\n").encode("utf-8"))


    def login(self):
        '''
            წარმატებული ავტორიზაციის შემთხვევაში, შედეგად ვიღებთ True-ს,
            სხვა შემთხვევაში, False-ს.
        '''
        headers = {'User-Agent': \
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', 
                   'Referer': 'http://www.magtifun.ge/index.php?page=2&lang=ge'
                }
        s = requests.Session() 

        self.session = s; 
        s.headers.update(headers)

        # user info
        info = {'user': self.username, 'password': self.password}

        self.soup = bs(s.get(self.urls['login']).text, 'html.parser')
        info['csrf_token'] = self.soup.select('input[name="csrf_token"]')[0]['value']
        
        # get login page
        answer = s.post(self.urls['login_proc'], data=info);
        answer.encoding = "utf-8"
        self.soup = bs(answer.text, "html.parser") 
        
        # logged in or not?
        if "თქვენს ანგარიშზეა" in answer.text:
            self.get_balance()
            self.update_login_log(True)
            return True

        self.update_login_log(False)
        return False
        

    def get_balance(self):
        ''' 
            გვეხმარება მივიღოთ ბალანსი & განვაახლოთ token
        '''  
        s = self.session
        soup = bs(s.get(self.urls['sms_page']).text, "html.parser")
        div = soup.select('div.menu_list')[0]
        balance = int(div.find_all("span")[1].text)

        token = soup.find("input", {'name':'csrf_token'})['value']
        self.balance = balance
        self.token = token

        return balance


    def send_messages(self, numbers, messages):
        '''
            ყველა შეტყობინების წარმატებით გაგზავნის შემთხვევაში ვიღებთ შედეგს True, 
            სხვა შემთხვევაში, False-ს. 
            ინფორმაცია ინდივიდუალური შეტყობინებებისთვის ინახება log-ის ფაილში.

            ფუნქცია არ ახდენს არგუმენტთა მნიშვნელოვნად შემოწმებას, შესაბამისად, მის გამოყენებამდე 
            დარწმუნდით, რომ ყველა პარამეტრი სწორად არის მითითებული

            არგუმენტები:
                1. numbers - 1 ან რამდენიმე ნომერი სადაც ვგზავნით შეტყობინებას
                2. messages - 1 ან რამდენიმე შეტყობინება ნომრების შესაბამისად
                
            მაგალითად:
                1 შეტყობინების გაგზავნის შემთხვევაში numbers 
                შეიძლება იყოს როგორც "123456678", ისე ["123456678"]

                messages კი როგორც "სალამი magtifun-იდან", ისე ["სალამი magtifun-იდან"]
        '''

        # check login status
        if not hasattr(self, "token"): return False

        if not isinstance(numbers, list): numbers = [numbers]
        if not isinstance(messages, list): messages = [messages]

        s = self.session
        resps = [] # to check that server said * is ok

        for number, message in zip(numbers, messages):

            send_me = {"csrf_token": self.token, 
                       "recipients": number, 
                       "message_body": message}
            # save response text
            server_resp = s.post(self.urls['message_send'], data=send_me).text

            self.get_balance() # update balance & token

            self.update_messages_log(number, message, server_resp)
            resps.append(server_resp)

        # decide what to return
        for resp in resps:
            if resp.lower() != "success":
                return False
        return True
