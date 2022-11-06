from typing import Type, Union

import disnake


# from disnake.ext import commands


async def channel_exists(inter: Type[disnake.Interaction], channel_name: str):
    """
    Check if a given channel name exists in the originating guild

    Parameters
    ----------
    channel_name: channel name to check if exists.
    """
    # find the channel, where to send the message
    channel = None
    if type(channel_name) is str:
        channel = disnake.utils.get(inter.guild.text_channels, name=channel_name)
    if channel is None:
        await inter.edit_original_message(content="Impossible. Perhaps the Archives are incomplete.\n" +
                                                  "I don't see a channel named `#" + channel_name + "`")
        return None
    return channel


async def user_or_role_has_permission(
        inter: Type[disnake.Interaction],
        channel: disnake.TextChannel = None,
        user: Union[disnake.Member, disnake.Role] = None,
        can_write: bool = False,
        can_manage_reactions: bool = False,
        append_message: str = None
):
    """
    Check if authoring user has permission to post in a channel

    Parameters
    ----------
    channel: channel object to check.
    """
    channel = channel if channel else inter.channel
    user_permissions = channel.permissions_for(inter.author)

    if can_write and not user_permissions.send_messages:
        message = "Imitating the Captain, huh? Surely that violates some kind of Starfleet protocol.\n"
        if append_message:
            message += append_message
        else:
            message += "You don't have permissions to use this command"
        await inter.edit_original_message(content=message)
        return False

    if can_manage_reactions and user_permissions.manage_messages:
        message = f"You don't have the permissions to remove unneeded reactions or spam in {channel.mention}\n"
        if append_message:
            message += append_message
        else:
            message += "https://www.govloop.com/wp-content/uploads/2015/02/data-star-trek-request-denied.gif"
        await inter.edit_original_message(content=message)
        return False
    return True


async def check_if_bot_has_permission(
        inter: Type[disnake.Interaction] = None,
        channel: disnake.TextChannel = None,
        append_message: str = None
):
    """
    Check if the bot has permission to post in a channel.

    Parameters
    ----------
    channel: channel object to check.
    """
    message = "My lord, is that legal? \n "
    if not channel:
        channel = inter.channel
    if append_message:
        message += append_message
    else:
        message += "I don't have permission to send messages in #" + str(channel)

    if not channel.permissions_for(channel.guild.me).send_messages:
        if inter:
            await inter.edit_original_message(content=message)
        return False
    return True
