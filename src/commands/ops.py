import random
import glob
import disnake

async def drill(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/drill/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 Drill - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def casual(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/casual/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 Casual Squad Online!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def fugg(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/fugg/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 FUGG - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def fubg(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/fubg/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 FUBG - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For relaxation, calm thoughts and stress free building.",
            inline=True
            )
    return Message


async def fuad(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/fuad/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 FUAD - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message


async def huntsmen(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/huntsmen/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 Huntsmen - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="TeamSpeak is Mandatory!",
            value="Hit the button below to go straight there.",
            inline=True
            )
    return Message


async def fuel(message_body):
    propaganda = disnake.File(fp=random.choice(glob.glob("./assets/splash_art/fuel/*.png")))
    Message = disnake.Embed(
            title="__Planetside 2 FUEL - Starting NOW!__",
            color=0x9E0B0F,
            description=str(message_body),
            )
    Message.set_image(
        file=propaganda
    )
    Message.add_field(
            name="Join the conversation on TeamSpeak",
            value="For chat, tactics and discussion.",
            inline=True
            )
    return Message
