import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False

# ------------------- 页面配置 浅色治愈主题 -------------------
st.set_page_config(
    page_title="小U - 青少年情绪陪伴机器人",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 浅色系护眼配色
primary_color = "#A8DADC"
bg_color = "#F1FAEE"
text_color = "#1D3557"

# 自定义样式
st.markdown(f"""
<style>
    .stApp {{background-color: {bg_color};}}
    .stButton>button {{background-color: {primary_color}; color: {text_color}; border-radius: 12px;}}
    .stRadio>label {{color: {text_color};}}
    .stChatMessage {{border-radius: 15px; padding: 10px; background-color: #F8F9FA;}}
    [data-testid="stHeader"] {{background-color: rgba(0,0,0,0);}}
    .css-1vq4p4l {{background-color: {primary_color};}}
</style>
""", unsafe_allow_html=True)

# ------------------- 侧边栏导航 -------------------
with st.sidebar:
    st.title("🤍 小U导航")
    page = st.radio(
        "选择功能页面",
        ["📊 实时监测与评估", "👤 个人中心", "🌿 情绪疗愈中心"]
    )

# ------------------- 页面1：实时监测与评估（原主界面） -------------------
def main_page():
    st.title("📊 实时监测与情绪评估")
    st.caption("多模态数据展示 | 专业焦虑评估 | 情绪报告生成")

    # 全局状态初始化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [("robot", "你好，我是小U。接下来我会陪你完成情绪评估，点击选项回答即可。")]
    if "scale_answers" not in st.session_state:
        st.session_state.scale_answers = []
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0

    # GAD-7 专业焦虑量表
    gad7_questions = [
        "过去两周里，你有多少时间感到紧张、焦虑或急躁？",
        "过去两周里，你有多少时间感到无法停止或控制担忧？",
        "过去两周里，你有多少时间对各种事情过度担忧？",
        "过去两周里，你有多少时间很难放松下来？",
        "过去两周里，你有多少时间坐立不安、难以静坐？",
        "过去两周里，你有多少时间变得容易烦恼或易怒？",
        "过去两周里，你有多少时间感到害怕、慌乱或不安？"
    ]
    score_options = ["完全没有", "几天", "一半以上天数", "几乎每天"]
    score_map = {"完全没有":0, "几天":1, "一半以上天数":2, "几乎每天":3}

    # 多模态数据面板
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("😌 面部情绪状态")
        emotion = st.selectbox("实时识别", ["平静放松", "轻微紧张", "中度焦虑", "烦躁不安"], index=0)
    with col2:
        st.subheader("❤️ 生理指标(HRV)")
        rmssd = st.slider("RMSSD(ms) 心率变异性", 10, 80, 45)
        if rmssd >= 50:
            hrv_risk = "✅ 状态极佳"
            hrv_desc = "身体放松，情绪调节能力正常"
        elif rmssd >= 30:
            hrv_risk = "☁️ 轻微疲劳"
            hrv_desc = "身体状态良好，适度休息即可"
        elif rmssd >= 20:
            hrv_risk = "🌧️ 需放松"
            hrv_desc = "身体处于紧张状态，建议放松调节"
        else:
            hrv_risk = "💤 建议休息"
            hrv_desc = "身体负荷较高，需要及时休息调整"
        st.metric("身心状态", hrv_risk)
    with col3:
        st.subheader("🎤 语音情绪状态")
        voice = st.selectbox("语音情感分析", ["放松温和", "平稳正常", "紧张急促", "压抑低沉"], index=0)

    # HRV实时波形
    st.subheader("📈 实时身心波形监测")
    fig, ax = plt.subplots(figsize=(9, 3), facecolor=bg_color)
    t = np.linspace(0, 15, 300)
    hrv_wave = 0.8 * np.sin(2 * np.pi * 0.3 * t) + 0.2 * np.random.randn(len(t))
    ax.plot(t, hrv_wave, color=primary_color, linewidth=2.5, alpha=0.8)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_ylabel("情绪波动强度", color=text_color)
    ax.set_xlabel("时间 (s)", color=text_color)
    ax.set_title(f"当前RMSSD：{rmssd} ms | {hrv_risk}", color=text_color)
    ax.fill_between(t, hrv_wave, color=primary_color, alpha=0.1)
    plt.tight_layout()
    st.pyplot(fig)

    # 放松音乐模块
    st.divider()
    st.subheader("🎵 放松音乐（可切换播放）")
    music_list = {
        "音乐1（放松）": r"C:\Users\王克京\Desktop\robot\music1.mp3",
        "音乐2（冥想）": r"C:\Users\王克京\Desktop\robot\music2.mp3",
        "音乐3（白噪音）": r"C:\Users\王克京\Desktop\robot\music3.mp3"
    }
    selected_music = st.selectbox("选择背景音乐", list(music_list.keys()))
    try:
        with open(music_list[selected_music], "rb") as f:
            audio_data = f.read()
        st.audio(audio_data, format="audio/mp3")
    except:
        st.info("💡 请将MP3音乐文件放入 robot 文件夹，即可播放")
    st.caption("评估过程中可播放音乐，缓解紧张情绪")

    # 对话与评估模块
    st.divider()
    st.subheader("💬 小U陪伴对话 & 情绪评估")
    for role, text in st.session_state.chat_history:
        with st.chat_message("小U" if role == "robot" else "你"):
            st.write(text)

    if st.session_state.current_q < len(gad7_questions):
        st.info(f"📝 第 {st.session_state.current_q + 1}/7 题")
        question = gad7_questions[st.session_state.current_q]
        answer = st.radio(question, score_options, horizontal=True, key=f"q_{st.session_state.current_q}")

        if st.button("✅ 提交答案", type="primary"):
            st.session_state.scale_answers.append(score_map[answer])
            st.session_state.chat_history.append(("user", answer))
            st.session_state.current_q += 1
            
            if st.session_state.current_q < len(gad7_questions):
                st.session_state.chat_history.append(("robot", "已记录，进入下一题"))
            else:
                st.session_state.chat_history.append(("robot", "评估已完成，正在为你生成情绪分析报告"))
                st.session_state.report_generated = True
            st.rerun()

    # 情绪报告模块
    st.divider()
    if st.session_state.report_generated:
        st.header("📄 小U·情绪分析报告")
        total_scale_score = sum(st.session_state.scale_answers)
        
        emotion_score = {"平静放松":0, "轻微紧张":1, "中度焦虑":2, "烦躁不安":3}[emotion]
        voice_score = {"放松温和":0, "平稳正常":1, "紧张急促":2, "压抑低沉":3}[voice]
        hrv_score = 0 if rmssd>=50 else 1 if rmssd>=30 else 2 if rmssd>=20 else 3
        final_score = total_scale_score * 0.5 + (hrv_score*5) * 0.3 + ((emotion_score+voice_score)*2.5) * 0.2

        if final_score < 5:
            level = "🟢 身心状态良好"
            tip = "当前情绪稳定，保持良好的生活状态即可。"
        elif final_score < 10:
            level = "🟡 轻微疲劳状态"
            tip = "存在轻微压力，通过休息和放松可快速恢复。"
        elif final_score < 15:
            level = "🟠 中度焦虑状态"
            tip = "近期压力较大，建议进行规律的放松调节。"
        else:
            level = "🔴 需关注情绪状态"
            tip = "建议及时与家人、老师沟通，或寻求专业心理支持。"

        col1, col2 = st.columns(2)
        with col1:
            st.metric("量表总分", f"{total_scale_score} 分")
        with col2:
            st.metric("综合状态", level)
        st.info(tip)
        
        with st.expander("🌸 身心状态综合解读", expanded=True):
            st.markdown(f"✅ **心理状态**：{['无焦虑','轻度焦虑','中度焦虑','重度焦虑'][[total_scale_score<=4, total_scale_score<=9, total_scale_score<=14, True].index(True)]}")
            st.markdown(f"✅ **生理状态**：{hrv_desc}")
            st.markdown(f"✅ **外在状态**：面部{emotion} | 语音{voice}")

        with st.expander("💌 专业调节建议", expanded=True):
            st.subheader("🌿 生理放松方法")
            st.write("1. 深呼吸训练：吸气4秒→屏息7秒→呼气8秒")
            st.write("2. 每日聆听放松音乐，每次10-15分钟")
            st.write("3. 保证充足睡眠，稳定自主神经功能")
            st.subheader("🌿 生活调节建议")
            st.write("适度进行户外运动，减少电子产品使用时间")
            st.write("有情绪困扰时，及时与信任的人沟通交流")

# ------------------- 页面2：个人中心 -------------------
def personal_center_page():
    st.title("👤 个人中心")
    st.caption("个人信息管理 | 历史报告查看 | 个性化设置")

    # 个人信息编辑
    st.subheader("📝 个人信息")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("昵称", value="小用户", disabled=False)
        st.number_input("年龄", min_value=10, max_value=18, value=15)
    with col2:
        st.selectbox("性别", ["男", "女", "不愿透露"], index=0)
        st.text_area("个性签名", value="每天都要开心一点~")
    st.button("💾 保存信息", type="primary")

    # 历史报告记录
    st.divider()
    st.subheader("📊 历史情绪报告")
    report_data = [
        {"日期": "2026-03-14", "综合评分": "6.2分", "状态": "🟡 轻微疲劳"},
        {"日期": "2026-03-12", "综合评分": "4.1分", "状态": "🟢 身心良好"},
        {"日期": "2026-03-10", "综合评分": "8.5分", "状态": "🟠 中度焦虑"}
    ]
    for report in report_data:
        with st.expander(f"{report['日期']} | {report['状态']} | {report['综合评分']}"):
            st.write("✅ 心理状态：轻度焦虑")
            st.write("✅ 生理状态：轻微疲劳")
            st.write("💡 建议：增加户外运动，保证充足睡眠")

    # 收藏的疗愈资源
    st.divider()
    st.subheader("❤️ 收藏的疗愈资源")
    st.write("- 478呼吸引导训练")
    st.write("- 冥想纯音乐（音乐2）")
    st.write("- 考前焦虑缓解指南")

# ------------------- 页面3：情绪疗愈中心 -------------------
def healing_center_page():
    st.title("🌿 情绪疗愈中心")
    st.caption("放松干预工具 | 个性化疗愈方案 | 情绪调节资源")

    # 快速放松工具
    st.subheader("🚀 快速放松工具")
    tool = st.selectbox(
        "选择放松方式",
        ["478呼吸引导", "正念冥想", "情绪日记", "自然白噪音"]
    )

    if tool == "478呼吸引导":
        st.info("🧘 478呼吸法：吸气4秒 → 屏息7秒 → 呼气8秒")
        st.progress(0)
        st.button("开始引导", type="primary")
    elif tool == "正念冥想":
        st.video("https://www.youtube.com/watch?v=inpok4MKVbs")  # 示例冥想视频
        st.caption("5分钟正念冥想引导，帮助平复情绪")
    elif tool == "情绪日记":
        st.text_area("记录今天的心情...", height=150)
        st.button("💾 保存日记", type="primary")
    elif tool == "自然白噪音":
        st.audio("https://assets.mixkit.co/sfx/preview/mixkit-clear-forest-stream-ambience-2559.mp3", format="audio/mp3")
        st.caption("森林白噪音，帮助平复焦虑情绪")

    # 场景化疗愈方案
    st.divider()
    st.subheader("📋 场景化疗愈方案")
    scenario = st.selectbox(
        "选择当前场景",
        ["考前焦虑", "社交压力", "日常放松", "情绪低落"]
    )
    if scenario == "考前焦虑":
        st.write("1. 考前10分钟进行3组478呼吸训练")
        st.write("2. 听5分钟自然白噪音")
        st.write("3. 积极心理暗示：我已经准备充分了")
    elif scenario == "社交压力":
        st.write("1. 提前准备对话话题，减少临场紧张")
        st.write("2. 社交前进行5分钟正念冥想")
        st.write("3. 关注自身感受，不必过度在意他人评价")

    # 专业心理资源
    st.divider()
    st.subheader("📚 专业心理资源")
    st.write("- [全国心理援助热线](https://www.cmhc.org.cn/)")
    st.write("- 青少年情绪调节推荐书籍：《情绪急救》")
    st.write("- 学校心理咨询室预约方式：XXX-XXXXXXX")

# ------------------- 页面路由 -------------------
if page == "📊 实时监测与评估":
    main_page()
elif page == "👤 个人中心":
    personal_center_page()
elif page == "🌿 情绪疗愈中心":
    healing_center_page()