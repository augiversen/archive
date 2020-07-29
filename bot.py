### Boot

import discord
from discord.ext import commands
import sqlite3
import vars

# Sets up bot and database connection.
bot = commands.Bot(command_prefix = 'a!')
db = sqlite3.connect('users.db')
c = db.cursor()

# Debug, confirms bot is running & commands have been loaded properly.
@bot.event
async def on_ready():
    print(f'Running {bot.user}.')

### Commands

# Returns your level.
@bot.command(brief = 'Gamification!', description = 'Shows how big brain you are.')
async def level(ctx):
	user = ctx.author.id
	c.execute('''SELECT * FROM users WHERE user_id = ?''', (user,))
	query = c.fetchone()
	if query:
		level = query[1]
		await ctx.send(f'`Level {level}.`')
	else:
 		await ctx.send(f'`Level 0. Try contributing something!`')
    
# Returns a leaderboard with the users that have contributed the most to #archive.
@bot.command(brief = 'Returns level leaderboard.', description = 'REALLY shows how big brain you are.')
@commands.guild_only()
async def leaderboard(ctx, page: int = 1):
	page = (page * 10) - 10
	c.execute('''SELECT * FROM users LIMIT 10 OFFSET ?''', (page,))
	query = c.fetchall()
	if query:
		string = ''
		rank = page + 1
		for i in query:
			user = bot.get_user(i[0])
			if user:
				string += f'[{rank}.] {user.name}: level {i[1]}.\n'
			else:
				string += f'[{rank}.] No longer in server: level {i[1]}.\n'
			rank += 1
		await ctx.send(f'```ini\n{string}```')
	else:
		await ctx.send('No entries on this page!')

### Other

# Checks for uploads to #archive.
@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if message.author.id == bot.user.id:
			return
	if str(message.channel) == 'archive' and message.attachments:
		user = message.author.id
		c.execute('''SELECT * FROM users WHERE user_id = ?''', (user,))
		query = c.fetchone()
		if query:
			level_up = query[1] + 1
			c.execute('''UPDATE users SET score = ? WHERE user_id = ?''', (level_up, user,))
		else:
			c.execute('''INSERT INTO users(user_id, score) VALUES (?, 1)''', (user,))
		db.commit()

bot.run(vars.token)