from discord.ext import commands

# NOTE See: https://discordpy.readthedocs.io/en/v1.4.1/ext/commands/api.html#checks


def has_guild_permissions(**perms):
    original = commands.has_guild_permissions(**perms).predicate

    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return await original(ctx)

    return commands.check(extended_check)


def is_administrator():
    return has_guild_permissions(administrator=True)
