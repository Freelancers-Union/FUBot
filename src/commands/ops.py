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
            name="Join the tactic discussion and bit of nonsense on TeamSpeak",
            value="ts.fugaming.org\n`futs`",
            inline=True
            )
    return Message
