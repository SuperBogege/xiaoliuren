import streamlit as st
import datetime
import pytz

# 尝试导入农历转换库
try:
    from lunarcalendar import Converter, Solar
except ImportError:
    st.error("请先在终端运行: pip install lunarcalendar")
    st.stop()

class XiaoLiuRen:
    def __init__(self):
        self.gods = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]
        self.shichen = ["子时(23-1点)", "丑时(1-3点)", "寅时(3-5点)", "卯时(5-7点)",
                        "辰时(7-9点)", "巳时(9-11点)", "午时(11-13点)", "未时(13-15点)",
                        "申时(15-17点)", "酉时(17-19点)", "戌时(19-21点)", "亥时(21-23点)"]

        self.god_details = {
            '大安': {'五行': '木', '方位': '东方', '吉凶': '大吉', 'summary': '身不动时，属木，主安稳、缓慢、贵人。',
                     'interpretation': '代表安稳，适合长期决策，凡事求稳，不宜急躁。'},
            '留连': {'五行': '土', '方位': '东南', '吉凶': '中平', 'summary': '卒未归时，属土，主拖延、纠缠、反复。',
                     'interpretation': '事情可能拖延，进展缓慢，需更多时间和耐心，不可冲动。'},
            '速喜': {'五行': '火', '方位': '南方', '吉凶': '吉', 'summary': '人即至时，属火，主快速、喜讯、文书。',
                     'interpretation': '好运将至，适合快速行动，机会来临，但需谨慎筛选。'},
            '赤口': {'五行': '金', '方位': '西方', '吉凶': '凶', 'summary': '官事凶时，属金，主口舌、争斗、伤灾。',
                     'interpretation': '容易发生争执或官非，需谨慎言行，避免冲突，宜守不宜攻。'},
            '小吉': {'五行': '水', '方位': '西南', '吉凶': '小吉', 'summary': '人来喜时，属水，主小利、桃花、出行。',
                     'interpretation': '事情有小利，适合轻松事务，虽无大成就但过程顺利。'},
            '空亡': {'五行': '土', '方位': '北方', '吉凶': '大凶', 'summary': '音信稀时，属土，主虚无、落空、意外。',
                     'interpretation': '事情可能停滞或落空，宜反思调整，避免冒进，静待时机。'}
        }

        self.matters_category = {
            '1': '婚姻感情', '2': '财运得失', '3': '疾病健康', '4': '失物寻人',
            '5': '出行安全', '6': '官非是非', '7': '学业功名', '8': '家宅风水',
            '9': '生育子嗣', '10': '职业选择', '11': '天气占验', '12': '择吉择日', '13': '梦境吉凶'
        }

    def get_shichen_index(self, hour):
        # 23点和0点都属于子时（索引为0）
        if hour == 23 or hour == 0: 
            return 0
        return (hour + 1) // 2

    def calculate(self, lunar_month, lunar_day, shichen_index):
        # 传统小六壬算法：月上起日，日上起时
        month_index = (lunar_month - 1) % 6
        day_index = (month_index + lunar_day - 1) % 6
        final_index = (day_index + shichen_index) % 6
        return self.gods[final_index]

# 初始化
diviner = XiaoLiuRen()

# --- 网页界面开始 ---
st.set_page_config(page_title="小六壬占卜", page_icon="🔮", layout="centered")
st.title("🔮 小六壬在线占卜")
st.markdown("---")

# 选择起卦方式
mode = st.radio("请选择起卦方式：", ("时间起卦 (使用当前时间)", "数字起卦 (随机报三个数字)"))

# 使用 session_state 来保存起卦结果
if 'final_god' not in st.session_state:
    st.session_state.final_god = None
if 'divination_info' not in st.session_state:
    st.session_state.divination_info = ""

if mode == "时间起卦 (使用当前时间)":
    if st.button("⏰ 立即起卦"):
        # 【核心修复】：强制获取北京时间（东八区），防止服务器时区错误
        beijing_tz = pytz.timezone('Asia/Shanghai')
        target_date = datetime.datetime.now(beijing_tz)
        
        # 【核心修复】：处理23点后的“子时跨日”问题
        actual_date_for_lunar = target_date
        if target_date.hour >= 23:
            actual_date_for_lunar = target_date + datetime.timedelta(days=1)

        solar_obj = Solar(actual_date_for_lunar.year, actual_date_for_lunar.month, actual_date_for_lunar.day)
        lunar = Converter.Solar2Lunar(solar_obj)
        
        hour = target_date.hour
        shichen_idx = diviner.get_shichen_index(hour)

        # 计算结果并存入“备忘录”
        st.session_state.final_god = diviner.calculate(lunar.month, lunar.day, shichen_idx)
        st.session_state.divination_info = f"📅 占卜时间: {target_date.strftime('%Y-%m-%d %H:%M')} | 🌙 农历: {lunar.year}年{lunar.month}月{lunar.day}日 | ⏰ 时辰: {diviner.shichen[shichen_idx]}"

else:
    st.write("请在心中默念所求之事，然后随机输入三个数字（用空格隔开）")
    user_input = st.text_input("输入三个数字 (例如: 3 15 8)", "")
    if st.button("🔢 开始数字起卦"):
        try:
            nums = [int(x) for x in user_input.split()]
            if len(nums) == 3:
                # 【优化】：数字起卦的大数取余规则（除以6取余，余数为0按6算）
                month_num = nums[0] % 6 if nums[0] % 6 != 0 else 6
                day_num = nums[1] % 6 if nums[1] % 6 != 0 else 6
                hour_num = nums[2] % 6 if nums[2] % 6 != 0 else 6
                
                # 转换为索引（索引从0开始，所以减1）
                shichen_idx = hour_num - 1 
                
                # 计算结果并存入“备忘录”
                st.session_state.final_god = diviner.calculate(month_num, day_num, shichen_idx)
                st.session_state.divination_info = f"起卦数字: {nums[0]} (起因), {nums[1]} (过程), {nums[2]} (结果)"
            else:
                st.error("❌ 必须输入正好三个数字！")
        except ValueError:
            st.error("❌ 格式错误，请输入三个用空格隔开的整数！")

# 显示结果（从“备忘录”里读取）
if st.session_state.final_god:
    st.markdown("---")
    st.success(st.session_state.divination_info)

    final_god = st.session_state.final_god
    details = diviner.god_details[final_god]

    st.header(f"🔮 最终落宫: 【{final_god}】")
    st.write(f"**方位:** {details['方位']}  |  **五行:** {details['五行']}  |  **吉凶:** {details['吉凶']}")
    st.write(f"**卦辞:** {details['summary']}")
    st.write(f"**综合建议:** {details['interpretation']}")

    st.markdown("---")
    st.subheader("👉 请选择你想占卜的具体事项：")

    matter_labels = [f"{k}. {v}" for k, v in diviner.matters_category.items()]
    selected_matter = st.selectbox("选择事项", matter_labels)

    if selected_matter:
        selected_key = selected_matter.split('.')[0]
        matter_name = diviner.matters_category[selected_key]

        st.info(f"📋 针对【{matter_name}】的专项解读：")
        st.write(f"🔮 **落宫:** {final_god} ({details['吉凶']})")
        st.write(f"📖 **建议:** 在{matter_name}方面，{details['interpretation']}")
        st.write(f"🧭 **提示:** 有利方位在{details['方位']}，五行属性为{details['五行']}。")
