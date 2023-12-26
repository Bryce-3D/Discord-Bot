from ..bot_config import bot, commands



#Utilities ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Dict to quickly convert a digit to it's spelling
digit_to_word = {0:'zero', 1:'one', 2:'two', 3:'three', 4:'four', 
            5:'five', 6:'six', 7:'seven', 8:'eight', 9:'nine'}
#Dict to quickly convert a digit to it's keycap emoji
num_to_keycap = {0:'0️⃣', 1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 
                 5:'5️⃣', 6:'6️⃣', 7:'7️⃣', 8:'8️⃣', 9:'9️⃣', 10:'🔟'}

@bot.command()
async def poll(ctx:commands.Context, question:str, *choices:str) -> None:
    '''Creates a poll with a question and a (possibly null) set of choices'''
    msg_text = question

    #If no choices given
    if len(choices) == 0:
        msg = await ctx.send(msg_text)
        await msg.add_reaction('<:ya:1102451988005929021>')
        await msg.add_reaction('<:meh:1102451982750457996>')
        await msg.add_reaction('<:na:1102451985954902036>')
    
    #If choices are given
    else:
        #If too many choices, tell them to put less
        if len(choices) > 10:
            await ctx.send('Pls put at most 10 options')
        else:   #If not too many choices
            #Add the choices to the msg
            for i in range(len(choices)):
                msg_text += '\n'
                msg_text += f':{digit_to_word[i]}: - {choices[i]}'
            
            msg = await ctx.send(msg_text)   #Send the msg

            #Add reactions
            for i in range(len(choices)):
                await msg.add_reaction(num_to_keycap[i])
