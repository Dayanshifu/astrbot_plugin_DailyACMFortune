from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
from datetime import datetime, timedelta
import json
import os

events_list = [
    ["背诵课文", "看一遍就背下来了", "记忆力只有 50 Byte"],
    ["参加模拟赛", "可以AK虐全场", "注意爆零"],
    ["吃饭", "人是铁饭是钢", "小心变胖啊"],
    ["重构代码", "代码质量明显提高", "越改越乱"],
    ["发朋友圈", "分享是种美德", "会被当做卖面膜的"],
    ["开电脑", "电脑的状态也很好", "意外的死机故障不可避"],
    ["考试", "学的全会，蒙的全对", "作弊会被抓"],
    ["膜拜大神", "接受神犇光环照耀", "被大神鄙视"],
    ["纳财", "要到好多 Money", "然而今天并没有财运"],
    ["上课", "100% 消化", "反正你听不懂"],
    ["刷题", "成为虐题狂魔", "容易 WA"],
    ["睡觉", "养足精力，明日再战", "翻来覆去睡不着"],
    ["体育锻炼", "身体棒棒哒", "消耗的能量全吃回来了"],
    ["玩网游", "犹如神助", "匹配到一群猪队友"],
    ["写作业", "都会写，写的全对", "上课讲了这些了吗"],
    ["装逼", "获得众人敬仰", "被识破"],
    ["装弱", "谦虚最好了", "被看穿"],
    ["熬夜", "事情终究是可以完成的", "爆肝"],
    ["出行", "一路顺风", "路途必然坎坷"],
    ["扶老奶奶过马路", "RP++", "会被讹"],
    ["搞基", "友谊地久天长", "会被掰弯"],
    ["祭祀", "获得祖宗的庇护", "祖宗不知干啥就不鸟你"],
    ["继续完成WA的题", "下一次就可以 AC 了", "然而变成了 TLE"],
    ["泡妹子", "说不定可以牵手", "一定会被拒绝"],
    ["上B站", "愉悦身心", "会被老师发现"],
    ["洗澡", "你多久没洗澡了？", "当心着凉"],
    ["写作文", "非常有文采", "不知所云，离题千里"],
    ["学数论", "数论大法好", "咋看都不会"],
    ["学习珂学", "珂朵莉太可爱了", "珂朵莉不知干啥不理你"],
    ["唱歌", "成为歌神", "别人唱歌要钱，你要命"],
    ["抽卡", "一发入魂", "只有保底"],
    ["出公开赛", "rated，评价很高", "出了原题裸题错题不可做题"],
    ["打东方", "All clear!", "满身疮痍"],
    ["打线上公开赛", "涨很多 rating", "掉大分"],
    ["点外卖", "及时送到", "一直没有送到还不给退款"],
    ["放假", "自由自在的一个假期", "就放一天，全是作业"],
    ["交友", "友谊地久天长", "交友不慎"],
    ["卷题", "水平显著提升", "我咋啥都不会"],
    ["看视频网站", "愉悦身心", "会被老师看见"],
    ["摸鱼", "放松身心", "被老师制裁"],
    ["骗分", "不可以，总司令然后拿一半分", "一分不得"],
    ["抢最优解", "一发就是最优解", "越卡常越慢"],
    ["切水题", "通过数猛涨", "被抓抄题解"],
    ["请教问题", "获得大佬的解答", "被当作 xxs"],
    ["去食堂", "给了双倍的量", "爱吃的菜刚被打完"],
    ["上厕所", "想出了题目的解法", "被机房惨案"],
    ["上洛谷", "全方位提升", "你谷日爆"],
    ["水讨论区", "看到有趣的事情", "和其他人激情对线"],
    ["贴贴", "说不定擦出火花", "一定会被拒绝"],
    ["玩我的世界", "下界挖到远古遗骸", "转角遇到苦力怕"],
    ["网购", "买到历史最低价", "正好错过促销"],
    ["写暴戾语言", "成功发泄", "禁赛一年"],
    ["写洛谷日报", "文思泉涌，下笔如有神", "发现还差得远"],
    ["写题解", "一遍通过审核", "连续提交不符合要求"],
    ["学新算法", "看一遍就懂了", "怎么也学不会"],
    ["造数据", "严谨数据，经久耐用", "数据出锅，当众谢罪"],
]
special_events = {
    (6, 7): ["高考", "考的全会，蒙的全对"],
    (6, 8): ["高考", "考的全会，蒙的全对"],
    (6, 9): ["高考", "考的全会，蒙的全对"],
    (11, 1): ["参加 CSP", "祝您 RP++"],
    (11, 29): ["参加 NOIP", "祝您 RP++"],
    (15, 23): ["参加省选", "祝您 RP++"],
    (17, 20): ["参加 NOI", "捧杯稳了"]
}

fortune_levels = [
    ("大凶", 1),
    ("凶", 3),
    ("中平", 3),
    ("吉", 2),
    ("小吉", 2),
    ("中吉", 2),
    ("大吉", 1)
]
special_fortune_levels = [
    ("吉", 2),
    ("小吉", 2),
    ("中吉", 2),
    ("大吉", 1)
]

DATA_FILE = "fortune_data.json"

@register("astrbot_plugin_dailyacmfortune", "Dayanshifu", "洛谷运势", "1.0.0", "https://github.com/Dayanshifu/astrbot_plugin_dailyacmfortune")
class FortunePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.fortune_data = {}
        self.load_data()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.fortune_data = json.load(f)
            except Exception as e:
                logger.error(f"加载运势数据失败: {e}")
                self.fortune_data = {}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.fortune_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存运势数据失败: {e}")

    def get_continuous_days(self, user_id: str, today: datetime) -> int:
        if user_id not in self.fortune_data:
            return 0
            
        user_record = self.fortune_data[user_id]
        if "checkin_history" not in user_record:
            return 0
            
        checkin_dates = user_record["checkin_history"]
        if not checkin_dates:
            return 0
            
        # 按日期排序
        sorted_dates = sorted(checkin_dates, reverse=True)
        
        # 检查连续打卡
        continuous_days = 0
        current_date = today.date()
        
        for i, date_str in enumerate(sorted_dates):
            checkin_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected_date = current_date - timedelta(days=i)
            
            if checkin_date == expected_date:
                continuous_days += 1
            else:
                break
                
        return continuous_days

    def update_checkin_history(self, user_id: str, today: datetime):
        today_str = today.strftime("%Y-%m-%d")
        
        if user_id not in self.fortune_data:
            self.fortune_data[user_id] = {"checkin_history": []}
        elif "checkin_history" not in self.fortune_data[user_id]:
            self.fortune_data[user_id]["checkin_history"] = []
            
        if today_str not in self.fortune_data[user_id]["checkin_history"]:
            self.fortune_data[user_id]["checkin_history"].append(today_str)
            self.fortune_data[user_id]["checkin_history"] = self.fortune_data[user_id]["checkin_history"][-30:]

    def get_user_fortune(self, user_id: str, user_name: str, today: datetime) -> dict:
        today_str = today.strftime("%Y-%m-%d")
        
        self.update_checkin_history(user_id, today)
        
        continuous_days = self.get_continuous_days(user_id, today)
        
        if user_id in self.fortune_data:
            user_record = self.fortune_data[user_id]
            if user_record.get("date") == today_str:
                user_record["continuous_days"] = continuous_days
                return user_record
                
        fortune_level, special_event = self.generate_fortune(today)
        random_events = random.sample(events_list, 4)
        quote = f"§ {fortune_level} §\n\n"
        
        if fortune_level == "大吉":
            if special_event:
                quote += (f"宜:{special_event[0]}\n")
                quote += (f"{special_event[1]}\n")
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}")
            else:
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
                quote += (f"宜:{random_events[1][0]}\n")
                quote += (f"{random_events[1][1]}")
            quote += ("\n\n万事皆宜")
        elif fortune_level == "大凶":
            quote += ("诸事不宜\n\n")
            quote += (f"忌:{random_events[2][0]}\n")
            quote += (f"{random_events[2][2]}\n")
            quote += (f"忌:{random_events[3][0]}\n")
            quote += (f"{random_events[3][2]}")
        else:
            if special_event:
                quote += (f"宜:{special_event[0]}\n")
                quote += (f"{special_event[1]}\n")
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
            else:
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
                quote += (f"宜:{random_events[1][0]}\n")
                quote += (f"{random_events[1][1]}\n")
            quote += ("\n")
            quote += (f"忌:{random_events[2][0]}\n")
            quote += (f"{random_events[2][2]}\n")
            quote += (f"忌:{random_events[3][0]}\n")
            quote += (f"{random_events[3][2]}")
            
        new_fortune = {
            "date": today_str,
            "fortune_level": fortune_level,
            "quote": quote,
            "special_event": special_event[0] if special_event else None,
            "random_events": random_events,
            "user_name": user_name,
            "continuous_days": continuous_days
        }
        
        self.fortune_data[user_id].update(new_fortune)
        self.save_data()
        
        return new_fortune

    def generate_fortune(self, today: datetime):
        month = today.month
        day = today.day
        special_event = special_events.get((month, day))
        
        if special_event:
            levels, weights = zip(*special_fortune_levels)
            selected_level = random.choices(levels, weights=weights, k=1)[0]
            return selected_level, special_event
        else:
            levels, weights = zip(*fortune_levels)
            selected_level = random.choices(levels, weights=weights, k=1)[0]
            return selected_level, None

    @filter.command("运势", alias={"今日人品", "运势", "今日运势", "运气", "签到", "打卡"})
    async def helloworld(self, event: AstrMessageEvent):
        today = datetime.now()
        user_id = str(event.get_sender_id())
        user_name = event.get_sender_name()
        user_fortune = self.get_user_fortune(user_id, user_name, today)
        
        continuous_days = user_fortune.get("continuous_days", 0)
        header = f"{user_name}的运势"
        if continuous_days > 0:
            header = f"你已经连续打卡了{continuous_days}天\n{header}"
            
        yield event.plain_result(f"{header}\n{user_fortune['quote']}")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        self.save_data()