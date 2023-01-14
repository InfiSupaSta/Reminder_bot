Reminder bot based on aiogram, FASTApi, postgres, docker.  
Reminders will be created based on user input according to user timezone offset.


Quickstart:
-
1) First of all rename **.env.template** file to **.env** and fill the BOT_TOKEN variable. 
It can be obtained via BotFather in Telegram app.
2) Build all necessary images and run it
> docker-compose up --build

Usage example
- 

After steps above you can interact with bot. Use /help and /start commands for more info.
After registration and setting your timezone offset you can create tasks. It must follows next pattern:

> REMIND ... TASK ...

REMIND and TASK - required keywords to create task. 
Without using both user input will be pointed like unrecognized command.
Its case insensitive - so there is no difference between
**reMInD** and **ReMind**.

At this moment 5 patterns for tasks creating available and they looks like:
> Remind every 5 secs task do not be lazy  
> Remind every 2 hours task ...  
> Remind every 45 mins task ...

> Remind 31 december 23:59 task do some workout

> Remind 1.1.2023 23:59 task eat some spicy food

> Remind tomorrow 23:59 task waiting for next day

> Remind in 2.5 hours task something cool  
> Remind in 3 minutes task ...

For the **EVERY** and **IN** patterns (first and last examples) unit of time must include minimum amount of symbols to 
univocal recognizing - **sec** **min** **hour** **day**.  
All available patterns can be found in ./bot/examples/tasks_pattern_examples.py or by using bot /examples command.