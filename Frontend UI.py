import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import base64
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="青少年焦虑状态智能陪伴机器人",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }

    .metric-card.small {
        padding: 0.8rem;
        margin: 0.2rem;
    }

    .metric-card.small h4 {
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .metric-card.small h2 {
        font-size: 1.2rem;
        margin: 0;
    }

    .status-normal {
        color: #28a745;
        font-weight: bold;
    }

    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }

    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }

    .realtime-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #28a745;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 5px;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 70%;
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        margin-right: 1rem;
        text-align: right;
        flex-direction: row-reverse;
    }

    .bot-message {
        background-color: #f3e5f5;
        margin-left: 1rem;
        margin-right: auto;
        text-align: left;
    }

    .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .message-content {
        flex: 1;
    }

    .chat-input-container {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }

    .chat-input-container input {
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'gad7_answers' not in st.session_state:
    st.session_state.gad7_answers = {}
if 'gad7_current_question' not in st.session_state:
    st.session_state.gad7_current_question = 0
if 'monitoring_data' not in st.session_state:
    st.session_state.monitoring_data = {
        'facial': [],
        'hrv': [],
        'voice': [],
        'timestamps': []
    }
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = {
        'dates': [],
        'anxiety_scores': []
    }
if 'show_gad7' not in st.session_state:
    st.session_state.show_gad7 = False
if 'playing_music' not in st.session_state:
    st.session_state.playing_music = False

# GAD-7焦虑自评表问题
gad7_questions = [
    "在过去两周内，您感到紧张、焦虑或急切吗？",
    "在过去两周内，您不能停止或控制担忧吗？",
    "在过去两周内，您对各种各样的事情担忧过多吗？",
    "在过去两周内，您感到很难放松下来吗？",
    "在过去两周内，您变得容易烦躁或急躁吗？",
    "在过去两周内，您感到好像有什么可怕的事发生吗？",
    "在过去两周内，您感到无法静坐吗？"
]

# 机器人回复模板
bot_intro = "你好！我是小U，你的智能陪伴机器人。我可以帮你监测和管理焦虑状态，让我们一起开始吧！"

# 侧边栏导航
with st.sidebar:
    st.markdown("### 🤖 智能陪伴机器人小U")
    st.markdown("---")

    if st.button("🏠 心情监测中心", width='stretch'):
        st.session_state.page = 'home'

    if st.button("💝 情绪疗愈中心", width='stretch'):
        st.session_state.page = 'healing'

    if st.button("👤 个人中心", width='stretch'):
        st.session_state.page = 'profile'



# 心情监测中心页面
if st.session_state.page == 'home':
    st.markdown('<div class="main-header"><h1>🏠 心情监测中心</h1><p>多模态焦虑状态实时监测与分析</p></div>',
                unsafe_allow_html=True)

    # 实时监测区域
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><h3>😊 面部表情分析</h3></div>', unsafe_allow_html=True)

        # 模拟面部表情数据 - 八种情绪
        emotion_labels = ['中性', '开心', '难过', '生气', '惊讶', '害怕', '厌恶', '轻蔑']
        emotion_values = np.random.dirichlet(np.ones(8), size=1)[0]

        fig_emotion = go.Figure(data=[go.Pie(
            labels=emotion_labels,
            values=emotion_values,
            hole=0.4,
            marker_colors=['#9E9E9E', '#4CAF50', '#2196F3', '#F44336', '#FF9800', '#FF5722', '#9C27B0', '#607D8B']
        )])
        fig_emotion.update_traces(textinfo='label+percent')
        fig_emotion.update_layout(
            title="当前情绪分布",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_emotion, width='stretch')

        dominant_emotion = emotion_labels[np.argmax(emotion_values)]
        if dominant_emotion in ['生气', '害怕', '厌恶', '轻蔑']:
            st.markdown(f'<p class="status-danger">主导情绪: {dominant_emotion}</p>', unsafe_allow_html=True)
        elif dominant_emotion == '难过':
            st.markdown(f'<p class="status-warning">主导情绪: {dominant_emotion}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="status-normal">主导情绪: {dominant_emotion}</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h3>❤️ HRV健康监测</h3></div>', unsafe_allow_html=True)

        # 模拟HRV数据
        hrv_value = np.random.uniform(30, 100)
        hrv_status = "正常" if hrv_value > 50 else "偏低"

        fig_hrv = go.Figure(go.Indicator(
            mode="gauge+number",
            value=hrv_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "HRV指数"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 30], 'color': "#F44336"},
                    {'range': [30, 50], 'color': "#FF9800"},
                    {'range': [50, 100], 'color': "#4CAF50"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_hrv.update_layout(height=300)
        st.plotly_chart(fig_hrv, width='stretch')

        if hrv_status == "正常":
            st.markdown(f'<p class="status-normal">HRV状态: {hrv_status}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="status-warning">HRV状态: {hrv_status}</p>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><h3>🎤 语音情绪分析</h3></div>', unsafe_allow_html=True)

        # 模拟语音情绪数据
        voice_emotion = np.random.choice(['平静', '焦虑', '紧张', '放松'])
        voice_intensity = np.random.uniform(0, 100)

        fig_voice = go.Figure(go.Bar(
            x=['平静度', '焦虑度', '紧张度', '放松度'],
            y=np.random.dirichlet(np.ones(4), size=1)[0] * 100,
            marker_color=['#4CAF50', '#FF9800', '#F44336', '#2196F3']
        ))
        fig_voice.update_layout(
            title="语音情绪指标",
            height=300,
            yaxis_title="百分比 (%)"
        )
        st.plotly_chart(fig_voice, width='stretch')

        if voice_emotion == '焦虑':
            st.markdown(f'<p class="status-danger">语音情绪: {voice_emotion}</p>', unsafe_allow_html=True)
        elif voice_emotion == '紧张':
            st.markdown(f'<p class="status-warning">语音情绪: {voice_emotion}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="status-normal">语音情绪: {voice_emotion}</p>', unsafe_allow_html=True)

    # 开始GAD-7自评表的按钮
    if not st.session_state.show_gad7:
        if st.button("开始焦虑评估", width='stretch'):
            st.session_state.show_gad7 = True
            st.session_state.gad7_answers = {}
            st.session_state.gad7_current_question = 0
            # 重置聊天历史，添加机器人介绍
            st.session_state.chat_history = [
                {'role': 'bot', 'content': bot_intro, 'timestamp': datetime.now()}
            ]
            st.rerun()

    # GAD-7焦虑自评表（对话形式）
    if st.session_state.show_gad7:
        # 焦虑评估对话标题和重新开始按钮
        col_title, col_restart = st.columns([3, 1])
        with col_title:
            st.markdown('<div class="card"><h3>💬 焦虑评估对话</h3></div>', unsafe_allow_html=True)
        with col_restart:
            if st.button("重新开始", key="restart_early"):
                st.session_state.show_gad7 = False
                st.session_state.gad7_answers = {}
                st.session_state.gad7_current_question = 0
                st.session_state.chat_history = []
                st.rerun()

        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(
                        f'<div class="chat-message user-message"><div class="avatar" style="background-color: #4CAF50; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">👤</div><div class="message-content"><strong>你:</strong> {message["content"]}</div></div>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="chat-message bot-message"><div class="avatar" style="background-color: #2196F3; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">🤖</div><div class="message-content"><strong>小U:</strong> {message["content"]}</div></div>',
                        unsafe_allow_html=True)

        # 处理GAD-7问题
        if st.session_state.gad7_current_question < len(gad7_questions):
            # 如果是新问题，添加机器人的问题到聊天历史
            if not st.session_state.chat_history or len(st.session_state.chat_history) == 1 or (st.session_state.chat_history and st.session_state.chat_history[-1]['role'] == 'user'):
                question = gad7_questions[st.session_state.gad7_current_question]
                bot_message = f"问题 {st.session_state.gad7_current_question + 1}/{len(gad7_questions)}: {question}\n\n请回答：1. 完全不会 2. 好几天 3. 一半以上的天数 4. 几乎每天"
                st.session_state.chat_history.append({
                    'role': 'bot',
                    'content': bot_message,
                    'timestamp': datetime.now()
                })
                st.rerun()

            # 用户选择答案（选择题）
            answer_options = ["完全不会", "好几天", "一半以上的天数", "几乎每天"]
            selected_answer = st.radio(
                "请选择你的答案:",
                answer_options,
                index=None,
                key=f"gad7_input_{st.session_state.gad7_current_question}"
            )

            if st.button("发送") and selected_answer:
                # 添加用户答案到聊天历史
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': selected_answer,
                    'timestamp': datetime.now()
                })

                # 保存答案
                st.session_state.gad7_answers[st.session_state.gad7_current_question] = selected_answer

                # 移动到下一个问题或完成
                if st.session_state.gad7_current_question < len(gad7_questions) - 1:
                    st.session_state.gad7_current_question += 1
                    st.rerun()
                else:
                    # 评估完成，生成报告
                    bot_message = "🎉 评估已完成！正在生成分析报告..."
                    st.session_state.chat_history.append({
                        'role': 'bot',
                        'content': bot_message,
                        'timestamp': datetime.now()
                    })
                    # 将current_question设置为len(gad7_questions)，以便进入生成报告的分支
                    st.session_state.gad7_current_question = len(gad7_questions)
                    st.rerun()
        else:
            # 计算GAD-7得分
            score_mapping = {
                "完全不会": 0,
                "好几天": 1,
                "一半以上的天数": 2,
                "几乎每天": 3
            }

            total_score = sum(score_mapping.get(st.session_state.gad7_answers.get(i, "完全不会"), 0) for i in
                              range(len(gad7_questions)))

            # 焦虑等级判定
            if total_score <= 4:
                anxiety_level = "轻度焦虑"
                anxiety_color = "#4CAF50"
            elif total_score <= 9:
                anxiety_level = "中度焦虑"
                anxiety_color = "#FF9800"
            elif total_score <= 14:
                anxiety_level = "中重度焦虑"
                anxiety_color = "#FF5722"
            else:
                anxiety_level = "重度焦虑"
                anxiety_color = "#F44336"

            # 生成焦虑分析报告
            st.markdown('<div class="card"><h3>📊 焦虑分析报告</h3></div>', unsafe_allow_html=True)

            # 报告内容区域
            report_container = st.container()
            with report_container:
                # 基本信息和焦虑等级
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="card" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                        <h2 style="color: {anxiety_color};">{anxiety_level}</h2>
                        <p>GAD-7总分: <strong>{total_score}/21</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    # 四项指标比例（使用监测数据的平均值）
                    # 如果有监测数据，使用平均值；否则使用模拟数据
                    if st.session_state.monitoring_data['hrv']:
                        hrv_score = np.mean(st.session_state.monitoring_data['hrv'])  # HRV分析（使用平均值）
                    else:
                        hrv_score = np.random.uniform(50, 100)  # 默认值
                    
                    if st.session_state.monitoring_data['facial']:
                        facial_score = np.mean(st.session_state.monitoring_data['facial'])  # 表情分析（使用平均值）
                    else:
                        facial_score = np.random.uniform(0, 100)  # 默认值
                    
                    if st.session_state.monitoring_data['voice']:
                        voice_score = np.mean(st.session_state.monitoring_data['voice'])  # 语义分析（使用平均值）
                    else:
                        voice_score = np.random.uniform(0, 100)  # 默认值
                    
                    gad7_score = (total_score / 21) * 100     # 量表

                    # 按照权重计算综合得分
                    # HRV分析30%、语义分析25%、表情分析25%、量表20%
                    weighted_score = (
                        hrv_score * 0.3 +
                        voice_score * 0.25 +
                        facial_score * 0.25 +
                        gad7_score * 0.2
                    )

                    fig_report = go.Figure(data=[
                        go.Bar(name='面部表情', x=['面部表情'], y=[facial_score], marker_color='#2196F3'),
                        go.Bar(name='HRV指标', x=['HRV指标'], y=[hrv_score], marker_color='#4CAF50'),
                        go.Bar(name='语音情绪', x=['语音情绪'], y=[voice_score], marker_color='#FF9800'),
                        go.Bar(name='GAD-7自评', x=['GAD-7自评'], y=[gad7_score], marker_color='#9C27B0')
                    ])
                    fig_report.update_layout(
                        title="四项指标综合分析",
                        barmode='group',
                        height=200
                    )
                    st.plotly_chart(fig_report, width='stretch')

                # 综合评估得分
                st.markdown(f"<div class='card' style='text-align: center; margin-top: 1rem;'><h4>综合评估得分</h4><h2>{weighted_score:.1f}</h2><p>权重: HRV 30% | 语义 25% | 表情 25% | 量表 20%</p></div>", unsafe_allow_html=True)

                # 综合建议
                st.markdown('<div class="card" style="margin-top: 1rem;"><h4>💡 综合建议</h4></div>', unsafe_allow_html=True)

                suggestions = []
                if total_score > 9:
                    suggestions.append("• 您的焦虑水平较高，建议寻求专业心理咨询师的帮助")
                if hrv_value < 50:
                    suggestions.append("• HRV指标偏低，建议进行深呼吸练习和放松训练")
                if dominant_emotion == '焦虑':
                    suggestions.append("• 面部表情显示焦虑情绪，建议尝试冥想或音乐疗法")
                if voice_emotion in ['焦虑', '紧张']:
                    suggestions.append("• 语音情绪分析显示紧张状态，建议进行放松练习")

                if not suggestions:
                    suggestions.append("• 您的各项指标表现良好，继续保持健康的生活方式！")

                # 建议列表
                suggestions_html = "<div style='padding: 0 1rem;'>"
                for suggestion in suggestions:
                    suggestions_html += f"<p>{suggestion}</p>"
                suggestions_html += "</div>"
                st.markdown(suggestions_html, unsafe_allow_html=True)

            # PDF下载功能
            def get_pdf_download_link():
                # 生成HTML内容
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>焦虑分析报告</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
                        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                        .score {{ text-align: center; }}
                        .suggestions {{ margin-top: 20px; }}
                        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class='header'>
                        <h1>焦虑分析报告</h1>
                        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class='grid'>
                        <div class='card'>
                            <h2 style='color: {anxiety_color}; text-align: center;'>{anxiety_level}</h2>
                            <p style='text-align: center;'>GAD-7总分: <strong>{total_score}/21</strong></p>
                        </div>
                        <div class='card'>
                            <h3 style='text-align: center;'>四项指标得分</h3>
                            <p>面部表情: {facial_score:.1f}</p>
                            <p>HRV指标: {hrv_score:.1f}</p>
                            <p>语音情绪: {voice_score:.1f}</p>
                            <p>GAD-7自评: {gad7_score:.1f}</p>
                        </div>
                    </div>
                    
                    <div class='card score'>
                        <h3>综合评估得分</h3>
                        <h2>{weighted_score:.1f}</h2>
                        <p>权重: HRV 30% | 语义 25% | 表情 25% | 量表 20%</p>
                    </div>
                    
                    <div class='card'>
                        <h3>综合建议</h3>
                        <div class='suggestions'>
                            {''.join([f'<p>{s}</p>' for s in suggestions])}
                        </div>
                    </div>
                    
                    <div class='footer'>
                        <p>© 2026 青少年焦虑状态智能陪伴机器人 | 多模态融合分析系统</p>
                    </div>
                </body>
                </html>
                """
                
                # 转换为PDF（这里使用HTML作为PDF内容，实际项目中可以使用更专业的PDF库）
                b64 = base64.b64encode(html_content.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="anxiety_report_{datetime.now().strftime("%Y%m%d")}.html">下载报告</a>'
                return href

            st.markdown(get_pdf_download_link(), unsafe_allow_html=True)

            # 按钮区域
            col_buttons = st.columns(2)
            with col_buttons[0]:
                if st.button("重新开始评估"):
                    st.session_state.show_gad7 = False
                    st.session_state.gad7_answers = {}
                    st.session_state.gad7_current_question = 0
                    st.session_state.chat_history = []
                    st.rerun()
            with col_buttons[1]:
                if st.button("返回首页"):
                    st.session_state.page = 'home'
                    st.rerun()

# 情绪疗愈中心页面
elif st.session_state.page == 'healing':
    st.markdown('<div class="main-header"><h1>💝 情绪疗愈中心</h1><p>多种疗愈方式，助您缓解焦虑</p></div>',
                unsafe_allow_html=True)

    # 疗愈方式选择
    healing_methods = {
        "🧘 冥想练习": {
            "description": "通过正念冥想，帮助您放松身心，缓解焦虑情绪",
            "duration": "10-30分钟",
            "content": [
                "找一个安静的地方，坐下来，闭上眼睛",
                "深呼吸，吸气4秒，屏住呼吸2秒，呼气6秒",
                "专注于你的呼吸，感受空气进出身体",
                "如果思绪飘走，温柔地将注意力拉回到呼吸上",
                "持续练习10-30分钟"
            ]
        },
        "🎵 音乐疗法": {
            "description": "聆听舒缓的音乐，调节情绪，减轻压力",
            "duration": "15-45分钟",
            "content": [
                "选择舒缓的古典音乐、自然声音或轻音乐",
                "戴上耳机，找一个舒适的姿势",
                "闭上眼睛，专注于音乐的旋律",
                "让音乐带走你的烦恼和焦虑",
                "建议每天聆听15-45分钟"
            ]
        },
        "📝 写日记": {
            "description": "通过书写表达情绪，整理思绪，释放压力",
            "duration": "10-20分钟",
            "content": [
                "找一个安静的时间和地点",
                "写下你今天的感受和经历",
                "不要担心语法和拼写，自由表达",
                "写下让你焦虑的事情，以及可能的解决方案",
                "每天坚持写10-20分钟"
            ]
        },
        "🏃 运动释放": {
            "description": "通过运动释放压力，提升心情，改善睡眠",
            "duration": "20-60分钟",
            "content": [
                "选择你喜欢的运动方式（跑步、瑜伽、游泳等）",
                "每周至少进行3-5次运动",
                "运动时注意呼吸节奏",
                "运动后进行适当的拉伸放松",
                "每次运动20-60分钟"
            ]
        },
        "🎨 艺术创作": {
            "description": "通过绘画、手工等艺术活动表达情感，转移注意力",
            "duration": "30-60分钟",
            "content": [
                "准备绘画工具或手工材料",
                "不要追求完美，专注于创作过程",
                "用颜色和形状表达你的情绪",
                "享受创作的乐趣和成就感",
                "每次创作30-60分钟"
            ]
        },
        "💬 智能对话": {
            "description": "与AI陪伴机器人对话，获得情感支持和建议",
            "duration": "灵活",
            "content": [
                "在聊天框中输入你的想法和感受",
                "机器人会倾听并给予回应",
                "可以讨论任何让你困扰的话题",
                "获得情感支持和实用建议",
                "随时开始，随时结束"
            ]
        }
    }

    selected_method = st.selectbox("选择疗愈方式:", list(healing_methods.keys()))

    if selected_method:
        method_info = healing_methods[selected_method]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f'<div class="card"><h3>{selected_method}</h3></div>', unsafe_allow_html=True)
            st.markdown(f"**描述**: {method_info['description']}")
            st.markdown(f"**建议时长**: {method_info['duration']}")

            st.markdown("**操作步骤**:")
            for i, step in enumerate(method_info['content'], 1):
                st.markdown(f"{i}. {step}")

        with col2:
            st.markdown('<div class="card"><h4>📊 疗愈效果</h4></div>', unsafe_allow_html=True)

            # 模拟疗愈效果数据
            before_anxiety = np.random.uniform(50, 90)
            after_anxiety = np.random.uniform(20, 50)

            fig_effect = go.Figure(data=[
                go.Bar(name='疗愈前', x=['焦虑指数'], y=[before_anxiety], marker_color='#FF9800'),
                go.Bar(name='疗愈后', x=['焦虑指数'], y=[after_anxiety], marker_color='#4CAF50')
            ])
            fig_effect.update_layout(
                title="疗愈效果对比",
                barmode='group',
                height=300
            )
            st.plotly_chart(fig_effect, width='stretch')

            improvement = ((before_anxiety - after_anxiety) / before_anxiety) * 100
            st.markdown(f"**焦虑改善**: {improvement:.1f}%")

    # 音乐播放功能
    if selected_method == "🎵 音乐疗法":
        st.markdown('<div class="card"><h4>🎵 音乐播放器</h4></div>', unsafe_allow_html=True)

        # 模拟音乐列表
        music_list = [
            "冥想放松音乐",
            "自然声音 - 雨声",
            "古典音乐 - 莫扎特",
            "白噪音",
            "轻音乐"
        ]

        selected_music = st.selectbox("选择音乐:", music_list)

        # 模拟音乐播放功能
        if st.button("▶️ 播放", key="play_music"):
            st.session_state.playing_music = True
            st.success(f"正在播放: {selected_music}")
            # 显示音乐播放状态
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <p style="margin: 0; color: #4CAF50;">🎵 正在播放: {selected_music}</p>
                <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">音量: 50%</p>
            </div>
            """.format(selected_music=selected_music), unsafe_allow_html=True)

        if st.button("⏸️ 暂停", key="pause_music"):
            st.session_state.playing_music = False
            st.info("音乐已暂停")

        if st.session_state.playing_music:
            st.markdown(f"<p style='color: #4CAF50;'>🎵 正在播放: {selected_music}</p>", unsafe_allow_html=True)

    # 智能对话区域
    if selected_method == "💬 智能对话":
        st.markdown('<div class="card"><h4>💬 与小U对话</h4></div>', unsafe_allow_html=True)

        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(
                        f'<div class="chat-message user-message"><div class="avatar" style="background-color: #4CAF50; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">👤</div><div class="message-content"><strong>你:</strong> {message["content"]}</div></div>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="chat-message bot-message"><div class="avatar" style="background-color: #2196F3; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">🤖</div><div class="message-content"><strong>小U:</strong> {message["content"]}</div></div>',
                        unsafe_allow_html=True)

        # 用户输入
        user_input = st.text_input("输入你的消息:", key="chat_input")

        if st.button("发送") and user_input:
            # 添加用户消息
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })

            # 模拟机器人回复
            responses = [
                "我理解你的感受，这确实是一个让人焦虑的情况。",
                "听起来你正在经历一些挑战，我很愿意倾听你的故事。",
                "你的感受是正常的，很多人都有类似的经历。",
                "深呼吸，放松一下，我们一起想办法解决这个问题。",
                "你已经迈出了寻求帮助的第一步，这很勇敢！",
                "记住，焦虑是可以管理的，你并不孤单。"
            ]
            bot_response = np.random.choice(responses)

            st.session_state.chat_history.append({
                'role': 'bot',
                'content': bot_response,
                'timestamp': datetime.now()
            })

            st.rerun()

        if st.button("清空对话"):
            st.session_state.chat_history = []
            st.rerun()

# 个人中心页面
elif st.session_state.page == 'profile':
    st.markdown('<div class="main-header"><h1>👤 个人中心</h1><p>查看历史监测数据与焦虑状态变化</p></div>',
                unsafe_allow_html=True)

    # 生成模拟历史数据
    if not st.session_state.historical_data['dates']:
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        anxiety_scores = [np.random.uniform(20, 80) for _ in range(30)]

        st.session_state.historical_data['dates'] = dates
        st.session_state.historical_data['anxiety_scores'] = anxiety_scores

    # 焦虑状态变化曲线
    st.markdown('<div class="card"><h3>📈 焦虑状态变化曲线</h3></div>', unsafe_allow_html=True)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=st.session_state.historical_data['dates'],
        y=st.session_state.historical_data['anxiety_scores'],
        mode='lines+markers',
        name='焦虑指数',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6)
    ))

    # 添加趋势线
    z = np.polyfit(range(len(st.session_state.historical_data['anxiety_scores'])),
                   st.session_state.historical_data['anxiety_scores'], 1)
    p = np.poly1d(z)
    fig_trend.add_trace(go.Scatter(
        x=st.session_state.historical_data['dates'],
        y=st.session_state.historical_data['anxiety_scores'],  # Use actual anxiety scores instead of p(range(...))
        mode='lines',
        name='趋势线',
        line=dict(color='#FF9800', width=2, dash='dash')
    ))
    fig_trend.update_layout(
        title="30天焦虑指数变化趋势",
        xaxis_title="日期",
        yaxis_title="焦虑指数",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig_trend, width='stretch')

    # 统计信息
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_score = np.mean(st.session_state.historical_data['anxiety_scores'])
        st.markdown(f'<div class="metric-card small"><h4>平均焦虑指数</h4><h2>{avg_score:.1f}</h2></div>', unsafe_allow_html=True)

    with col2:
        max_score = np.max(st.session_state.historical_data['anxiety_scores'])
        st.markdown(f'<div class="metric-card small"><h4>最高焦虑指数</h4><h2>{max_score:.1f}</h2></div>', unsafe_allow_html=True)

    with col3:
        min_score = np.min(st.session_state.historical_data['anxiety_scores'])
        st.markdown(f'<div class="metric-card small"><h4>最低焦虑指数</h4><h2>{min_score:.1f}</h2></div>', unsafe_allow_html=True)

    with col4:
        current_score = st.session_state.historical_data['anxiety_scores'][-1]
        st.markdown(f'<div class="metric-card small"><h4>当前焦虑指数</h4><h2>{current_score:.1f}</h2></div>',
                    unsafe_allow_html=True)

    # 历史数据表格
    st.markdown('<div class="card"><h3>📋 历史监测数据</h3></div>', unsafe_allow_html=True)

    df = pd.DataFrame({
        '日期': st.session_state.historical_data['dates'],
        '焦虑指数': st.session_state.historical_data['anxiety_scores'],
        '面部表情': [np.random.choice(['开心', '平静', '焦虑', '悲伤']) for _ in
                     range(len(st.session_state.historical_data['dates']))],
        'HRV指数': [np.random.uniform(30, 100) for _ in range(len(st.session_state.historical_data['dates']))],
        '语音情绪': [np.random.choice(['平静', '焦虑', '紧张', '放松']) for _ in
                     range(len(st.session_state.historical_data['dates']))]
    })

    st.dataframe(df, width='stretch')

    # 数据导出
    if st.button("📥 导出数据"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="下载CSV文件",
            data=csv,
            file_name=f"anxiety_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # 页脚
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">© 2026 青少年焦虑状态智能陪伴机器人 | 多模态融合分析系统</p>',
        unsafe_allow_html=True)