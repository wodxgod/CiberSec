#Developed by wodx @ 26-06-2019
import discord, subprocess, json, os

#These commands are blacklisted, as they're pretty useless in this project.
BLACKLISTED_COMMANDS = [
    'nano', 
    'leafpad'
]

#Operators which's used to run multiple commands at once
OPERATORS = [
    ';',
    '&&',
    '||'
]

CONFIG = json.loads(open('config/config.json').read())

def main():
    #Bot token check
    token = CONFIG['config']['token']
    if not token or len(token) != 59 or not '.' in token:
        print('[-] Invalid token.')
        exit()

    #OS check
    if not os.name == 'posix':
        print('[-] CiberSec has to be run on a Linux machine.')
        exit()

    cibersec = discord.ext.Bot(command_prefix = '')

    #Ready event
    @cibersec.event
    async def on_ready():
        print('[*] CiberSec is ready to use.')

    #Message event
    @cibersec.event
    async def on_message(message):
        if message.author == cibersec.user:
            return
        
        channel = message.channel
        try:
            if channel.id == int(CONFIG['config']['terminal']):
                command = message.content

                #Command analyzing
                for operator in OPERATORS:
                    if ' %s ' % (operator) in command:
                        command_split = command.split(' %s ' % (operator))
                        for cmd in command_split:
                            for cmd_blacklisted in BLACKLISTED_COMMANDS:
                                if cmd.startsWith(cmd_blacklisted):
                                    await cibersec.send_message(channel, 'Error! Command was blacklisted.')
                                    return

                #Clear command
                if command.startsWith('clear'):
                    async for msg in cibersec.logs_from(channel):
                        await cibersec.delete_message(msg)
                    await cibersec.send_message(channel, '[+] Shell was cleared!')
                    return

                #Running the shell command
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

                #Command output
                output = process.stdout.read() + process.stderr.read()
                if not output:
                    output = '[-] Not output recieved.'

                #Adding command to history
                try:
                    command_history_channel = cibersec.get_channel(int(CONFIG['config']['history']))
                    try:
                        msg = cibersec.logs_from(command_history_channel)[0]
                        msg_content = msg.content
                        msg_content += command + '\n'
                        await cibersec.edit_message(msg, msg_content)
                    except:
                        await cibersec.send_message(command_history_channel, command + '\n')

                except:
                    await cibersec.send_message(channel, '[-] Command history channel not found!')
                    return

                #Returning the output
                await cibersec.send_message(channel, output)
        except:
            await cibersec.send_message(channel, output)

    cibersec.run(CONFIG['config']['token'])

if __name__ == '__main__':
    main()
