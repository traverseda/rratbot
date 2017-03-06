import shelve, string, random, collections
from botCore import bot
from discord import client
voteStorage = shelve.open('./storage/votes.shelve',writeback=True)

@bot.command(pass_context=True)
async def createVote(ctx,argCount: int, issue=None):
    """
    Votes are normalized to lowercase letters only.

    That means
        `##Vote1!!!, 8`
    and
        `vote, 8`
    are both votes on the same issue.
    We only actually use that first line for anything.
    """
    if not issue:
        issue = ''.join(random.choices(string.ascii_uppercase,k=32))
    if argCount > 24:
        await bot.say("Too many options. We can only use 24")
        return
    if issue in voteStorage:
        await bot.say("An issue with that name already exists")
        return

    issue=[char for char in issue.lower() if char.isalpha()]
    issue="".join(issue)
    options = string.ascii_lowercase[:argCount]
    issueObject={
        'argCount':argCount,
        'opId':ctx.message.id,
        'interfaces':set(),
    }
    voteStorage[issue]=issueObject
    msgStr = """To vote anonymously, DM rbot with `?voteInterface {issue}`. Count Votes with `?voteCount {issue}`"
    """
    msg = await bot.say(msgStr.format(issue=issue))
    await spawnVoteInterface(issue, bot)

@bot.command()
async def voteCount(issueID):
    issue = voteStorage[issueID]
    votes = collections.defaultdict(set)
    for msg in issue['interfaces']:
        channel, msgID = msg
        channel = bot.get_channel(channel)
        msg = await bot.get_message(channel, msgID)
        for reaction in msg.reactions:
            users = await bot.get_reaction_users(reaction)
            for user in users:
                if user.id == bot.user.id:
                    break
                votes[user.id].add(reaction.emoji)
    finalVotes=collections.Counter()
    for key, value in votes.items():
        finalVotes.update(value)
    msg=[]
    msgStr="{} : {}% with {} votes"
    voteCount = sum(finalVotes.values())
    msg.append("Total: "+str(voteCount))
    for key,value in finalVotes.items():
       msg.append(msgStr.format(key,round((value/voteCount)*100),value))
    await bot.say("\n".join(msg))

@bot.command()
async def voteInterface(issueID):
    await spawnVoteInterface(issueID, bot)

asciiEmotes=('🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿',)

async def spawnVoteInterface(issueID, botInstance):
    msg = await botInstance.say("Vote on `{}` using reactions below.".format(issueID))
    voteStorage[issueID]['interfaces'].add((msg.channel.id, msg.id))
    voteStorage.sync()
    for c in asciiEmotes[:voteStorage[issueID]['argCount']]:
        await botInstance.add_reaction(msg, c)
