import discord

# Type of ctx.author
type DiscordUser = discord.User|discord.Member
# Type of ctx.channel
type DiscordChannel = (
    discord.TextChannel
    | discord.StageChannel
    | discord.VoiceChannel
    | discord.Thread
    | discord.DMChannel
    | discord.GroupChannel
    | discord.PartialMessageable
)
