import uuid
from .translation import translate_field_name
# 一、主体钢筋材料
cage_steel_materials = [
    "Q235B钢筋(现浇构件钢筋)",
    "水平钢筋绑扎",
    "竖向钢筋绑扎",
    "拉筋绑扎",
    "预留水平钢筋绑扎"
]

# 二、连接材料
cage_connection_materials = [
    "直螺纹钢筋套筒(Φ16-Φ40)",
    "锥套锁紧套筒及配套材料",
    "Q345预埋铁件(钢筋锚固板)",
    "模块竖向钢筋锥套连接",
    "措施短柱预埋件安装及调整",
    "模块起吊、落位、短柱连接"
]

# 三、工装系统
cage_tool_materials = [
    "Q235B零星钢结构(盖板等工装)",
    "立柱(HW150*150)",
    "立柱(HW100*100)",
    "钢筋限位工装安装及调整",
    "L型钢筋",
    "\"J\"钢筋",
    "剪刀撑",
    "U型卡",
    "双U型卡",
    "短柱(HW150*150)",
    "预埋件安装"
]

# 四、施工辅助材料
cage_auxiliary_materials = [
    "定型围栏",
    "模板支设",
    "C25混凝土",
    "铁件",
    "电焊条",
    "单层彩钢板"
]

# 五、机械设备
cage_mechanical_equipment = [
    "螺栓套丝机(φ39)",
    "砂轮切割机(500)",
    "自升式塔式起重机(1500KNm)",
    "重型塔吊",
    "汽车吊(80t)",
    "汽车吊(25t)",
    "吊装索具"
]

# 主体钢筋材料
steel_materials = [
    "Q235B钢筋(现浇构件钢筋)",
    "水平钢筋、竖向钢筋",
    "拉筋",
    "预留水平钢筋"
]

# 连接材料
connection_materials = [
    "单侧钢覆面安装加固+埋件焊接材料+镶入件焊接材料",
    "通常设备室钢覆面及预留钢覆面组队焊接"
]

# 钢覆面材料
steel_cover_materials = [
    "单侧钢覆面埋件临时安装",
    "另一侧钢覆面埋件临时安装",
    "钢覆面后台制作"
]

# 埋件材料
embedding_materials = [
    "不锈钢埋件后台制作",
    "碳钢埋件后台制作",
    "套管、镶入件后台制作" 
]

# 机械设备
mechanical_equipment = [
    "螺栓套丝机(φ39)",
    "砂轮切割机(500)",
    "自升式塔式起重机(1500KNm)",
    "重型塔吊"
]
#吊装锁具
lifting_lock = [
    '压制钢丝绳（A68 6*36 7500cm）',
    "压制钢丝绳（A52 6*36 7407cm）",
    "压制钢丝绳（A36 6*36 1500cm）",
    "压制钢丝绳（A68 6*36 9447cM）",
    "压制钢丝绳（φ52 6*36 8678cm）",
    '花篮螺栓-JW3128', 
    '花篮螺栓-JW3319',
    '花篮螺栓-JW3409',
    '卸扣-17T', 
    '卸扣-30T',
    '卸扣-55T',
    ]

prefab_materials = [
    "预制板模板支设",
    "预制板钢筋制作安装",
    "预制板混凝土浇筑",
    "模块化角钢制作安装",
    "模块起重吊装设备",
    "模块运输设备",
]

# 二次浇筑材料
secondary_casting_materials = [
    "二浇区板模板支设",
    "二浇区板钢筋制作安装",
    "二浇区混凝土浇筑", 
    "钢丝网模板",
    "施工缝凿毛材料"
]

# 支撑系统
support_materials = [
    "满堂脚手架搭设",
    "外双排脚手架搭设",
    "模块落位钢筋接头连接"
]

# 埋件及连接材料
place_materials = [
    "预制场地摊销费"
]

# 预制场地设施
Prefabricated_site_facilities = [
    "场地平整",
    "模块支设",
    "C25混凝土浇筑(15cm+5cm)",
    "模板拆除",
    "预制场地维护",
]

# 一、主体钢筋材料
rebar_materials = [
    "钢筋制作安装材料",
    "预制板顶分布钢筋",
    "预制板吊环钢筋",
    "底部加大钢筋"
]

# 二、混凝土材料
concrete_materials = [
    "预制构件混凝土"
]

# 三、模板及支撑材料
formwork_materials = [
    "模板支拆",
    "满堂支撑架体搭设拆除"
]

# 四、埋件及连接材料
tunnel_embedding_materials = [
    "支撑角钢埋件",
    "墙体埋件",
    "顶板埋件",
    "特殊机械套筒",
]

c404_tunnel_embedding_materials = [
    "角钢埋件(L100*100)",
    "支撑角钢埋件(L100*10，15kg/m)",
    "墙体埋件(T2型，34kg/m)",
    "普通套筒",
]

# 五、防水及接缝材料
tunnel_waterproof_materials = [
    "遇水膨胀止水条",
    "三元乙丙橡胶垫"
]

# 六、施工处理材料
construction_materials = [
    "叠合板凿毛材料"
]

# 七、机械设备
tunnel_equipment = [
    "25t汽车吊",
    "平板车",
    "随车吊",
    "80吨汽车吊",
    "预制构件运输设备"
]

# 八、预制场地设施
tunnel_site_facilities = [
    "场地平整材料",
    "场地硬化材料",
    "办公区建设材料",
    "围墙建设材料",
    "200T龙门吊",
    "龙门吊轨道",
    "预制加工场摊销"
]

others = [
    "间接施工费（直接施工）",
    "间接施工费（模块化施工）",
]

# 钢衬里施工模式配置
# 一、基础结构类
steel_lining_foundation = [
    "网架存放场地",
    "制作胎具", 
    "钢支墩、埋件混凝土剔凿",
    "钢支墩、埋件混凝土回填",
    "钢支墩、埋件安装",
    "钢支墩、埋件使用折旧"
]

# 二、结构构件类
steel_lining_structure = [
    "扶壁柱安装",
    "扶壁柱拆除", 
    "扶壁柱构件使用折旧费",
    "走道板及操作平台制作",
    "走道板及操作平台搭设",
    "走道板及操作平台拆除"
]

# 三、辅助设施类
steel_lining_auxiliary = [
    "脚手架搭拆",
    "环向加固工装",
    "模块就位措施", 
    "角钢增设"
]

# 四、机械设备类
steel_lining_equipment = [
    "人工保养吊索具",
    "吊索具使用机械倒运",
    "模板试吊、吊装投入的人工"
]

# 五、钢网架系统
steel_lining_frame = [
    "钢网架制作",
    "钢网架安装",
    "钢网架拆除",
    "模块吊耳制、安、拆"
]

# 六、试验检测
steel_lining_testing = [
    "荷载试验人工配合"
]

# 钢衬里所有材料分类
steel_lining_all_categories = {
    "基础结构": steel_lining_foundation,
    "结构构件": steel_lining_structure, 
    "辅助设施": steel_lining_auxiliary,
    "机械设备": steel_lining_equipment,
    "钢网架系统": steel_lining_frame,
    "试验检测": steel_lining_testing
}



project_types = ['桥梁工程', '隧道工程', '路基工程', '涵洞工程', '建筑工程']

param_types = ['钢筋材料', '混凝土材料', '模板材料', '连接材料', '其他材料']

units = ['m', 'm²', 'm³', 'mm', 'cm', 'kg', 't', '个', '件']

DEFAULT_PARAM_ID = str(uuid.uuid4())