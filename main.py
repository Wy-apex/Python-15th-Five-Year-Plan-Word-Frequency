
# “十五五”规划文本热词频率统计
# 功能：中文分词、词频统计、柱状图、中文词云、CSV导出

from pathlib import Path
from collections import Counter
import re

import jieba
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from wordcloud import WordCloud

# 1. 设置文件路径
BASE_DIR = Path(__file__).resolve().parent
TEXT_FILE = BASE_DIR / "data" / "plan.txt"
IMAGE_DIR = BASE_DIR / "images"
RESULT_DIR = BASE_DIR / "results"

IMAGE_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# 2. 读取规划原文
if not TEXT_FILE.exists():
    print("错误：找不到 data/plan.txt 文件")
    raise SystemExit(1)

text = TEXT_FILE.read_text(encoding="utf-8-sig").strip()

if not text:
    print("错误：规划文本内容为空！")
    raise SystemExit(1)

print("===== 十五五规划文本热词频率统计 =====")
print(f"原始文本字符数：{len(text)}")

# 3. 添加专业词汇，减少分词时被拆开的情况
for word in [
    "十五五", "高质量发展", "新质生产力",
    "科技创新", "现代化产业体系", "人工智能",
    "数字经济", "绿色发展", "共同富裕"
]:
    jieba.add_word(word)

# 4. 定义停用词
# 保留“发展”“建设”“创新”等有分析意义的词语
stop_words = {
    "一个", "一些", "一种", "这个", "这些",
    "其中", "以及", "有关", "关于", "按照",
    "通过", "进一步", "不断", "各类",
    "各项", "相关", "方面", "包括",
    "具有", "更加", "同时"
}

# 5. 中文分词
words = jieba.lcut(text)

# 6. 清洗分词结果
valid_words = []

for word in words:
    word = word.strip()

    # 只保留两个字及以上的中文词语
    if len(word) < 2:
        continue

    if not re.fullmatch(r"[\u4e00-\u9fff]+", word):
        continue

    if word in stop_words:
        continue

    valid_words.append(word)

# 7. 统计词频
word_counter = Counter(valid_words)
top20 = word_counter.most_common(20)

print(f"有效分词数量：{len(valid_words)}")
print(f"不同词语数量：{len(word_counter)}")

print("\n===== 高频词 Top 20 =====")
print(f"{'排名':<6}{'词语':<14}出现次数")

for index, (word, count) in enumerate(top20, start=1):
    print(f"{index:<6}{word:<14}{count}")

# 8. 保存完整词频统计表
total_words = len(valid_words)

frequency_data = []

for word, count in word_counter.most_common():
    frequency_data.append({
        "词语": word,
        "出现次数": count,
        "词频占比(%)": round(count / total_words * 100, 4)
    })

df = pd.DataFrame(frequency_data)

csv_file = RESULT_DIR / "word_frequency.csv"

df.to_csv(
    csv_file,
    index=False,
    encoding="utf-8-sig"
)

print(f"\n词频统计表已保存：{csv_file}")

# 9. 查找 Windows 中文字体
font_candidates = [
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc")
]

font_path = next(
    (path for path in font_candidates if path.exists()),
    None
)

if font_path is None:
    print("错误：未找到可用的中文字体！")
    print("请检查 Windows 字体目录。")
    raise SystemExit(1)

chinese_font = FontProperties(fname=str(font_path))

# 10. 绘制 Top 20 高频词柱状图
chart_words = [item[0] for item in top20]
chart_counts = [item[1] for item in top20]

fig, ax = plt.subplots(figsize=(12, 9))

bars = ax.barh(chart_words, chart_counts)

ax.set_yticks(range(len(chart_words)))
ax.set_yticklabels(
    chart_words,
    fontproperties=chinese_font
)

ax.invert_yaxis()

ax.set_title(
    "十五五规划高频词 Top 20",
    fontproperties=chinese_font,
    fontsize=18
)

ax.set_xlabel(
    "出现次数",
    fontproperties=chinese_font
)

ax.bar_label(bars, padding=4)

fig.tight_layout()

chart_file = IMAGE_DIR / "top20_words.png"

fig.savefig(chart_file, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"热词柱状图已保存：{chart_file}")

# 11. 生成中文词云
wordcloud = WordCloud(
    font_path=str(font_path),
    width=1400,
    height=900,
    background_color="white",
    max_words=150,
    collocations=False
)

wordcloud.generate_from_frequencies(
    dict(word_counter)
)

cloud_file = IMAGE_DIR / "wordcloud.png"
wordcloud.to_file(str(cloud_file))

print(f"中文词云已保存：{cloud_file}")

print("\n===== 实验运行完成 =====")
