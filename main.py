from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core import AstrBotConfig
from astrbot.api import logger
from astrbot.core.star.filter.event_message_type import EventMessageType
import astrbot.api.message_components as Comp

@register("repeater", "wiikaros", "一个简单的复读插件", "1.0.0")
class repeater(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.repeat_group_whitelist = config.get("repeat_group_whitelist", [])  # 允许复读的群组列表
        self.repeat_target_whitelist = config.get("repeat_target_whitelist", [])  # 允许复读的对象列表
        self.repeat_target_format: dict = config.get("repeat_target_format", {})
        logger.info(f"白名单长度: {len(self.repeat_target_whitelist)}")
        logger.info(f"白名单成员: {', '.join(self.repeat_target_whitelist)}")
        logger.info(f"复读格式: {self.repeat_target_format}")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 复读处理
    @filter.event_message_type(EventMessageType.GROUP_MESSAGE)
    async def repeat_handler(self, event: AstrMessageEvent):
        # 群白名单
        group_id = event.get_group_id()
        if self.repeat_group_whitelist and str(group_id) not in self.repeat_group_whitelist:
            return
        # 目标白名单
        sender_id = event.get_sender_id()
        if self.repeat_target_whitelist and str(sender_id) not in self.repeat_target_whitelist:
            return
        # 匹配复读格式并复读
        messages = event.get_messages()
        for seg in messages:
            if isinstance(seg, Comp.Plain):
                if not self.repeat_target_format.get("text", True):
                    return
                else:
                    yield event.plain_result(event.message_str)
            elif isinstance(seg, Comp.Image):
                if not self.repeat_target_format.get("image", True):
                    return
                else:
                    yield event.image_result(seg.url)

        

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
