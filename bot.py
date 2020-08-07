### Boot

import discord
from discord.ext import commands
import sqlite3
import config

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
 		await ctx.send('`Level 0. Try contributing something!`')

# Returns your server rank, wouldn't function with ROW_NUMBER() for some reason.
@bot.command(brief = 'Competition!', description = 'REALLY shows how big brain you are.')
async def rank(ctx):
	user = ctx.author.id
	rank = 1
	c.execute('''SELECT user_id FROM users ORDER BY score DESC''')
	query = c.fetchall()
	for user_id in query:
		if user_id[0] == user:
			return await ctx.send(f'`You\'re #{rank}!`')
		rank += 1
	await ctx.send('`Try contributing before checking your rank!`')
    
# Returns a leaderboard with the users that have contributed the most to #archive.
@bot.command(brief = 'Returns level leaderboard.', description = 'Compare brain sizes.')
@commands.guild_only()
async def leaderboard(ctx, page: int = 1):
	page = (page * 10) - 10
	c.execute('''SELECT * FROM users ORDER BY score DESC LIMIT 10 OFFSET ?''', (page,))
	query = c.fetchall()
	if query:
		string = ''
		rank = page + 1
		for i in query:
			user = bot.get_user(i[0])
			if user:
				string += f'[{rank}.] {user.name}: level {i[1]}.\n'
			else:
				string += f'[{rank}.] User left server: level {i[1]}.\n'
			rank += 1
		await ctx.send(f'```ini\n{string}```')
	else:
		await ctx.send('No entries on this page!')

### Other

ebook_formats = ('.pdf', '.epub', '.txt', '.azw', '.djvu', '.mobi', '.iba', '.txt', '.rtf', '.chm', '.doc', '.html')

# Checks for uploads to #archive.
@bot.event
async def on_message(message):
        await bot.process_commands(message)
        if message.author.id == bot.user.id:
                        return
        if str(message.channel) == 'archive' and message.attachments:
                if message.attachments[0].filename.endswith(ebook_formats):
                        user = message.author.id
                        c.execute('''SELECT * FROM users WHERE user_id = ?''', (user,))
                        query = c.fetchone()
                        if query:
                                c.execute('''UPDATE users SET score = score + 1 WHERE user_id = ?''', (user,))
                        else:
                                c.execute('''INSERT INTO users(user_id, score) VALUES (?, 1)''', (user,))
                        db.commit()

bot.run(config.token)