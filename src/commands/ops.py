import random
import disnake

async def drill(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/567172242803523597/925515906556264528/platoon_copy_3.png",
    "https://cdn.discordapp.com/attachments/567172242803523597/925515906178744401/platoon_copy_2.png",
    "https://cdn.discordapp.com/attachments/567172242803523597/925515906866614282/platoon_copy_4.png",
    "https://cdn.discordapp.com/attachments/567172242803523597/925515907239915550/platoon_copy.png",]
    Message = disnake.Embed(
            title="__Planetside 2 Drill - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def casual(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991057796432797746/casual.png",]
    Message = disnake.Embed(
            title="__Planetside 2 Casual Squad Online!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def fugg(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991044437880741930/FUGG.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991044438417625108/FUGG_copy.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991044438740594718/FUGG_copy_2.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991044439264854047/FUGG_copy_3.png",]
    Message = disnake.Embed(
            title="__Planetside 2 FUGG - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def fubg(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991046582415814677/FUBG_copy_2.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991046582801666118/FUBG.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991046583091089425/FUBG_copy.png",]
    Message = disnake.Embed(
            title="__Planetside 2 FUBG - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For relaxation, calm thoughts and stress free building.",
            inline=True
            )
    return Message


async def fuad(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991054044086808656/FUAD.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991054044439122000/FUAD_copy.png",]
    Message = disnake.Embed(
            title="__Planetside 2 FUAD - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def huntsmen(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991055897491017829/HUNTSMEN_copy.png",
    "https://cdn.discordapp.com/attachments/986678839008690176/991055897734295592/HUNTSMEN.png",]
    Message = disnake.Embed(
            title="__Planetside 2 Huntsmen - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="TeamSpeak is Mandatory!",
            value="Hit the button below to go straight there.",
            inline=True
            )
    return Message


async def fuel(message_body):
    propaganda=["https://cdn.discordapp.com/attachments/986678839008690176/991056056513867816/FUEL.png",]
    Message = disnake.Embed(
            title="__Planetside 2 FUEL - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        url=random.choice(propaganda)
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message
    