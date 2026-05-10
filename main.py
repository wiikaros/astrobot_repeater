from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core import AstrBotConfig
from astrbot.api import logger
from astrbot.core.star.filter.event_message_type import EventMessageType
import astrbot.api.message_components as Comp

@register("repeater", "wiikaros", "一个简单的复读插件", "1.0.0")
class repeater(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.repeat_enabled = config.get("repeat", True)  # 是否启用复读功能
        self.repeat_group_whitelist = config.get("repeat_group_whitelist", [])  # 允许复读的群组列表
        self.repeat_target_whitelist = config.get("repeat_target_whitelist", [])  # 允许复读的对象列表
        self.repeat_target_format: dict = config.get("repeat_target_format", {})
        logger.info(f"白名单长度: {len(self.repeat_target_whitelist)}")
        logger.info(f"白名单成员: {', '.join(self.repeat_target_whitelist)}")
        logger.info(f"复读格式: {self.repeat_target_format}")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        pass

    # 开启复读
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("开启复读")
    async def enable_repeater(self, event: AstrMessageEvent):
        self.repeat_enabled = True
        self.config.__setattr__("repeat", True)
        yield event.plain_result("已开启复读")
    
    # 关闭复读
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("关闭复读")
    async def disable_repeater(self, event: AstrMessageEvent):
        self.repeat_enabled = False
        self.config.__setattr__("repeat", False)
        yield event.plain_result("已关闭复读")

    # 查看复读配置
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("复读配置")
    async def view_repeater_config(self, event: AstrMessageEvent):
        config_info = f"复读功能: {'启用' if self.repeat_enabled else '禁用'}\n"
        config_info += f"复读群聊白名单: {', '.join(self.repeat_group_whitelist) if self.repeat_group_whitelist else '无'}\n"
        config_info += f"复读对象白名单: {', '.join(self.repeat_target_whitelist) if self.repeat_target_whitelist else '无'}\n"
        config_info += f"复读格式: {', '.join([k for k, v in self.repeat_target_format.items() if v]) if self.repeat_target_format else '无'}"
        yield event.plain_result(config_info)

    # 添加复读群聊白名单
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("添加复读群聊")
    async def add_group_whitelist(self, event: AstrMessageEvent, group_id: str = None):
        if group_id is None:
            # 如果没有提供群ID，默认使用当前消息所在的群ID
            group_id = event.get_group_id()
        if str(group_id) not in self.repeat_group_whitelist:
            self.repeat_group_whitelist.append(str(group_id))
            self.config.__setattr__("repeat_group_whitelist", self.repeat_group_whitelist)
            yield event.plain_result(f"已添加群 {group_id} 到复读群聊白名单")
        else:
            yield event.plain_result(f"群 {group_id} 已在复读群聊白名单中")

    # 移除复读群聊白名单
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("移除复读群聊")
    async def remove_group_whitelist(self, event: AstrMessageEvent, group_id: str = None):
        if group_id is None:
            group_id = event.get_group_id()
        if str(group_id) in self.repeat_group_whitelist:
            self.repeat_group_whitelist.remove(str(group_id))
            self.config.__setattr__("repeat_group_whitelist", self.repeat_group_whitelist)
            yield event.plain_result(f"已移除群 {group_id} 从复读群聊白名单")
        else:
            yield event.plain_result(f"群 {group_id} 不在复读群聊白名单中")

    # 添加复读对象白名单
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("添加复读目标")
    async def add_target_whitelist(self, event: AstrMessageEvent, target_id: str = None):
        if target_id is None:
            yield event.plain_result("请提供要添加到复读目标白名单的用户ID")
            return
        if str(target_id) not in self.repeat_target_whitelist:
            self.repeat_target_whitelist.append(str(target_id))
            self.config.__setattr__("repeat_target_whitelist", self.repeat_target_whitelist)
            yield event.plain_result(f"已添加用户 {target_id} 到复读目标白名单")
        else:
            yield event.plain_result(f"用户 {target_id} 已在复读目标白名单中")

    # 移除复读对象白名单
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("移除复读目标")
    async def remove_target_whitelist(self, event: AstrMessageEvent, target_id: str = None):
        if target_id is None:
            yield event.plain_result("请提供要从复读目标白名单中移除的用户ID")
            return
        if str(target_id) in self.repeat_target_whitelist:
            self.repeat_target_whitelist.remove(str(target_id))
            self.config.__setattr__("repeat_target_whitelist", self.repeat_target_whitelist)
            yield event.plain_result(f"已移除用户 {target_id} 从复读目标白名单")
        else:
            yield event.plain_result(f"用户 {target_id} 不在复读目标白名单中")

    # 设置复读格式
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("设置复读格式")
    async def set_repeat_format(self, event: AstrMessageEvent, format: str = None):
        if format is None:
            yield event.plain_result("请提供复读格式，格式选项包括: 文本, 图片, 全部")
            return
        if format == "文本":
            self.repeat_target_format["text"] = True
            self.repeat_target_format["image"] = False
        elif format == "图片":
            self.repeat_target_format["text"] = False
            self.repeat_target_format["image"] = True
        elif format == "全部":
            self.repeat_target_format["text"] = True
            self.repeat_target_format["image"] = True
        else:
            yield event.plain_result("无效的复读格式选项，请选择: 文本, 图片, 全部")
            return
        self.config.__setattr__("repeat_target_format", self.repeat_target_format)
        yield event.plain_result(f"已设置复读格式: {', '.join([f for f in ['text', 'image'] if self.repeat_target_format.get(f.lower(), False)]) if self.repeat_target_format else '无'}")

    # 显示帮助
    @filter.command("复读帮助")
    async def repeat_help(self, event: AstrMessageEvent):
        help_text = (
            "复读插件使用说明:\n"
            "1. 管理员可以使用以下命令管理复读功能:\n"
            "   - 【开启复读】: 开启复读功能\n"
            "   - 【关闭复读】: 关闭复读功能\n"
            "   - 【复读配置】: 查看当前复读配置\n"
            "   - 【添加复读群聊】 [群ID]: 将指定群添加到复读群聊白名单（不提供群ID则默认添加当前群）\n"
            "   - 【移除复读群聊】 [群ID]: 将指定群从复读群聊白名单中移除（不提供群ID则默认移除当前群）\n"
            "   - 【添加复读目标】 [用户ID]: 将指定用户添加到复读目标白名单\n"
            "   - 【移除复读目标】 [用户ID]: 将指定用户从复读目标白名单中移除\n"
            "   - 【设置复读格式】 [文本/图片/全部]: 设置机器人复读的消息类型\n"
            "2. 只有在开启复读功能且满足白名单条件的情况下，机器人才会进行复读。"
        )
        yield event.plain_result(help_text)

    # 复读处理
    @filter.event_message_type(EventMessageType.GROUP_MESSAGE)
    async def repeat_handler(self, event: AstrMessageEvent):
        if not self.repeat_enabled:
            return
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
        try:
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
        except Exception as e:
            logger.error(f"复读处理出错: {e}")
