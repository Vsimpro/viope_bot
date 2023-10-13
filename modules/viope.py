import openai
import time, json, requests

from selenium import webdriver
from selenium.webdriver.common.keys          import Keys
from selenium.webdriver.common.action_chains import ActionChains


class Bot:
    def __init__(self, username, password, course_id, openai_org, openai_key):
        self.course_id = course_id

        self.username = username
        self.password = password

        self.openai_key = openai_key
        self.openai_org = openai_org

        self.cookie = None

        # poor mans mongodb
        self.storage = {
            "modules"        : {},
            "module_amnt"   : 0,
            "current_module" : 1,
        }

        self.js_junk = ""
        with open("js_junk.js", "r") as file:
            self.js_junk = "".join(file.readlines()).strip().replace( "\n", " " ).replace( "\t", " " ).replace( "\r", " " )


        self.driver = None

        
#   === BOT FUNCTIONALITIES ===
    # This is the main loop of the bot.
    def begin(self):
        # Prepare selenium
        try:
            self.driver = webdriver.Firefox()
            self.driver.get("https://vw4.viope.com/")  

        except Exception as e:
            print( "[!] Could not open the browser. Details:  ", e)
            self.close()

        print( "[*] Window opened. " )

        self.login()
        self.select_course()

        # Go Through all the exercises:
        self.get_course_modules()

        counter = 0
        for module_nmbr in range(1, self.storage["module_amnt"] + 1):
            self.do_module( module_nmbr )
            time.sleep( 2 / 10 )

            counter += 1

            # When testing, break after 1st
            if counter > 1:
                pass
                #break

        print( "[*] Stopping. Goodbye." )
        return 0
    

    def close(self):
        try:
            self.driver.close()
        except Exception as e:
            exit( 1 )

        exit( 0 )

#   === SITE FUNCTIONALITIES ===

    def login(self):
        self.driver.find_element(by="xpath", value="//input[@name='username']").send_keys(self.password)        
        self.driver.find_element(by="xpath", value="//input[@name='password']").send_keys(self.password)        
        self.driver.find_element(by="xpath", value="//button[@type='submit']").click()
                
        print( "[*] Logged in as: ", self.username )
        return 0
    

    def select_course(self):

        time.sleep( 2 / 10 )

        try:
            self.driver.find_element(by="xpath", value=f"//a[@href='/student/{self.course_id}/']").click()
        except Exception as e:
            print( "[!] Ran into an error selecting the desired course. Is the ID correct: ", self.course_id )
            print( "[!] More details: ", e )
            return 1
        
        print( f"[*] Course {self.course_id} opened. " )
        return 0
    

    def get_course_modules(self):

        time.sleep( 1 )

        try:
            module_buttons = self.driver.find_elements(by="xpath", value="//button[@ng-repeat='st_ch in student_chapters']")

        except Exception as e:
            print( "[!] Could not find buttons. Is the course open..? Details: ", e )
            return 1

        print( "[..] Refreshing module buttons" )
        self.storage["module_amnt"] = 0
        for button in module_buttons:
        
            _number = button.get_attribute("textContent").strip()
            self.storage["module_amnt"] += 1
            self.storage["modules"][_number] = button
            

        return 0
    
    def do_module( self, module ):
        print( "[*] Beginning module: ", str(module).replace("_", " ").replace("button", "") )
        
        # Open module
        self.get_course_modules()
        for module_number in range(1, self.storage["module_amnt"] + 1):
            if module_number == module:
                self.storage["modules"][str(module_number)].click()
                break

        time.sleep( 2 / 10 )

        # Open Programming exc.
        self.driver.find_element(by="xpath", value="/html/body/div[4]/div[1]/div[2]/ul/li[2]/a").click()
        time.sleep( 1 )

        page = self.driver.find_element(by="xpath", value="/html/body/div[4]/div[2]/div[1]/div/div[1]/div/div[1]/button/span[3]").get_attribute("textContent").strip()
        page_now = page.split("/")[0] 
        page_max = page.split("/")[1]       

        for _ in range(int(page_now), int(page_max) + 1):

            # Get the Task at hand: 
            task_number = self.driver.current_url.split("/#/prog/")[1].split("/")[1]
            task_element = self.driver.find_element(by="xpath", value="//div[@id='description_text']")
            
            task_instructions = task_element.text
            # Prompt magic
            prompt_eng = "Give me example as code. Do not state what language the code is in. Please refrain from explaining the code, simply provide me with Python that fits the task. Please give only the working. Remove everything else from your response. Provide only Python. don't include the question in your response."
            prompt = task_instructions + "\n" +prompt_eng

            # Switch to API handling:
            print( "[*] Starting to solve", task_number)
            self.solve_task(task_number, prompt)

            # Move to next task on the list.
            # self.driver.find_element(by="xpath", value="/html/body/div[4]/div[2]/div[1]/div/div[1]/div/button[4]").click()
            print("[*] Moving to next task")
            time.sleep( 1 )



        return 0 
    

    def send_code(self, code):
        # /student/11596/#/prog/100942/126535
        # /student/11596/exercise/100942/126535/exercise_submit
        # Parse ID's
        try:
            url_ids = self.driver.current_url.split("/#/prog/")[1]
            chapter_id  = url_ids.split("/")[0] 
            template_id = url_ids.split("/")[1]
            
        except Exception as e:
            print( "[*] Could not parse URL. Are we on the task page..? Details: ", e )
            if "Alert Text" in str(e):
                pass

            else:
                return 1

        # Generate URL
        url = f"https://vw4.viope.com/student/{self.course_id}/exercise/{chapter_id}/{template_id}/exercise_submit"

        # Check cookies
        if self.cookie == None:
            for cookie in self.driver.get_cookies():
                if cookie["name"] == 'dancer.session':
                    self.cookie = cookie["value"]

        cookies = {
            "dancer.session" : self.cookie,
            "lang" : "en"
        }

        # Craft headers 
        headers = {
            "Host": "vw4.viope.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://vw4.viope.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }

        # Craft Data
        data =  {
            "exercise_template_id": int(template_id),
            "chapter_id": int(chapter_id),
            "exercise_type":"prog",
            "answer":[ { 
                    "partial_start":None,
                    "filename":"ohjelma.py",
                    "file_group_type":"answer",
                    "exercise_template_id": int(template_id),
                    "partial_end":None,
                    "content": f"{code}"
                }],
            "action":"test"
        }

        json_data = json.dumps(data)
        
        response = requests.post( url=url, data=json_data, cookies=cookies, headers=headers )
        
        if response.status_code == 200:
            return response.text

        return None


    def save_code(self, code):

        # Parse ID's
        try:
            url_ids = self.driver.current_url.split("/#/prog/")[1]
            chapter_id  = url_ids.split("/")[0] 
            template_id = url_ids.split("/")[1]
            
        except Exception as e:
            print( "[*] Could not parse URL. Are we on the task page..? Details: ", e )

            if "Alert Text" in str(e):
                pass

            else:
                return 1

        # Generate URL
        url = f"https://vw4.viope.com/student/{self.course_id}/exercise/{chapter_id}/{template_id}/exercise_submit"

        # Check cookies
        if self.cookie == None:
            for cookie in self.driver.get_cookies():
                if cookie["name"] == 'dancer.session':
                    self.cookie = cookie["value"]

        cookies = {
            "dancer.session" : self.cookie,
            "lang" : "en"
        }

        # Craft headers 
        headers = {
            "Host": "vw4.viope.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://vw4.viope.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }

        # Craft Data
        data =  {
            "exercise_template_id": int(template_id),
            "chapter_id": int(chapter_id),
            "exercise_type":"prog",
            "answer":[ { 
                    "partial_start":None,
                    "filename":"ohjelma.py",
                    "file_group_type":"answer",
                    "exercise_template_id": int(template_id),
                    "partial_end":None,
                    "content": f"{code}"
                }],
            "action":"save"
        }

        json_data = json.dumps(data)
        
        response = requests.post( url=url, data=json_data, cookies=cookies, headers=headers )
        
        if response.status_code == 200:
            return response.text

        return None


    def get_code(self, prompt):
        code = ""

        openai.organization = self.openai_org
        openai.api_key      = self.openai_key

        # Send the prompt to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant, providing me Python code."},
                {"role": "user",   "content": prompt},
            ]
        )

        try:
            code = str(response["choices"][0]["message"]["content"])
            if "```" in code:
                code = code.split("```")[1].split("```")[0] 

        except Exception as e:
            print( "[!] Could not parse GPT results. Details:", e )
            print( response )

        time.sleep( 1 )
        return code 


    def solve_task(self, task_number, prompt):

        # detect page change:
        start_uri = self.driver.current_url

        # Start code iteration
        fix = ""
        data = None
        java_script_junk = self.js_junk 
        while 1:

            # Try to skip before generating code:
            self.driver.execute_script(java_script_junk)
            
            if start_uri != self.driver.current_url: 
                print( "[+] Task was done. skipping." )
                return 0

            time.sleep( 1 )

            # Get ChatGPT response:
            code = self.get_code(prompt + fix)
            result = self.send_code(code)
            
            if result != None:
                error_message = ""
                try:
                    # I love Viope <3
                    data = json.loads(result)
                    
                    try:
                        for _json in data["runtimes"]:
                            if 'art_msg' in _json: 
                                error_message = _json['art_msg']
                    
                    except KeyError:
                        error_message = data['art_msg']

                except Exception as e:
                    print( data )
                    print( "[!] Output from API different than expected. Details:  ", e )
                    return 1
            
                if error_message != "":

                    # Check for mismatch in expected output
                    if error_message == "Your program's output is shorter than expected":
                        print( data["right"]  )

                    print( "[?] Error: ", error_message )
                    print( "[?] Code:", code)
                    print( "[!] Task", task_number, "failed. Get new response from GPT?" )
                    fix = "Code you provided last time: " + code + ". It produces this error: " + error_message + ". Fix your code so that it works."
                    
                    # Refresh browser.
                    self.driver.refresh()
                    continue
                    
                if error_message == "":
                    try:
                        data = json.loads(result)
                        
                    except Exception as e:
                        print( "[!] Output from API different than expected. Details:  ", e )
                        return 1

                    print( "[*] Task ", task_number,  "done." )

                     # This is a hack but if it works.
                    self.save_code(code)

                    time.sleep( 1 )

                    # Refresh, check
                    self.driver.refresh()
                    
                    #TODO: Move to file
                    print( "[*] Prepare to submit " )
                    self.driver.execute_script(java_script_junk)
                    time.sleep( 6 )
                    break

        return 