from aiogram.types import BotCommand

COMMANDS = [BotCommand(command="/start", description="запустити бота"),
            BotCommand(command="/help", description="список команд"),
            BotCommand(command="/create", description="створити чергу: /create назва"),
            BotCommand(command="/queue", description="показати чергу"),
            BotCommand(command="/join", description="стати на місце: /join номер"),
            BotCommand(command="/leave", description="вийти з черги"),
            BotCommand(command="/swap", description="помінятись місцями: /swap номер"),
            BotCommand(command="/export", description="вивантажити в Excel"),]