import streamlit as st
from aip import AipImageClassify
from openai import OpenAI

# 已经删除了 import os 和 from utils import get_base64_image

# 仅运行，上传时需改
BAIDU_APP_ID = st.secrets["BAIDU_APP_ID"]
BAIDU_API_KEY = st.secrets["BAIDU_API_KEY"]
BAIDU_SECRET_KEY = st.secrets["BAIDU_SECRET_KEY"]
QWEN_API_KEY = st.secrets["QWEN_API_KEY"]

st.set_page_config(page_title="校园生物多样性随手拍", page_icon="📸", layout="wide")

baidu_client = AipImageClassify(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)
qwen_client = OpenAI(api_key=QWEN_API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 只保留了 remote 链接，并将 github blob 改为了 cdn.jsdelivr.net 的加速链接
YANGDA_PLANTS = {
    "百日菊": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/bairiju.jpg",
        "desc": "菊科百日菊属一年生草本。花瓣艳丽，紫红色/玫红色，花芯黄褐，校园花坛花卉。别名步步登高，因为后开的花位置比先开的更高。",
        "video": "https://www.bilibili.com/video/BV1Nfn46gEKW/"           # 此处为随机网址须替代（后同）
    },
    "常春藤": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/changchunteng.jpg",
        "desc": "五加科常春藤属，常绿木质藤本。叶片典型三角心形、掌状裂，攀援生长，可做垂直绿化。",
        "video": "https://www.bilibili.com/video/BV1sfn46gELA/"
    },
    "葱莲": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/conglian.jpg",
        "desc": "石蒜科葱莲属，多年生球根草本。叶片细长像小葱，白色六瓣花，校园草坪非常常见。⚠️鳞茎有毒，不要误食。",
        "video": "https://www.bilibili.com/video/BV11fn46gEP7/"
    },
    "灰喜鹊": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/huixique.jpg",
        "desc": "灰喜鹊是鸦科鸟类，很聪明，成群活动。食性杂，吃昆虫、植物种子、果实，是益鸟。淡蓝色的长尾是它最明显的特征",
        "video": "https://www.bilibili.com/video/BV1Awnt6MELj/"
    },
    "水杉": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/shuishan.jpg",
        "desc": "杉科水杉属，国家一级保护植物，活化石。高大乔木，条形羽状叶片，扬大校园行道树，秋冬落叶。",
        "video": "https://www.bilibili.com/video/BV1Pfn46gEyS/"
    },
    "无刺枸骨": {
        "remote": "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/wucigougu.jpg",
        "desc": "冬青科冬青属，常绿灌木。革质亮绿叶，秋季结大量密集红色浆果；普通枸骨叶片带刺，这个变种无尖刺。",
        "video": "https://www.bilibili.com/video/BV1Pfn46gEji/"
    },
}

if "selected_plant" not in st.session_state:
    st.session_state.selected_plant = None

def get_plant_name(image_bytes):
    try:
        result = baidu_client.plantDetect(image_bytes)
        if result.get('result') and len(result['result']) > 0:
            return result['result'][0]['name']
        return "未识别"
    except Exception as e:
        return f"识别失败: {e}"

def get_plant_info(plant_name):
    try:
        prompt = f"你是一名擅长科学知识传播的生物学专家。请为植物：{plant_name}，写一段科普介绍。要求：采用严谨但通俗的语言，包含物种分类、形态特征、生态价值。字数控制在150-200字左右。语气要生动有趣，像科普博主一样。"
        response = qwen_client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "system", "content": "你是一个专业的生物科普专家。"}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        if plant_name in YANGDA_PLANTS:
            return f"📚 本地科普档案：\n\n{YANGDA_PLANTS[plant_name]['desc']}\n\n（注：当前网络异常，已为您展示本地存档的科普信息）"
        else:
            return f"😢 抱歉，未能获取到「{plant_name}」的科普信息。"

# 1. 背景图直接用写好的 jsDelivr 加速链接
bg_css_src = "https://cdn.jsdelivr.net/gh/Permy-pm/plant_app@main/file.webp"

# 2. 注入 CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

.stApp {{
    background-image: url('{bg_css_src}');  
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(253, 251, 247, 0.88);
    z-index: -2;
}}
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

h1 {{ color: #2E4A35 !important; font-family: 'Inter', 'Microsoft YaHei', sans-serif !important; font-weight: 700 !important; }}
p, div, span {{ color: #3A4A3F !important; font-family: 'Inter', 'Microsoft YaHei', sans-serif !important; }}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
.stTabs [data-baseweb="tab"] {{
    background-color: #E8F0EA; border-radius: 8px 8px 0 0; padding: 8px 20px;
    color: #2E4A35; font-weight: 600;
}}
.stTabs [aria-selected="true"] {{ background-color: #F2C94C !important; color: #1A2E1F !important; }}

.stButton > button {{
    background-color: #F2C94C !important; color: #1A2E1F !important;
    border-radius: 12px !important; border: none !important;
    font-weight: 600 !important; padding: 8px 16px !important;
    transition: all 0.3s ease;
}}
.stButton > button:hover {{ background-color: #E2B93B !important; transform: translateY(-2px); }}

[data-testid="stFileUploader"] > section {{
    border: 2px dashed #2E4A35 !important; border-radius: 12px !important;
    background-color: #FFFFFF !important;
}}
[data-testid="stFileUploader"] section button {{
    background-color: transparent !important; color: #2E4A35 !important;
    border: 1px solid #2E4A35 !important; border-radius: 8px !important;
    font-size: 14px !important; padding: 4px 12px !important;
}}
[data-testid="stFileUploader"] section button span {{ display: none !important; }}
[data-testid="stFileUploader"] section button::after {{ content: "选择文件" !important; font-weight: 600 !important; color: #2E4A35 !important; }}


.bubble-container {{
    position: relative;
    height: 420px;
    width: 100%;
    margin-bottom: 20px;
    overflow: hidden;
}}
.bubble {{
    position: absolute;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 50%; padding: 0;
    box-shadow: 0 8px 32px rgba(46, 74, 53, 0.2);
    backdrop-filter: blur(8px);
    border: 2px solid rgba(255, 255, 255, 0.9);
    overflow: hidden; display: flex; justify-content: center; align-items: center;
    transition: transform 0.3s ease; cursor: pointer;
}}
.bubble:hover {{ transform: scale(1.5); z-index: 10; }}
.bubble img {{ width: 100%; height: 100%; object-fit: cover; }}

.bubble-1 {{ width: 200px; height: 200px; top: 5%; left: 2%; animation: floatBubble 6s ease-in-out infinite; }}
.bubble-2 {{ width: 160px; height: 160px; top: 2%; left: 38%; animation: floatBubble 4s ease-in-out infinite 1s; }}
.bubble-3 {{ width: 220px; height: 220px; top: 5%; right: 3%; animation: floatBubble 7s ease-in-out infinite 0.5s; }}
.bubble-4 {{ width: 170px; height: 170px; bottom: 25%; left: 8%; animation: floatBubble 5s ease-in-out infinite 2s; }}
.bubble-5 {{ width: 190px; height: 190px; bottom: 8%; right: 10%; animation: floatBubble 5.5s ease-in-out infinite 1.5s; }}
.bubble-6 {{ width: 150px; height: 150px; bottom: 40%; left: 45%; animation: floatBubble 6.5s ease-in-out infinite 0.8s; }}
@keyframes floatBubble {{
    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-20px) rotate(3deg); }}
}}

.plant-card {{
    background-color: #FFFFFF; border-radius: 15px; padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #2E8B57; margin-top: 20px;
}}
.stAlert {{ border-radius: 10px !important; }}
</style>
""", unsafe_allow_html=True)

st.title("校园生物多样性随手拍")

tab1, tab2 = st.tabs(["📸 AI 识别", "🌳 扬大特色植物"])
# 第一页
with tab1:
    st.markdown("### 📸 上传照片，AI 识别校园植物")
    st.write("上传一张校园里的花草树木照片，AI 将为你识别植物并生成科普文字。")

    uploaded_file = st.file_uploader("请上传一张植物照片", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        st.image(image_bytes, caption='你上传的照片', use_container_width=True)
        if st.button('开始识别植物'):
            with st.spinner('AI 正在努力识别中...'):
                plant_name = get_plant_name(image_bytes)
                if plant_name not in ["未识别"] and "识别失败" not in plant_name:
                    st.success(f"🎉 识别成功！这株植物是：**{plant_name}**")
                    with st.spinner('📝 正在调用大模型生成专属科普...'):
                        intro_text = get_plant_info(plant_name)
                        baike_url = f"https://baike.baidu.com/item/{plant_name}"
                        st.markdown(f"""
                        <div class="plant-card">
                            <h2 style="color: #2E8B57; margin-bottom: 10px;">🌿 识别结果：{plant_name}</h2>
                            <p style="color: #333333; line-height: 1.6; font-size: 16px;">{intro_text}</p>
                            <p style="margin-top: 15px;"><a href="{baike_url}" target="_blank" style="color: #2E8B57; font-weight: 600; text-decoration: none;">🔗 点击这里查看「{plant_name}」的百度百科详细介绍</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"😢 识别失败，错误信息：{plant_name}，请换一张清晰的照片试试。")

# 第二页
with tab2:
    st.markdown("### 🌳 扬州大学校园特色植物图鉴")
    st.write("点击泡泡，查看植物介绍和视频解说。")

    bubble_html = '<div class="bubble-container">'
    for index, (name, info) in enumerate(YANGDA_PLANTS.items()):
        position_class = f"bubble-{ (index % 6) + 1 }"
        # 直接读取 remote 链接
        image_src = info["remote"]
        bubble_html += f'<div class="bubble {position_class}"><img src="{image_src}" /></div>'
    bubble_html += '</div>'
    st.markdown(bubble_html, unsafe_allow_html=True)

    st.markdown("#### 🌿 点击下方按钮查看植物详情")
    cols = st.columns(len(YANGDA_PLANTS))
    for i, plant_name in enumerate(YANGDA_PLANTS.keys()):
        with cols[i]:
            if st.button(f"🌿 {plant_name}", key=f"btn_{plant_name}", use_container_width=True):
                st.session_state.selected_plant = plant_name

    if st.session_state.selected_plant:
        p = st.session_state.selected_plant
        info = YANGDA_PLANTS[p]
        if p == "灰喜鹊":
            baike_url = "https://baike.baidu.com/item/灰喜鹊/734473"
        else:
            baike_url = f"https://baike.baidu.com/item/{p}"
        st.markdown(f"""
        <div class="plant-card">
            <h2 style="color: #2E8B57; margin-bottom: 10px;">🌿 植物详情：{p}</h2>
            <p style="color: #333333; line-height: 1.6; font-size: 16px;">{info['desc']}</p>
            <p style="margin-top: 15px;">
                <a href="{baike_url}" target="_blank" style="color: #2E8B57; font-weight: 600; text-decoration: none;">🔗 百度百科</a>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <a href="{info['video']}" target="_blank" rel="noreferrer" referrerpolicy="no-referrer" style="color: #2E8B57; font-weight: 600; text-decoration: none;">🎬 视频解说</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ 关闭介绍"):
            st.session_state.selected_plant = None
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎬 植物视频解说")
    st.write("点击下方卡片，观看对应植物的百科视频。")

    video_cols = st.columns(3, gap="large")
    for i, (name, info) in enumerate(YANGDA_PLANTS.items()):
        with video_cols[i % 3]:
            # 直接读取 remote 链接
            img_src = info["remote"]
            st.markdown(f"""
            <div style="
                background: #FFFFFF;
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 12px rgba(46, 74, 53, 0.08);
                text-align: center;
                height: 320px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            ">
                <img src="{img_src}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 10px;" />
                <h4 style="color: #2E4A35; margin: 10px 0 5px 0;">{name}</h4>
                <a href="{info['video']}" target="_blank" style="
                    color: #2E4A35;
                    font-weight: 600;
                    text-decoration: none;
                    background-color: #F2C94C;
                    padding: 6px 16px;
                    border-radius: 8px;
                    display: inline-block;
                ">🎬 观看视频</a>
            </div>
            """, unsafe_allow_html=True)