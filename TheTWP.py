import pyIRC, TWPTwitter, TWPStocks, re, sys

CHAN		= '#TimeWastePool'
NICK		= 'TheTWP'
AUTOJOIN	= True
TWITTER_KEYS= {
	'ck'	: open('t_ck').read().rstrip('\n'),
	'cs'	: open('t_cs').read().rstrip('\n'),
	'atk'	: open('t_atk').read().rstrip('\n'),
	'ats'	: open('t_ats').read().rstrip('\n')
}
COMMANDS = {
	'!follow'		: ['USAGE: !follow @twitter_user','DESCRIPTION: adds @twitter_user to the database table of users we follow'],
	'!unfollow'		: ['USAGE: !unfollow @twitter_user','DESCRIPTION: removes @twitter_user to the database table of users we follow'],
	'!twitterlist'	: ['USAGE: !twitterlist','DESCRIPTION: send you a list of all the users we are following on Twitter'],
	'!watchstock'	: ['USAGE: !watchstock stocksymbol', 'DESCRIPTION: adds a stock symbol to the table of stock symbols we watch'],
	'!removestock'	: ['USAGE: !remove stocksymbol', 'DESCRIPTION: removes a stock sybmol from the table of stock symbols we are watching'],
	'!stockprice'	: ['USAGE: !stockprice stocksymbol', 'DESCRIPTION get the price of one share of the given stock sybmol'],
	'!help'			: ['USAGE: !help','DESCRIPTION: you are literally using this right now...']
}

def GetNick(msg):
	return msg[1:msg.index('!')]

def CheckHelp(msg):
	if msg.find(COMMANDS.keys()[-1]) != -1:
		help_nick = GetNick(msg)
		BOT.send_msg(help_nick, '========== TheTWP Help ==========')
		for cmd in COMMANDS:
			BOT.send_msg(help_nick, cmd)
			BOT.send_msg(help_nick, "     %s" % COMMANDS[cmd][0])
			BOT.send_msg(help_nick, "     %s" % COMMANDS[cmd][1])
		BOT.send_msg(help_nick, '=================================')
		
def CheckWatchStock(msg):
	validation = re.search('\!watchstock\s(\w{1,5})', msg)
	if validation:
		BOT.send_msg(GetNick(msg), STOCKS.watch_stock(validation.group(1)))
	
def CheckRemoveStock(msg):
	validation = re.search('\!removestock\s(\w{1,5})', msg)
	if validation:
		BOT.send_msg(GetNick(msg), STOCKS.remove_stock(validation.group(1)))
	
def CheckStockPriceReq(msg):
	validation = re.search('\!stockprice\s(\w{1,5})', msg)
	if validation:
		BOT.send_msg(CHAN, STOCKS.get_stockprice(validation.group(1)))		

def CheckOpenPrices():
	data = STOCKS.get_open_ticker()
	if data:
		BOT.send_msg(CHAN, STOCKS.get_open_ticker())
	
def CheckClosePrices():
	data = STOCKS.get_close_ticker()
	if data:
		BOT.send_msg(CHAN, STOCKS.get_close_ticker())
			
def CheckFollow(msg):
	validation = re.search('\!follow\s@(.+)', msg)
	if validation:
		BOT.send_msg(GetNick(msg), TWITTER.start_following(validation.group(1)))

def CheckUnfollow(msg):
	validation = re.search('\!unfollow\s@(.+)', msg)
	if validation:
		BOT.send_msg(GetNick(msg), TWITTER.stop_following(validation.group(1)))
		
def CheckTwitterList(msg): # HAS NOT BEEN TESTED YET!
	validation = re.search('\!twitterlist', msg)
	if validation:
		twitter_list = ', '.join(TWITTER.get_following())
		BOT.send_msg(GetNick(msg), twitter_list)
	
def CheckTweets():
	tweets = TWITTER.get_tweets()
	if tweets:
		for tweet in tweets:
			BOT.send_msg(CHAN, tweet)
			
def CheckKillSelf(msg):
	validation = re.search('\!killyourself', msg)
	if validation and GetNick(msg) == 'DW3B':
		sys.exit()
		
def MainLoop():
	while True:
		message = BOT.check_messages()
		CheckOpenPrices()
		CheckClosePrices()
		CheckWatchStock(message)
		CheckRemoveStock(message)
		CheckStockPriceReq(message)
		CheckHelp(message)
		CheckFollow(message)
		CheckUnfollow(message)
		CheckTweets()
		
STOCKS = TWPStocks.TWPStocks()
		
TWITTER = TWPTwitter.TWPTwitter(ck=TWITTER_KEYS['ck'], cs=TWITTER_KEYS['cs'], atk=TWITTER_KEYS['atk'], ats=TWITTER_KEYS['ats'])

BOT = pyIRC.Bot(chan=CHAN, nick=NICK, autojoin=AUTOJOIN)
BOT.connect()

try:
	MainLoop()
except KeyboardInterrupt:
	sys.exit()
