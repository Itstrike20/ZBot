# -*- coding: utf-8 -*-

import datetime

import discord
import pytz
from discord.ext import commands

TIMEZONE = pytz.timezone('Europe/Brussels')


async def get_usage(parent_command, command_name):
    if parent_command.name == command_name:
        return parent_command.usage
    else:
        for subcommand in parent_command.all_commands.values():  # TODO fix for @commands.command which don't have an 'all_commands' attribute
            command_usage = await get_usage(subcommand, command_name)
            if command_usage:
                return command_usage
    return None


async def send_usage(context):
    if hasattr(context.cog, 'MAIN_COMMAND_NAME'):
        main_command_name = context.cog.MAIN_COMMAND_NAME
        command_name = context.invoked_with
        command_usage = await get_usage(context.bot.all_commands[main_command_name], command_name)
        if command_usage:
            bot_user = context.bot.user
            prefix = f"@{bot_user.name}#{bot_user.discriminator} " if '@' in context.prefix else context.prefix
            await context.send(f"Syntaxe: `{prefix}{command_name} {command_usage}`\n")
            # TODO add subcommands in usage
        else:
            print(f"No usage defined for {command_name}")
    else:
        print(f"No main command defined for {context.cog}.")


async def has_role(guild: discord.Guild, user: discord.User, role_name: str):
    member = guild.get_member(user.id)
    if member:
        role = discord.utils.get(member.roles, name=role_name)
        if role:
            return True
    return False


async def get_current_time():
    return datetime.datetime.now(TIMEZONE)


async def get_user_list(users, separator=", "):
    return separator.join(user.mention for user in users)


async def make_announce(context, channel: discord.TextChannel, announce_role_name: str, announce: str, embed: discord.Embed = False):
    announce_role = discord.utils.find(lambda role: role.name == announce_role_name, context.guild.roles)
    content = f"{announce_role.mention + ' ' if announce_role is not None else ''}{announce}"
    return await channel.send(content=content, embed=embed)


async def try_get(error: commands.CommandError, iterable, **filters):
    try:
        result = discord.utils.get(iterable, **filters)
        if not result:
            raise error
        return result
    except discord.NotFound:
        raise error


async def try_get_message(error: commands.CommandError, channel: discord.TextChannel, message_id: int):
    try:
        message = await channel.fetch_message(message_id)
        if not message:
            raise error
        return message
    except discord.NotFound:
        raise error