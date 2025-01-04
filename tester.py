
from src.modules.engine.smart_bot import SmartBot
class Testme:
    def __init__(self):
        self.controller =self
        self.controller.secret_key="SB6V5FQFUB2EBHYW3O3K2C4DFR5CB2X6HX2AZCMG5TY7AM5VK6GYW4EJ"
        self.controller.account_id= "GALWHPINY5E3NEUQAZMNSXJXDAD3ZDEJYK4CZRVLATBNHFGKZRLOZBBK"
        SmartBot(controller=self).start()

if __name__ == "__main__":
    Testme()



