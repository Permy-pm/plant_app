import streamlit as st
# ================= 页面美化 CSS =================
custom_css = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stAppViewContainer"] {
    background-color: #F4F9F4;
}

.plant-card {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 5px solid #2E8B57;
    margin-top: 20px;
}
</style>
"""
# ================================================

from aip import AipImageClassify
from openai import OpenAI

BAIDU_APP_ID = st.secrets["BAIDU_APP_ID"]      
BAIDU_API_KEY = st.secrets["BAIDU_API_KEY"] 
BAIDU_SECRET_KEY = st.secrets["BAIDU_SECRET_KEY"]
QWEN_API_KEY = st.secrets["QWEN_API_KEY"]

st.set_page_config(page_title="校园植物多样性随手拍", page_icon="🌿", layout="centered")

# ================= 前端 CSS 美化 =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    header[data-testid="stHeader"] { background-color: #2E4A35 !important; }
    header[data-testid="stHeader"] * { color: #FFFFFF !important; }
    .stApp { background-color: #FDFBF7 !important; }
    h1 { color: #2E4A35 !important; font-family: 'Inter', 'Microsoft YaHei', sans-serif !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    p, div, span { color: #3A4A3F !important; font-family: 'Inter', 'Microsoft YaHei', sans-serif !important; }
    .stButton > button { background-color: #F2C94C !important; color: #1A2E1F !important; border-radius: 12px !important; border: none !important; font-weight: 600 !important; padding: 10px 24px !important; transition: all 0.3s ease; }
    .stButton > button:hover { background-color: #E2B93B !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(242, 201, 76, 0.4); }
    [data-testid="stFileUploader"] > section { border: 2px dashed #2E4A35 !important; border-radius: 12px !important; background-color: #FFFFFF !important; }
    [data-testid="stFileUploader"] section button { background-color: transparent !important; color: #2E4A35 !important; border: 1px solid #2E4A35 !important; border-radius: 8px !important; font-size: 14px !important; padding: 4px 12px !important; }
    [data-testid="stFileUploader"] section button:hover { background-color: #E8F0EA !important; }
    [data-testid="stFileUploader"] section button span { display: none !important; }
    [data-testid="stFileUploader"] section button::after { content: "选择文件" !important; font-weight: 600 !important; color: #2E4A35 !important; }
    .stAlert { border-radius: 10px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= 1. 后端密钥配置区 =================
# 百度 AI 配置
baidu_client = AipImageClassify(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

# 千问大模型配置
qwen_client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ================= 2. 本地兜底字典（API失败时使用） =================
LOCAL_PLANT_DICT = {
    "桂花": "桂花是中国木犀科木犀属众多植物的习称，是中国传统十大名花之一，集绿化、美化、香化于一体的观赏与实用兼备的优良园林树种。扬州城市绿地的基调树种之一。",
    "琼花": "琼花是忍冬科荚蒾属落叶或半常绿灌木，又称扬州琼花、聚八仙。4-5月间开花，花大如盘，洁白如玉。周边八朵为萼片发育成的不孕花，中间为两性小花。扬州市花。",
    "芍药": "芍药是毛茛科芍药属的多年生草本植物，花朵很大，和牡丹花相似，观赏价值极高。扬州栽培芍药历史悠久，名扬天下。扬州市花。",
    "银杏": "银杏是银杏科银杏属落叶乔木，秋季叶片变为金黄色，是优良的观赏树种。扬州市树。",
    "垂柳": "垂柳是杨柳科柳属落叶乔木，枝条细长下垂，姿态优美，常种植于水边。扬州市树。",
    "香樟": "香樟是樟科樟属常绿大乔木，树冠广展，枝叶茂密，是扬州城市绿地的骨干树种和基调树种之一。",
    "女贞": "女贞是木犀科女贞属常绿灌木或乔木，是扬州城市绿地的基调树种之一。夏季开白色小花，果实为紫黑色。",
    "龙柏": "龙柏是柏科圆柏属常绿小乔木，树冠圆柱形，侧枝常有螺旋状扭曲。喜光，是扬州园林绿化中常用的灌木。",
    "碧桃": "碧桃是蔷薇科李属落叶小乔木，是桃的观赏变种。春季开花，花色丰富，是扬州城市绿地中的基调树种之一。",
    "石蒜": "石蒜是石蒜科石蒜属多年生草本植物，又名彼岸花。秋季开花，花叶永不相见，花色多为红色。全株有毒。",
    "美人蕉": "美人蕉是美人蕉科美人蕉属多年生草本植物，植株高大，叶片宽大。花朵大而艳丽，常成簇开放，花期长。",
    "红枫": "红枫是槭树科槭属落叶小乔木，是一种美丽的观叶树种。叶形优美，红色鲜艳持久，是扬州秋季重要的观叶植物。",
    "蜡梅": "蜡梅是蜡梅科蜡梅属落叶灌木，冬季开花，花香浓郁。花着生于第二年生枝条叶腋内，先花后叶。",
    "山茶": "山茶是山茶科山茶属灌木或小乔木，叶革质。花顶生，多为红色，花期在冬末春初，花大艳丽，四季长青。",
    "扶芳藤": "扶芳藤是卫矛科卫矛属常绿藤本植物，是扬州常见的攀缘植物。冬季蒴果爆裂后，露出红色的种子，红白相间。",
    "红果冬青": "红果冬青是冬青科冬青属半常绿小乔木，果实成熟后为红色，观赏期从11月可持续到12月。",
    "菊花": "菊花是菊科菊属多年生宿根草本植物，中国十大名花之一。品种繁多，是秋季扬州公园里重要的观赏花卉。",
    "万寿菊": "万寿菊是菊科万寿菊属一年生草本植物，花色鲜艳，多为黄色或橙色，花期长，是扬州常见的花坛、花境材料。",
    "绣球": "绣球是绣球花科绣球属灌木，花型丰满，大而美丽，花色能红能蓝，是扬州园林和庭院中常见的观赏植物。",
    "红花酢浆草": "红花酢浆草是酢浆草科酢浆草属多年生草本植物，开红色或粉色小花，常作为地被植物，在扬州公园的草坪和林下常见。"
}

# ================= 3. 后端核心函数区 =================
def get_plant_name(image_bytes):
    """调用百度API识别植物名称"""
    try:
        result = baidu_client.plantDetect(image_bytes)
        if result.get('result') and len(result['result']) > 0:
            return result['result'][0]['name']
        return "未识别"
    except Exception as e:
        return f"识别失败: {e}"

def get_plant_info(plant_name):
    """调用千问大模型生成科普文案，失败时使用本地字典"""
    # 先尝试调用大模型
    try:
        prompt = f"""
        你是一名擅长科学知识传播的生物学专家。请为植物：{plant_name}，写一段科普介绍。
        要求：采用严谨但通俗的语言，包含物种分类、形态特征、生态价值。
        字数控制在150-200字左右。语气要生动有趣，像科普博主一样。
        """
        response = qwen_client.chat.completions.create(
            model="qwen-turbo", 
            messages=[
                {"role": "system", "content": "你是一个专业的生物科普专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        # API调用失败，启用本地兜底
        if plant_name in LOCAL_PLANT_DICT:
            return f"📚 本地科普档案：\n\n{LOCAL_PLANT_DICT[plant_name]}\n\n（注：当前网络异常，已为您展示本地存档的科普信息）"
        else:
            return f"😢 抱歉，网络似乎出现了问题，未能获取到「{plant_name}」的科普信息。请检查网络后重试。"

# ================= 4. 前端界面区 =================
st.markdown(custom_css, unsafe_allow_html=True)
st.title("🌿 校园植物多样性随手拍")
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
                    st.markdown(f"""
                    <div class="plant-card">
                        <h2 style="color: #2E8B57; margin-bottom: 10px;">🌿 识别结果：{plant_name}</h2>
                        <p style="color: #333333; line-height: 1.6; font-size: 16px;">{intro_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            else:
                st.error(f"😢 识别失败，错误信息：{plant_name}，请换一张清晰的照片试试。")