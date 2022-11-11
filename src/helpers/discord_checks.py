from typing import Type, Union

import disnake


# from disnake.ext import commands


async def get_channel(inter: disnake.Interaction, channel_name: str = None, channel_id: id = None,
                      send_error: bool = False):
    """
    Check if a given channel name exists in the originating guild

    Parameters
    ----------
    channel_name: channel name to check if exists.
    """
    # find the channel, where to send the message
    channel = None
    if channel_id:
        channel = inter.guild.channels(channel_id)
    if channel_name:
        channel = disnake.utils.get(inter.guild.channels, name=channel_name)
    if channel is None:
        if send_error:
            await inter.edit_original_message(content="Impossible. Perhaps the Archives are incomplete.\n" +
                                                      "I don't see a channel named `#" + channel_name + "`")
        return None
    return channel


async def get_role(inter: disnake.Interaction, role_name: str = None,
                   role_id: int = None, send_error: bool = False):
    """
    Check if a given channel name exists in the originating guild

    Parameters
    ----------
    channel_name: channel name to check if exists.
    """
    role = None

    if role_id:
        role = inter.guild.role(role_id)
    elif role_name:
        role = disnake.utils.get(inter.guild.roles, name=role_name)
    if role is None:
        if send_error:
            await inter.edit_original_message(content="Impossible. Perhaps the Archives are incomplete.\n" +
                                                      "I don't see a role named `" + role_name + "`")
        return None
    return role


async def user_or_role_has_permission(
        inter: disnake.Interaction,
        channel: disnake.TextChannel = None,
        user_role: Union[disnake.Member, disnake.Role] = None,
        can_write: bool = False,
        can_manage_reactions: bool = False,
        send_error: bool = False
) -> bool:
    """
    Check if authoring user has permission to post in a channel

    Parameters
    ----------
    channel: channel object to check.
    """
    channel = channel if channel else inter.channel
    permissions = channel.permissions_for(inter.author)
    user_role = user_role if channel else inter.channel
    permissions = channel.permissions_for(inter.author)

    if can_write and not permissions.send_messages:
        message = "Imitating the Captain, huh? Surely that violates some kind of Starfleet protocol.\n" \
                  "You don't have permissions to use this command"

    if can_manage_reactions and not permissions.manage_messages:
        message = f"You don't have the permissions to remove unneeded reactions or spam in {channel.mention}" \
                  "\nhttps://www.govloop.com/wp-content/uploads/2015/02/data-star-trek-request-denied.gif"
    if send_error:
        await inter.edit_original_message(content=message)
        return False
    return True


async def check_if_bot_has_permission(
        inter: disnake.Interaction = None,
        channel: disnake.TextChannel = None,
        send_error: bool = False
) -> bool:
    """
    Check if the bot has permission to post in a channel.

    Parameters
    ----------
    channel: channel object to check.
    """
    message = "My lord, is that legal? \n " + "I don't have permission to send messages in #" + str(channel)
    if not channel:
        channel = inter.channel

    if not channel.permissions_for(channel.guild.me).send_messages:
        if inter and send_error:
            await inter.edit_original_message(content=message)
        return False
    return True
