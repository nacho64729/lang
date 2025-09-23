# -*- coding: utf-8 -*-
import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; char-scraper/1.0)",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 12
SLEEP_BETWEEN = 0.4  # be gentle to the site

def safe_extract_pinyin_and_def(phrase: str):
    """Robustly extract [pinyin] and '- definition' parts; return (pinyin, definition) or (None, None)."""
    # trim anything after 'radical' if present
    phrase = phrase.split("radical", 1)[0].strip()

    pinyin = None
    definition = None

    # pinyin inside first [...] if present
    if "[" in phrase and "]" in phrase:
        try:
            pinyin = phrase.split("[", 1)[1].split("]", 1)[0].strip()
        except Exception:
            pinyin = None

    # definition after first "- " if present
    if "- " in phrase:
        try:
            definition = phrase.split("- ", 1)[1].strip()
        except Exception:
            definition = None

    return pinyin, definition

def get_pnyn_def(char, session: requests.Session):
    encoded_char = urllib.parse.quote(char)
    url = f"https://www.chinesehideout.com/tools/strokeorder.php?c={encoded_char}"

    for attempt in range(3):
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            header = soup.find('div', id='mydef')
            if not header:
                return None, None
            phrase = header.get_text(strip=True)
            return safe_extract_pinyin_and_def(phrase)
        except Exception:
            if attempt == 2:
                return None, None
            time.sleep(0.6 + attempt * 0.4)

def parse_to_dict(s: str) -> dict:
    result = {}
    for line in s.strip().split("\n"):
        if not line.strip():
            continue
        key, val = line.split("\t", 1)  # split only at the first tab
        result[key] = val
    return result

def main():
    raw_data = """第一课：开学\t辆 研 究 弓 内 全 较 省 由 处 拉 柯 林
第二课：宿舍生活\t屋 摆 毯 柜 挂 门 调 栋 旧 恐 品 层 般 着 急
第三课：在饭馆儿\t留 鸡 蒸 芥 兰 嫩 菠 鲜 淡 咸 油 巾 筷 各 虑 主 微 丽 莎 梅 杭 川 湖
第四课：买东西\t恤 仔 无 论 需 牙 膏 粉 购 价 纯 棉 髦 质 量 标 乎 税
第五课：选课\t选 世 界 历 史 其 章 轻 松 授 讨 碰 毕 济 决 解 建 议 管 谈 将 挣 融 数 交 哲 申
第六课：男朋友女朋友\t朗 迷 相 底 背 景 根 陪 答 原 虎 停 歉 态 度 丢 三 钥 匙
第七课：电脑和网络\t络 闻 资 戏 博 载 软 结 杂 志 垃 圾 落 伍 食 迟 害 敢 待 瘾 严 代 助 翻 译 免
第八课：打工\t良 育 存 入 供 减 负 响 庭 取 验 零 奖 府 贷 款 农 村 低 遛 猫 读 借 欠 银 怪 乖
第九课：教育\t移 士 设 嫂 硕 婚 幸 福 厉 侄 排 钢 琴 画 怨 尊 择 反 童 龙 凤 番 墨
第十课：中国地理\t乡 火 船 风 河 流 部 山 漠 条 形 积 倍 挤 季 族 哈 尔 滨 疆 江 津 深 圳 云
第十一课：中国的节日\t舅 区 环 境 夕 墙 贴 倒 奇 酒 举 顺 利 剩 浪 余 传 统 粽 饼 团 宵 嘛 拜 恭 财 闹 鞭 炮 端 恩
第十二课：中国的变化\t变 及 街 盖 骑 装 筑 尝 句 尽 厦 座 声 咕 噜 夫 庙
第十三课：去云南旅游\t享 参 括 通 硬 铺 厢 顿 盒 幽 默 俗 惯 览 石 树 讲 故 塔 纪 万 笼 昆
第十四课：生活与健康\t与 妻 退 必 散 锻 炼 拳 晨 瑜 伽 注 于 肥 随 即 使 营 饱 科 须 吸 烟 熬 补 充 眠 熊
第十五课：男女平等\t妇 情 况 逐 渐 改 革 企 厂 酬 性 丈 互 模 范 队 厌 骄 傲 输 绩 职 薪 消 赢 冠 军 乒 乓 德
第十六课：环境保护与节约能源\t源 爬 益 段 推 雾 霾 筒 扔 阳 板 煤 规 温 赞 汗 砍 塑 袋 污 染 造 克 摄 氏
第十七课：理财与投资\t俭 投 涨 炒 股 引 姑 矛 盾 郁 闷 孙 未 劝 辛 苦 增 突 义 赚 抵 跌 赔
第十八课：中国历史\t之 观 朝 伟 展 皇 帝 贡 献 修 杀 宫 殿 坟 墓 兵 俑 丝 绸 贸 诗 达 技 术 曾 指 领 命 立 孔 秦 唐 宋 华
第十九课：面试\t跨 归 龟 满 销 湿 总 肃 吓 释 阴 寄 既 产 晴 缺 善 优 握
第二十课：世界变小了\t聚 庆 饯 锅 池 剧 搞 熟 稳 永 联 谊 欧 洲"""

    data_dict = parse_to_dict(raw_data)
    session = requests.Session()

    for lesson_name, chars in data_dict.items():
        base_dir = f"./output_chars/{lesson_name}"
        for char in chars.split():  # <= split the value string into tokens
            print(f"Fetching: {char}")
            pinyin, definition = get_pnyn_def(char, session)

            # make directory for this character (creates lesson folder too)
            char_dir = os.path.join(base_dir, char)
            os.makedirs(char_dir, exist_ok=True)

            info_path = os.path.join(char_dir, "info.txt")
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(f"Character: {char}\n")
                f.write(f"Pinyin: {pinyin or ''}\n")
                f.write(f"Definition: {definition or ''}\n")

            time.sleep(SLEEP_BETWEEN)

        print(f"\nAll character folders saved under: {base_dir}")

if __name__ == "__main__":
    main()
