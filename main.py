from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core import AstrBotConfig
from astrbot.api import logger
from astrbot.core.star.filter.event_message_type import EventMessageType

@register("repeater", "wiikaros", "一个简单的复读插件", "1.0.0")
class repeater(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.repeat_group_whitelist = []  # 允许复读的群组列表
        self.repeat_target_whitelist = []  # 允许复读的对象列表
        self.repeat_target_format: dict = config.get("repeat_target_format", {})

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    # 复读处理
    @filter.message_type(EventMessageType.GROUP_MESSAGE)
    async def repeat_handler(self, event: AstrMessageEvent):
        # 群白名单
        group_id = event.get_group_id()
        if self.repeat_group_whitelist and group_id not in self.repeat_group_whitelist:
            return
        # 目标白名单
        sender_id = event.get_sender_id()
        if self.repeat_target_whitelist and sender_id not in self.repeat_target_whitelist:
            return
        # 复读格式
        if not self.repeat_target_format.get("text", True) and event.message_type == EventMessageType.TEXT:
            return
        if not self.repeat_target_format.get("image", True) and event.message_type == EventMessageType.IMAGE:
            return
        # 进行复读
        if event.message_type == EventMessageType.TEXT:
            # await event.reply(event.message_str)
            await event.plain_result("文字复读: " + event.message_str)
        elif event.message_type == EventMessageType.IMAGE:
            await event.image_result("图片复读: " + event.message_image)
        

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
