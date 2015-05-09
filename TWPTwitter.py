import twitter, sqlite3, datetime, re

class TWPTwitter(object):
	
	def __init__(self, ck, cs, atk, ats):
		self.ck		= ck
		self.cs		= cs
		self.atk	= atk
		self.ats	= ats
		self.sql	= sqlite3.connect('twp_twitter.db')
		self.cur	= self.sql.cursor()
		self.api	= twitter.Api(consumer_key=self.ck, consumer_secret=self.cs, access_token_key=self.atk, access_token_secret=self.ats)
		self.last_status_pull	= datetime.datetime.now()
		
		# Create tables needed to manage posts and users we are following on Twitter
		self.cur.execute('CREATE TABLE IF NOT EXISTS oldposts_twitter(id TEXT)')
		self.cur.execute('CREATE TABLE IF NOT EXISTS following(name TEXT)')
		self.sql.commit()
		
		# Add all users we are following on Twitter to the 'following' table on initialization
		# This prevents additional API calls by letting us query our own database
		self.initial_following = self.api.GetFriends()
		if len(self.initial_following) > 0:
			for user in self.initial_following:
				self.start_following(user.screen_name)

	def start_following(self, name):
		# Verifies that a valid user account was given
		try:
			twitter_user = self.api.GetUser(screen_name=name)
		except:
			return 'Could not find user with that nickname'
		
		# Checks to make sure we are not already following the user before adding them to the table			
		self.cur.execute('SELECT name FROM following WHERE name=?', (name,))
		if not self.cur.fetchone():
			self.api.CreateFriendship(screen_name=name)
			self.cur.execute('INSERT INTO following VALUES(?)', (name,))
			self.sql.commit()
			return 'Success'
		else:
			return 'User account exists in table'
			
	def stop_following(self, name):
		# Removes a user from the 'following' table if it exists
		self.cur.execute('SELECT name FROM following WHERE name=?', (name,))
		if self.cur.fetchone():
			self.api.DestroyFriendship(screen_name=name)
			self.cur.execute('DELETE FROM following WHERE name=?', (name,))
			self.sql.commit()
			return 'Success'
		else:
			return 'Not following @%s' % user
		
	def get_following(self):
		# Returns a list of names of all the users we are following on Twitter
		following = []
		name_tuples = self.cur.execute('SELECT name FROM following').fetchall()
		if len(name_tuples) > 0:
			for name in name_tuples:
				following.append(name[0])
		return following
		
	def get_new_status(self, name):
		# Returns a formatted version of a user's status as well as the status ID
		tweet = self.api.GetUser(screen_name=name).status
		if tweet and not tweet.in_reply_to_user_id:
			self.cur.execute('SELECT * FROM oldposts_twitter WHERE id=?', (tweet.id,))
			if not self.cur.fetchone():
				self.cur.execute('INSERT INTO oldposts_twitter VALUES(?)', (tweet.id,))	
				self.sql.commit()			
				tweet = tweet.text.replace('\n', ' ')
				return '[@%s]: %s' % (name, tweet)
			else:
				return False
		else:
			return False
			
	def get_tweets(self): 
		tweets = []
		if (datetime.datetime.now() - self.last_status_pull).seconds > 30:
			names = self.get_following()
			if names:
				for name in names:
					status = self.get_new_status(name)
					if status:
						print status
						tweets.append(status)
				self.last_status_pull = datetime.datetime.now()
				return tweets