from yahoo_finance import Share
import sqlite3, datetime

class TWPStocks(object):
	def __init__(self):
		self.sql			= sqlite3.connect('twp_stocks.db')
		self.cur			= self.sql.cursor()
		self.posted_open	= None
		self.posted_close	= None

		self.cur.execute('CREATE TABLE IF NOT EXISTS stocks(symbol TEXT)')
		self.sql.commit()		
		
	def get_all_stocks(self):
		stocks = self.cur.execute('SELECT symbol FROM stocks').fetchall()
		stock_list = []
		if len(stocks) > 0:
			for stock in stocks:
				stock_list.append(stock[0])
		return stock_list
			
	def get_stockprice(self, sym):
		stock = Share(sym)
		if stock:
			return "%s (%s): $%s [%s]"	% (stock.symbol.upper(), stock.data_set['Name'], stock.get_price(), stock.get_change())
			
	def watch_stock(self, sym):
		stock_test = Share(sym.upper())
		if not stock_test:
			return 'No stock with that symbol'
		if not sym.upper() in self.get_all_stocks():			
			self.cur.execute('INSERT INTO stocks VALUES(?)', (sym.upper(),))
			self.sql.commit()
			return 'Success'
		elif sym.upper() in self.get_all_stocks():
			return 'Already watching that symbol'

	def remove_stock(self, sym):
		if sym.upper() in self.get_all_stocks():
			self.cur.execute('DELETE FROM stocks WHERE symbol=?', (sym.upper(),))
			self.sql.commit()
			return 'Success'
		elif not sym.upper() in self.get_all_stocks():
			return 'Not watching that symbol'		
			
	def get_open_ticker(self):
		date = datetime.datetime.now()
		weekday = date.weekday()
		if (datetime.time(07,30,30) < date.time() < datetime.time(07,31,30)) and (weekday != 5 or weekday != 6) and (self.posted_open == None or self.posted_open < date.date()):
			stock_prices = []
			all_stocks = self.get_all_stocks()
			if all_stocks:
				for stock in all_stocks:
					stock_info = Share(stock)
					stock_prices.append('%s: $%s [%s]' % (stock_info.symbol.upper(), stock_info.get_open(), stock_info.get_change()))
				self.posted_open = date.date()
				return ' - '.join(stock_prices)
		else:
			return False
			
	def get_close_ticker(self):
		date = datetime.datetime.now()
		weekday = date.weekday()
		if (datetime.time(16,00,30) < date.time() < datetime.time(16,01,30)) and (weekday != 5 or weekday != 6) and (self.posted_close == None or self.posted_close < date.date()):		
			stock_prices = []
			all_stocks = self.get_all_stocks()
			if all_stocks:
				for stock in all_stocks:
					stock_info = Share(stock)
					stock_prices.append('%s: $%s [%s]' % (stock_info.symbol.upper(), stock_info.get_prev_close(), stock_info.get_change()))
				self.posted_close = date.date()
				return ' - '.join(stock_prices)
		else:
			return False