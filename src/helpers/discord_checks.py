from typing import Union

import disnake


# from disnake.ext import commands


async def get_channel(
        inter: disnake.Interaction,
        channel_name: str = None,
        channel_id: id = None,
        send_error: bool = False
) -> Union[disnake.abc.GuildChannel, None]:
    """
    Check if a given channel name exists in the originating guild.
    Ether `channel_name` or `channel_id` must be given

    Parameters
    ----------
    inter: Used to get guild in which to check in and reply if needed
    channel_name: Channel name to check if exists.
    channel_id: ID of chanel
    send_error: Weather or not send error in interaction in response
    """
    # find the channel, where to send the message
    channel = None
    if channel_id:
        channel = inter.guild.get_channel(channel_id)
    if channel_name:
        channel = disnake.utils.get(inter.guild.channels, name=channel_name)

    if channel is None:
        if send_error:
            await inter.edit_original_message(content="Impossible. Perhaps the Archives are incomplete.\n" +
                                                      "I don't see a channel named `#" + channel_name + "`")
        return None
    return channel


async def get_role(
        inter: disnake.Interaction,
        role_name: str = None,
        role_id: int = None,
        send_error: bool = False
) -> Union[disnake.Role, None]:
    """
    Check if a given channel name exists in the originating guild
    Ether `role_name` or `role_id` must be given

    Parameters
    ----------
    inter: Used to get guild in which to check in and reply if needed
    role_name: Name of role
    role_id: IDof role
    send_error: Weather or not send error in interaction in response
    """
    role = None

    if role_id:
        role = inter.guild.get_role(role_id)
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
        write: bool = False,
        manage_reactions: bool = False,
        send_error: bool = False
) -> bool:
    """
    Check if authoring user has permission to post in a channel

    Parameters
    ----------
    inter: Used to get guild in which to check in and reply if needed
    channel: Channel object to check. If not given, chanel of interaction will be used
    user_role: User or role to check
    write: If `True` will check if one can write in chanel
    manage_reactions: If `True` will check if one can manage reactions in chanel
    send_error: Weather or not send error in interaction in response
    """
    channel = channel if channel else inter.channel
    user_role = user_role if user_role else inter.author
    permissions = channel.permissions_for(user_role)
    message = None

    if write and not permissions.send_messages:
        message = "Imitating the Captain, huh? Surely that violates some kind of Starfleet protocol.\n" \
                  "You don't have permissions to use this command"
    elif manage_reactions and not permissions.manage_messages:
        message = f"You don't have the permissions to remove unneeded reactions or spam in {channel.mention}" \
                  "\nhttps://www.govloop.com/wp-content/uploads/2015/02/data-star-trek-request-denied.gif"

    if send_error and message:
        await inter.edit_original_message(content=message)
        return False
    return True


async def bot_has_permission(
        inter: disnake.Interaction = None,
        channel: disnake.TextChannel = None,
        write=False,
        react=False,
        send_error: bool = False
) -> bool:
    """
    Check if the bot has permission to post in a channel.

    Parameters
    ----------
    inter: Used to get guild in which to check in and reply if needed
    channel: Channel object to check. If not given, chanel of interaction will be used
    write: If `True` will check if bot can write in chanel
    react: If `True` will check if bot can react in chanel
    send_error: Weather or not send error in interaction in response
    """
    no_permission: bool = False
    message = "My lord, is that legal? \n "
    if not channel:
        channel = inter.channel
    bot_permissions = channel.permissions_for(channel.guild.me)

    if write and not bot_permissions.send_messages:
        message += "I don't have permission to send messages in " + channel.mention
        no_permission = True
    elif react and not bot_permissions.add_reactions:
        message += "I don't have permission to react in " + channel.mention
        no_permission = True

    if no_permission:
        if inter and send_error:
            await inter.edit_original_message(content=message)
        return False
    return True
