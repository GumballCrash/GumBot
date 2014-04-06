import re
import sqlite3
import datetime

conn = sqlite3.connect('karma.db')
cur = conn.cursor()

try:
    cur.execute('''CREATE TABLE "karma" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL COLLATE NOCASE,
        "delta" INTEGER,
        "comment" TEXT,
        "add_time" TEXT NOT NULL
        );''')
    conn.commit()
except sqlite3.OperationalError:
    pass

config = None
usemap = None
ircbot = None

exp = re.compile("^(\([^)]+\)|[^ ]+)([+]{2}|[-]{2})(.*)$")

def getsubject(msg):
    msg = msg.strip().lower()
    if msg[0] == '(' and msg[len(msg) - 1] == ')':
        msg = msg[0:len(msg)-1].strip()
    return msg

def getreason(msg, sender):
    msg = msg.strip()
    if msg.startswith('#'):
        return msg[1:].strip()
    elif msg.startswith('//'):
        return msg[2:].strip()
    else:
        return ''

def fetch_karma(ktgt):
    cur.execute('''SELECT SUM(`delta`) FROM karma WHERE `name` LIKE ?;''', (ktgt,))
    ksum = cur.fetchone()[0]
    return ksum

def karmaparse(source, msg):
    msg = msg.strip()
    ismatch = exp.match(msg)
    if ismatch:
        subject = getsubject(ismatch.group(1))
        amount = ismatch.group(2)
        if amount == '--':
            amount = -1
            ktype = 'negative'
        else:
            amount = 1
            ktype = 'positive'
        reason = getreason(ismatch.group(3), source)
        if reason:
            reason = ' for "%s"' % reason
        if subject == source.lower() and amount > 0:
            return "You can't give karma to yourself... loser."
        else:        	
            cur.execute('''INSERT INTO karma (`name`,`delta`,`comment`,`add_time`) VALUES (?,?,?,?)''', (subject, amount, reason, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            if subject == config['nick'].lower() and amount > 0:
            	return "Karma for %s is now %s. Thanks, %s!" % (subject, fetch_karma(subject), source)
            elif subject == config['nick'].lower() and amount < 0:
                return "Karma for %s is now %s. Pfft." % (subject, fetch_karma(subject))
            else:
            	return "Karma for %s is now %s." % (subject, fetch_karma(subject))
    else:
        return None

def get_karma(msg):
    m = re.match('!karma (.+)', msg)
    if not m:
        return
    ktgt = m.group(1).strip()
    ksum = fetch_karma(ktgt)
    if ksum is None:
        kstr = 'No karma has ever been assigned to %s.' % ktgt
    else:
        kstr = '%s has %s karma.' % (ktgt, ksum)
    return kstr


"""
def explain(msg):
    m = re.match('!explain (.+)', msg)
    if not m:
        return
    ktgt = m.group(1).strip()
    cur.execute('''SELECT comment FROM karma where `name` LIKE ?;''', (ktgt,))
"""

	
def irc_msg(source, target, msg):
    if not target in config['channels']:
        return
    if msg.startswith('!karma'):
        kstr = get_karma(msg)
        ircbot.say(target, kstr)
        usemap[target].SendMessage(kstr)
    else:
        karma = karmaparse(source, msg)
        if karma and target in config['channels']:
            ircbot.say(target, karma)
            usemap[target].SendMessage(karma)

def skype_msg(sourceDisplay, sourceHandle, target, msg):
    if msg.startswith('!karma'):
        kstr = get_karma(msg)
        ircbot.say(usemap[target], kstr)
        target.SendMessage(kstr)
    else:
        karma = karmaparse(sourceDisplay, msg)
        if karma and usemap[target] in config['channels']:
            ircbot.say(usemap[target], karma)
            target.SendMessage(karma)
