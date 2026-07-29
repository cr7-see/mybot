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

@bot.tree.command(name="setup", description="إرسال لوحة الأزرار والتذاكر")
async def setup(interaction: discord.Interaction):
    view = TicketPanelView()
    # إضافة الأزرار الأخرى في نفس اللوحة إذا أردت
    await interaction.response.send_message("اختر ما يناسبك من الأزرار أدناه:", view=view)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول باسم {bot.user}")
    bot.add_view(TicketPanelView())
    try:
        synced = await bot.tree.sync()
        print(f"تم تحديث ومزامنة {len(synced)} أمر")
    except Exception as e:
        print(f"خطأ في المزامنة: {e}")

bot.run(os.environ.get('TOKEN'))
