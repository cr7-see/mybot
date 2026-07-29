import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة", style=discord.ButtonStyle.red, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("تم فتح تذكرتك بنجاح!", ephemeral=True)

class VerifyPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تفعيل الحساب", style=discord.ButtonStyle.green, custom_id="verify_account")
    async def verify_account(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("تم طلب تفعيل حسابك بنجاح!", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.grey, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("جاري إغلاق التذكرة...", ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول باسم {bot.user}")
    bot.add_view(TicketPanelView())
    bot.add_view(VerifyPanelView())
    bot.add_view(CloseTicketView())
    try:
        GUILD_ID = 123456789012345678
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"تم تحديث ومزامنة {len(synced)} أمر لسيرفرك")
    except Exception as e:
        print(f"خطأ في المزامنة: {e}")

bot.run(os.environ.get('TOKEN'))
