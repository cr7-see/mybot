import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------------------------------------
# آيدي سيرفرك:
GUILD_ID = 1524485864963576040

# آيدي رتبة التفعيل (مواطن ، RC) - تمنح للعضو:
VERIFIED_ROLE_ID = 1524487798810476546

# آيدي رتبة (جاري تفعيل ، RC) - تسحب من العضو:
PENDING_ROLE_ID = 1524487796990021803

# روابط الصور الخاصة بك:
LOGO_IMAGE = "https://cdn.discordapp.com/attachments/1524488438064353300/1531830162554097716/7d9ad4b5630df1cb1350ef7ba58178db.webp?ex=6a6aa382&is=6a695202&hm=6b6fb46883e46a5cd2b98c0f5204c3ed215e453380a50930b21b2a99c26d0e38&"
BANNER_IMAGE = "https://cdn.discordapp.com/attachments/1524488438064353300/1531830162910351532/7d9ad4b5630df1cb1350ef7ba58178db-1_edit_31147386794314.jpg?ex=6a6aa382&is=6a695202&hm=7fae7b156e4a6184fd2b23de049735384bc744be7cb453f4eb88cd46404a0498&"

# إيموجي سيرفرك المخصص:
CUSTOM_EMOJI = discord.PartialEmoji(name="emoji_12", id=1531847410056171580)
# ---------------------------------------------------------

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_safe")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message("سيتم حذف التذكرة خلال 5 ثوانٍ...", ephemeral=True)
            await asyncio.sleep(5)
            if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
                await interaction.channel.delete()
        except Exception as e:
            print(f"خطأ عند إغلاق التذكرة: {e}")

# دالة مساعدة لإنشاء التذكرة
async def create_ticket_channel(interaction: discord.Interaction, prefix: str, title_name: str):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    user = interaction.user

    channel_name = f"{prefix}-{user.name}"
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        await interaction.followup.send(f"لديك تذكرة مفتوحة بالفعل: {existing_channel.mention}", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

    embed = discord.Embed(
        title=f"تذكرة {title_name}",
        description=f"أهلاً بك {user.mention}، يرجى كتابة تفاصيل الطلب أو المشكلة هنا وسيرد عليك المسؤول قريباً.",
        color=discord.Color.red()
    )
    if LOGO_IMAGE.startswith("http"):
        embed.set_thumbnail(url=LOGO_IMAGE)

    await ticket_channel.send(embed=embed, view=CloseTicketView())
    await interaction.followup.send(f"تم إنشاء تذكرتك بنجاح: {ticket_channel.mention}", ephemeral=True)

# 1. بنل التذاكر العامة
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="طلب دعم فني", emoji=CUSTOM_EMOJI, style=discord.ButtonStyle.blurple, custom_id="btn_support", row=0)
    async def btn_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "دعم-فني", "طلب دعم فني")

    @discord.ui.button(label="طلب عصابه", emoji=CUSTOM_EMOJI, style=discord.ButtonStyle.blurple, custom_id="btn_gang", row=0)
    async def btn_gang(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "طلب-عصابة", "طلب عصابة")

    @discord.ui.button(label="طلب متجر", emoji=CUSTOM_EMOJI, style=discord.ButtonStyle.blurple, custom_id="btn_shop", row=1)
    async def btn_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "طلب-متجر", "طلب متجر")

    @discord.ui.button(label="طلب هيئة الرقابه والتفتيش", emoji=CUSTOM_EMOJI, style=discord.ButtonStyle.blurple, custom_id="btn_inspect", row=1)
    async def btn_inspect(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "رقابة-وتفتيش", "طلب هيئة الرقابة والتفتيش")

# 2. بنل خاص لطلب التفعيل فقط
class VerifyPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="طلب تفعيل حساب", emoji=CUSTOM_EMOJI, style=discord.ButtonStyle.blurple, custom_id="btn_verify")
    async def btn_verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(interaction, "تفعيل-حساب", "طلب تفعيل حساب")

# دالة معالجة التفعيل
async def process_verification(guild, target_member, admin_user, channel):
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    if verified_role:
        await target_member.add_roles(verified_role)

    pending_role = guild.get_role(PENDING_ROLE_ID)
    if pending_role and pending_role in target_member.roles:
        await target_member.remove_roles(pending_role)

    dm_embed = discord.Embed(
        title="✅ تم تفعيلك بنجاح",
        description=(
            f"مرحباً {target_member.mention}\n\n"
            f"تم تفعيلك في سيرفر **{guild.name}**\n\n"
            f"👤 المسؤول: {admin_user.mention}\n"
            f"🔥 أجواء | فعاليات | منافسات\n"
            f"❤️ نتمنى لك تجربة ممتعة"
        ),
        color=discord.Color.green()
    )
    if LOGO_IMAGE.startswith("http"):
        dm_embed.set_thumbnail(url=LOGO_IMAGE)
    
    try:
        await target_member.send(embed=dm_embed)
        await channel.send(f"✅ تم إعطاء رتبة **مواطن ، RC** وسحب رتبة **جاري تفعيل ، RC** من {target_member.mention} وإرسال الرسالة لخاصّه بنجاح!")
    except discord.Forbidden:
        await channel.send(f"✅ تم تحديث رتب {target_mention.mention} بنجاح، لكن تعذر إرسال الرسالة للخاص لأن خاصّ العضو مغلق.")

@bot.tree.command(name="verify", description="تفعيل العضو المنسوب وإعطائه الرتبة وسحب رتبة الانتظار")
@commands.has_permissions(administrator=True)
async def verify_slash(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    await process_verification(interaction.guild, member, interaction.user, interaction.channel)
    await interaction.followup.send("تم تنفيذ التفعيل بنجاح!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("تفعيل") and message.author.guild_permissions.administrator:
        if message.mentions:
            target_member = message.mentions[0]
            await process_verification(message.guild, target_member, message.author, message.channel)
        else:
            await message.channel.send("❌ يرجى عمل تاق للعضو، مثال: `تفعيل @العضو`")

    await bot.process_commands(message)

@bot.tree.command(name="setup_tickets", description="إرسال بنل التذاكر العامة")
@commands.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        description="تذاكر السيرفر اختر التكت الذي يناسبك بضغط على زر المناسب أسفل شاشة\n\n@everyone",
        color=discord.Color.red()
    )
    if LOGO_IMAGE.startswith("http"):
        embed.set_thumbnail(url=LOGO_IMAGE)
    if BANNER_IMAGE.startswith("http"):
        embed.set_image(url=BANNER_IMAGE)

    await interaction.channel.send(embed=embed, view=TicketPanelView())
    await interaction.followup.send("تم إرسال بنل التذاكر العامة بنجاح!", ephemeral=True)

@bot.tree.command(name="setup_verify", description="إرسال بنل طلب تفعيل الحساب")
@commands.has_permissions(administrator=True)
async def setup_verify(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = duda = discord.Embed(
        title="✨ قسم تفعيل الحسابات",
        description="اضغط على الزر بالأسفل لفتح تذكرة طلب تفعيل حسابك في السيرفر\n\n@everyone",
        color=discord.Color.green()
    )
    if LOGO_IMAGE.startswith("http"):
        duda.set_thumbnail(url=LOGO_IMAGE)

    await interaction.channel.send(embed=duda, view=VerifyPanelView())
    await interaction.followup.send("تم إرسال بنل التفعيل المنفصل بنجاح!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول باسم: {bot.user}")
    bot.add_view(TicketPanelView())
    bot.add_view(VerifyPanelView())
    bot.add_view(CloseTicketView())
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"تم تحديث ومزامنة {len(synced)} أمر لسيرفرك فوراً!")
    except Exception as e:
        print(f"خطأ في المزامنة: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
