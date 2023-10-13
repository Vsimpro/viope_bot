# Libraries
import os

# Modules
from modules import viope
from dotenv import load_dotenv

load_dotenv()


# Global variables
COURSE_ID   = os.getenv("COURSE_ID")
CREDENTIALS = {
    "username" : os.getenv("CREDENTIALS_USERNAME"),
    "password" : os.getenv("CREDENTIALS_PASSWORD")
}

OPENAI_KEY  = os.getenv("OPENAI_KEY")
OPENAI_ORG  = os.getenv("OPENAI_ORG")


def main():

    bot = viope.Bot( 
        course_id=COURSE_ID,
     
        openai_key=OPENAI_KEY,
        openai_org=OPENAI_ORG,
     
        username=CREDENTIALS["username"], 
        password=CREDENTIALS["password"]
    )

    # rock n roll buddy
    try:
        bot.begin()

        while 1:
            pass 
    
    except KeyboardInterrupt:
        bot.close()
        exit()



if __name__ == "__main__":
    main()
    