from discord.commands.context import ApplicationContext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from discord import Option, Message, TextChannel, Thread
from discord import OptionChoice
from models.custom_bot import DiscordBot
from discord.ext import commands
from agents.memory import InterviewerMemory
from agents import InterviewerAgent


class cog_interview(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='interview', description='desc')
    # @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be user once every 3 seconds
    async def interview(self, ctx: ApplicationContext, type: Option(
        str,
        choices=[
            OptionChoice(name="Interviewer", value='interviewer'),
            OptionChoice(name="Interviewee", value='interviewee')
        ], description='What role will the Bot play?')):
        await ctx.defer()
        if type == 'interviewer':
            interviewer_client = InterviewerAgent(llm=self.bot.llm,
                memory=InterviewerMemory(max_questions=2, interview_goals=['Python', 'Github', 'OpenAI API']))

            response = await interviewer_client.run(query=f'Hello, my name is {ctx.user.name}, '
                                                          f'I would like to apply for Python Intern role.')
            message = await ctx.respond(response)
            thread = await ctx.channel.create_thread(name=f'{ctx.user.name}\'s interviewer agent thread',
                                                     message=message)
            self.bot.interviewer_threads.append(thread.id)
            self.bot.interviewer_clients[thread.id] = interviewer_client
            return
        if type == 'interviewee':
            response = await self.bot.interviewee_client.run(query=f'Hello, Introduce yourself please.')
            message = await ctx.respond(response)
            thread = await ctx.channel.create_thread(name=f'{ctx.user.name}\'s interviewee agent thread',
                                                     message=message)
            self.bot.interviewee_threads.append(thread.id)
            return

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, Thread):
            print(message)
            print('content=', message.content)
            print(message.type)
            print(message.system_content)
            if message.channel.id in self.bot.interviewer_threads:
                async with message.channel.typing():
                    interviewer_client = self.bot.interviewer_clients.get(
                message.channel.id)
                    response = await interviewer_client.run(query=message.content)
                await message.channel.send(content=response)
            elif message.channel.id in self.bot.interviewee_threads:
                async with message.channel.typing():
                    response = await self.bot.interviewee_client.run(query=message.content)
                await message.channel.send(content=response)


def setup(client):
    client.add_cog(cog_interview(client))
