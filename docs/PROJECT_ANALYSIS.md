# 项目分析文档 - MapleStoryAutoLevelUp

> 📅 分析日期: 2026-06-16
> 🔄 最后更新: 2026-06-16
> 🎯 原始目标: Artale 私服自动练级工具
> 🚧 改造目标: Talery 私服适配

---

## 一、项目概览

| 属性 | 值 |
|------|-----|
| 项目名称 | MapleStoryAutoLevelUp |
| 原始适配 | Artale 私服 (TW/NA) |
| 技术方案 | 纯计算机视觉 (CV) + 键盘模拟，不访问游戏内存 |
| 技术栈 | Python 3.12 + OpenCV 4.11 + PySide6 + NumPy + windows-capture |
| 核心引擎 | `src/engine/MapleStoryAutoLevelUp.py` (~1925行) |
| 运行入口 | `python -m src.main` (UI模式) / `python -m src.engine.MapleStoryAutoLevelUp` (无UI) |
| 打包方式 | PyInstaller → .exe |
| 许可证 | MIT |
| 上游仓库 | https://github.com/KenYu910645/MapleStoryAutoLevelUp |

---

## 二、完整项目结构树

```
e:\rayjyliuMapNew\
├── .gitignore
├── build.bat                    # 打包脚本
├── LICENSE                      # MIT
├── Makefile                     # 构建命令
├── README.md / README.zh.md     # 中英文文档
├── requirements.txt             # Python依赖
│
├── config/                      # ═══════ 配置层 ═══════
│   ├── __init__.py
│   ├── config_default.yaml      # 🔑 主配置(335行) - 所有参数的默认值
│   ├── config_data.yaml         # 📊 数据映射(79行) - 地图-怪物映射 + 中英翻译
│   ├── config_cleric.yaml       # 牧师职业预设配置
│   ├── config_macOS.yaml        # macOS特定配置
│   └── legacy/                  # 旧版配置文件
│
├── src/                         # ═══════ 源码层 ═══════
│   ├── main.py                  # 🚪 入口: PySide6 App → AutoBotController → MainWindow
│   │
│   ├── engine/                  # ⚙️  核心引擎
│   │   ├── __init__.py
│   │   ├── MapleStoryAutoLevelUp.py  # 🔥 核心引擎(1925行): 配置加载/玩家定位/怪物检测/路线导航/命令输出
│   │   ├── FiniteStateMachine.py     # 🔄 有限状态机(54行): 管理6状态注册/转换(最小间隔1s)/帧循环
│   │   ├── HealthMonitor.py          # ❤️  HP/MP监控(243行): 独立线程检测血条→自动喝药→无药回城
│   │   ├── RuneSolver.py            # ✨ 符文解谜: 检测符文→识别箭头→按键解谜
│   │   └── Profiler.py              # 📊 性能分析: FPS低于5时打印各步骤耗时
│   │
│   ├── states/                  # 🔀 状态机各状态
│   │   ├── base_state.py        # 状态基类(16行): on_enter/on_exit/check_transitions/on_frame 接口
│   │   ├── hunting.py           # 🏹 狩猎状态(40行): 读路线→检怪物→攻击→查卡住→查符文消息
│   │   ├── finding_rune.py      # 🔍 找符文状态: 小地图搜索符文→接近
│   │   ├── near_rune.py         # 🎯 靠近符文状态: 按↑触发符文
│   │   ├── solving_rune.py      # 🧩 解符文状态: 识别4箭头→按正确顺序按键
│   │   ├── auxiliary.py         # 🤖 辅助模式: 不攻击不检怪，只按路线移动
│   │   └── patrol.py            # 🚶 巡逻模式: 屏幕边界间来回走动+定时攻击
│   │
│   ├── input/                   # ⌨️ 输入层
│   │   ├── __init__.py
│   │   ├── GameWindowCapturor.py     # 📸 窗口截取(Win): windows-capture库, 调整1296×759
│   │   ├── GameWindowCapturorForMac.py # 📸 窗口截取(Mac)
│   │   ├── KeyBoardController.py     # ⌨️ 键盘控制器: 独立线程→解析指令→模拟按键
│   │   └── KeyBoardListener.py       # 👂 全局键盘监听: F1暂停/F2截图/F3录制/F12终止
│   │
│   ├── ui/                     # 🖼️ UI层
│   │   ├── __init__.py
│   │   ├── ui.py               # 🖥️ 主窗口(1123行): 主Tab+高级设置+调试窗口+路线图
│   │   └── AutoBotController.py # 🔗 桥梁(138行): UI-引擎连接/快捷键注册/信号转发
│   │
│   ├── utils/                  # 🛠️ 工具层
│   │   ├── __init__.py
│   │   ├── common.py           # 🔧 核心工具(847行): 模板匹配/HSV转换/截图/配置加载/小地图定位
│   │   ├── global_var.py       # 🌐 全局变量(3行): WINDOW_WORKING_SIZE = (1296, 700)
│   │   ├── logger.py           # 📝 日志
│   │   └── ui.py               # 🎨 UI工具: 输入验证/高级设置面板/日志格式化
│   │
│   └── legacy/                 # ⚠️ 旧版引擎(已废弃)
│       └── mapleStoryAutoLevelUp_legacy.py
│
├── tools/                      # ═══════ 辅助工具 ═══════
│   ├── routeRecorder.py        # 🎥 路线录制器(573行): 监听键盘→RGB标记动作→存路线/地图
│   ├── mob_maker.py            # 👾 怪物图集下载器(133行): 从maplestory.io API下载PNG
│   ├── AutoDiceRoller.py       # 🎲 自动掷骰子: 创建角色时自动掷出目标属性
│   ├── email_test.py           # 📧 邮件测试
│   ├── getPixeColorOnImg.py    # 🎨 像素颜色提取
│   ├── image_masking_experiment.py # 🧪 图像蒙版实验
│   └── f_string_format_check.py    # ✅ f-string格式检查
│
├── minimaps/                   # ═══════ 小地图资源 ═══════
│   ├── README.bmp
│   ├── <map_name>/             # 每个地图一个子目录
│   │   ├── map.png             # 🗺️ 完整小地图(用于全局定位的模板匹配基准)
│   │   ├── route1.png          # 🧭 路线图1(RGB颜色编码: 红=左/蓝=右/橙=左跳/绿=停/黄=目标...)
│   │   ├── route2.png          # 🧭 路线图2(多路线可轮流切换)
│   │   └── route_rest.png      # 🧭 休息路线(跳转到此路线时回城/休息)
│   ├── ...共22个地图目录
│
├── monster/                    # ═══════ 怪物图集资源 ═══════
│   ├── <mob_name>/             # 每个怪物一个子目录
│   │   ├── <mob_name>_1.png    # 怪物动画帧(含原始+翻转版本, 绑定绿色背景mask)
│   │   ├── <mob_name>_2.png
│   │   └── ...
│   ├── ...共28种怪物
│
├── misc/                       # ═══════ 杂项UI模板 ═══════
│   ├── login_button_cn.png     # 登录按钮(中文)
│   ├── login_button_eng.png    # 登录按钮(英文)
│   ├── party_button_create_enable_cn.png   # 创建队伍按钮-可用(中文)
│   ├── party_button_create_disable_cn.png  # 创建队伍按钮-不可用(中文)
│   ├── party_button_create_enable_eng.png  # 创建队伍按钮-可用(英文)
│   └── party_button_create_disable_eng.png # 创建队伍按钮-不可用(英文)
│
├── rune/                       # ═══════ 符文系统资源 ═══════
│   ├── rune.png                # 符文基础图标
│   ├── rune_1.png ~ rune_3.png # 符文图案(1-3号)
│   ├── rune_2_cn.png / rune_2_eng.png  # 符文2中英文
│   ├── rune_enable_cn.png / rune_enable_eng.png  # 符文启用消息(中/英)
│   ├── rune_warning_cn.png / rune_warning_eng.png # 符文警告消息(中/英)
│   ├── arrow_up_1~3.png        # 上箭头(3种高亮状态)
│   ├── arrow_down_1~3.png      # 下箭头
│   ├── arrow_left_1~3.png      # 左箭头
│   └── arrow_right_1~3.png     # 右箭头
│
├── numbers/                    # ═══════ 数字资源 ═══════
│   ├── 4.png ~ 13.png          # 数字4-13模板(用于等级/属性识别)
│
├── maps/                       # ═══════ 旧版全尺寸地图(已废弃) ═══════
├── media/                      # ═══════ 文档媒体 ═══════
└── screenshot/                 # 截图输出
```

---

## 三、核心架构详解

### 3.1 系统架构图

```
                         ┌─────────────────────┐
                         │     main.py          │
                         │  (PySide6 QApp)      │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
     ┌────────▼────────┐  ┌────────▼────────┐  ┌─────────▼─────────┐
     │  MainWindow     │  │AutoBotController│  │  KeyBoardListener │
     │  (ui.py,1123行)  │◄─┤(138行, 桥梁层)  │──┤  (F1~F12 快捷键)  │
     │  · 主Tab面板     │  │· 管理启停       │  └───────────────────┘
     │  · 高级设置面板  │  │· 信号转发       │
     │  · 调试可视化    │  │· 配置读写       │
     │  · 路线图可视化  │  └───────┬─────────┘
     └─────────────────┘          │
                                  │ signals
                         ┌────────▼───────────────┐
                         │  MapleStoryAutoBot     │
                         │  (核心引擎, ~1925行)     │
                         │                        │
                         │  核心能力:              │
                         │  · 配置加载+验证        │
                         │  · 窗口截图管理         │
                         │  · 玩家定位(红条/名牌)  │
                         │  · 小地图全局定位       │
                         │  · 路线导航(RGB编码)    │
                         │  · 怪物检测(4种模式)    │
                         │  · 命令生成与输出       │
                         └──┬──────────┬──────────┘
                            │          │
        ┌───────────────────┤          ├───────────────────────┐
        │                   │          │                       │
  ┌─────▼─────┐   ┌─────────▼──┐  ┌───▼──────────┐  ┌─────────▼──────┐
  │ FSM       │   │HealthMonitor│  │GameWindow    │  │KeyboardController
  │ 有限状态机 │   │(HP/MP监控)  │  │Capturor      │  │(键盘模拟)      │
  │           │   │             │  │(窗口截图)     │  │               │
  │ 6个状态:  │   │· 血条百分比  │  │              │  │· 独立线程      │
  │ hunting   │   │· 自动喝药   │  │· windows-    │  │· 命令队列      │
  │find_rune  │   │· 无药回城   │  │  capture库   │  │· 按键防抖      │
  │near_rune  │   │· 强制治疗   │  │· FPS可控     │  │               │
  │solve_rune │   │             │  │              │  │               │
  │ aux       │   └─────────────┘  └──────────────┘  └───────────────┘
  │ patrol    │
  └─────┬─────┘
        │
  ┌─────▼──────────────────────────────────────────┐
  │  RuneSolver (符文解谜器)                         │
  │  · 符文消息检测 (rune_enable / rune_warning)     │
  │  · 符文位置检测                                   │
  │  · 箭头方向模板匹配                               │
  │  · 按键序列输出                                   │
  └────────────────────────────────────────────────┘
```

### 3.2 状态机转换图

```
                    ┌──────────────────────────────────────┐
                    │           init (根据mode选择)          │
                    └──┬───────────┬───────────┬───────────┘
                       │           │           │
              ┌────────▼──┐ ┌──────▼─────┐ ┌──▼──────────┐
              │  hunting  │ │    aux     │ │   patrol    │
              │ (正常模式) │ │ (辅助模式)  │ │ (巡逻模式)   │
              └──┬───┬────┘ └────────────┘ └─────────────┘
                 │   │
     检测到符文消息│   │符文解谜完成
                 │   │
    ┌────────────▼┐  │
    │finding_rune │  │
    │ (搜索符文)   │  │
    └──┬────┬─────┘  │
       │    │         │
  检测到│    │超时回    │
  附近符│    │hunting  │
       │    │         │
  ┌────▼────▼──┐     │
  │ near_rune  │     │
  │ (靠近符文)  │─────┘
  └──┬────┬────┘ 超时回finding_rune
     │    │
 触发│    │
 符文│    │
     │    │
┌────▼────▼──┐
│solving_rune│
│(解谜箭头)   │
└─────┬──────┘
      │ 解谜完成
      └──→ hunting
```

### 3.3 主循环流程 (每帧执行)

```
┌─────────────────────────────────────────────────────┐
│  MapleStoryAutoBot.loop()  主循环                    │
│  FPS: ~10 (由 system.fps_limit_main 控制)            │
├─────────────────────────────────────────────────────┤
│  1. 获取截图帧 (从 GameWindowCapturor 消费)           │
│  2. 更新玩家位置                                     │
│     ├── 优先: get_player_location_by_party_red_bar() │
│     │         HSV提取红色→轮廓→最大面积=血条          │
│     └── 备选: get_player_location_by_nametag()       │
│              模板匹配→垂直分割→最佳匹配                │
│  3. 更新小地图位置                                   │
│     ├── 截取小地图区域                                │
│     ├── 在整个map.png中模板匹配定位                   │
│     └── 检测黄色玩家点→换算全局坐标                    │
│  4. 检测其他玩家                                     │
│     └── 如有其他玩家→根据channel_change模式决定换线   │
│  5. FSM.do_state_stuff() 执行当前状态的on_frame()     │
│     ├── hunting:                                     │
│     │   ├── get_nearest_color_code() 读取路线指令     │
│     │   ├── check_reach_goal() 检查是否到达路线终点   │
│     │   ├── get_nearest_monster() 检测最近怪物        │
│     │   └── is_player_stuck() 卡住检测→随机动作       │
│     ├── finding_rune: 搜索符文                        │
│     ├── near_rune: 靠近+触发符文                      │
│     └── solving_rune: 识别箭头+按键                   │
│  6. FSM.check_transitions() 检查状态转换             │
│  7. kb.set_command() 输出最终控制指令到键盘控制器      │
│  8. 更新调试可视化窗口                                │
│  9. Profiler记录耗时                                 │
│ 10. FPS控制 sleep                                    │
└─────────────────────────────────────────────────────┘
```

### 3.4 玩家定位原理

```
方案A: 组队红条检测 (首选, nametag.enable=False时启用)

  游戏窗口 ──→ 截取相机区域(img_camera)
       │
       ├──→ HSV颜色空间转换
       ├──→ cv2.inRange 提取红色区域
       │    lower_red = [0, 60, 60]   (HSV, 深红)
       │    upper_red = [0, 100, 100] (HSV, 亮红)
       ├──→ cv2.findContours 找轮廓
       ├──→ 筛选条件: 5≤h≤7, 1≤w≤50, area≥10, fill_rate≥0.7
       ├──→ 最大面积轮廓 = 组队红条
       └──→ player_loc = (红条x + offset_x, 红条y + offset_y)
            offset默认 = [20, 66]

方案B: 名字标签检测 (备选, nametag.enable=True时启用)

  游戏窗口 ──→ 截取相机区域
       │
       ├──→ 垂直分割名字标签为多个片段(对抗遮挡)
       ├──→ 模板匹配(find_pattern_sqdiff)
       ├──→ 各片段独立匹配
       ├──→ 选取最佳匹配组合
       └──→ player_loc = nametag_loc + offset
```

### 3.5 路线导航原理

```
路线图(route*.png)使用RGB颜色编码:

颜色          RGB值          指令
────────────────────────────────────
🔴 红色       255,0,0        left none none        (向左走)
🔵 蓝色       0,0,255        right none none       (向右走)
🟠 橙色       255,127,0      left none jump        (向左走+跳)
🟦 青色       0,255,255      right none jump       (向右走+跳)
💚 酸橙绿    127,255,0      none down jump        (向下跳)
💜 品红       255,0,255      none none jump        (原地跳)
🟢 浅绿       0,255,127      stop stop stop        (停止)
🟨 黄色       255,255,0      none none goal        (到达目标)
🌸 粉色       255,0,127      none up teleport      (向上瞬移)
🟪 紫色       127,0,255      none down teleport    (向下瞬移)
🟩 深绿       0,127,0        left none teleport    (向左瞬移)
🟫 棕色       139,69,19      right none teleport   (向右瞬移)
⚪ 灰色       127,127,127    none up none          (攀爬)
🟡 浅黄       255,255,127    none down none        (下爬)

每帧在玩家周围 search_range=10 像素内搜索最近的颜色指令
```

### 3.6 怪物检测（4种模式对比）

| 模式 | 算法 | 计算量 | 准确度 | 适用场景 |
|------|------|--------|--------|---------|
| `contour_only` **(默认)** | 轮廓检测 + HP条颜色验证 | 中 | 高 | 通用推荐 |
| `color` | 颜色模板匹配 (BGR) | 高 | 最高 | 复杂背景 |
| `grayscale` | 灰度模板匹配 | 中 | 中 | 简单场景 |
| `template_free` | 基于角色尺寸推算 | 低 | 低 | 低配机器 |

---

## 四、配置文件详解

### 4.1 config_default.yaml 参数完整清单

```yaml
# 配置层级结构
config_default.yaml
├── bot                    # 🔁 机器人基本设置
│   ├── mode: "normal"     # 模式: normal/aux/patrol
│   ├── attack: "directional"  # 攻击类型: aoe_skill/directional
│   └── map: ""            # 地图名(需在config_data.yaml注册)
│
├── key                    # 🎮 按键映射
│   ├── aoe_skill: "q"     # AoE技能键
│   ├── directional_attack: "w"  # 定向攻击键
│   ├── teleport: "e"      # 瞬移键
│   ├── jump: "space"      # 跳跃键
│   ├── add_hp: "1"        # HP药水键
│   ├── add_mp: "2"        # MP药水键
│   ├── return_home: "home" # 回城卷轴键
│   └── party: "p"         # 队伍快捷键
│
├── buff_skill             # 💫 Buff技能
│   ├── keys: []           # Buff技能键列表
│   ├── cooldown: []       # 冷却时间列表
│   └── action_cooldown: 1 # Buff后延迟
│
├── directional_attack     # 🗡️ 定向攻击参数
│   ├── range_x: 350       # 水平范围(像素)
│   ├── range_y: 70        # 垂直范围(像素)
│   ├── cooldown: 0.9      # 攻击间隔(秒)
│   └── character_turn_delay: 0.02  # 转身延迟
│
├── aoe_skill              # 💥 AoE技能参数
│   ├── range_x: 400       # 水平范围
│   ├── range_y: 170       # 垂直范围
│   └── cooldown: 0.05     # 冷却
│
├── health_monitor         # ❤️ 健康监控
│   ├── enable: True       # 启用开关
│   ├── force_heal: False  # 强制治疗(停止攻击)
│   ├── add_hp_percent: 50 # HP阈值(百分比)
│   ├── add_mp_percent: 50 # MP阈值
│   ├── add_hp_cooldown: 0.5
│   ├── add_mp_cooldown: 0.5
│   ├── fps_limit: 20      # 监控线程FPS
│   ├── return_home_if_no_potion: False  # 无药回城
│   └── return_home_watch_dog_timeout: 3
│
├── teleport               # 🌀 瞬移
│   ├── is_use_teleport_to_walk: False  # 走路时瞬移
│   └── cooldown: 1
│
├── edge_teleport          # 🧙 边缘瞬移/跳跃
│   ├── enable: True
│   ├── trigger_box_width: 20
│   ├── trigger_box_height: 10
│   └── color_code: [255, 127, 127]  # 平台边缘RGB
│
├── party_red_bar          # ❤️ 组队红条检测 ⚠️ Talery需确认
│   ├── lower_red: [0, 60, 60]    # HSV深红
│   ├── upper_red: [0, 100, 100]  # HSV亮红
│   ├── offset: [20, 66]          # 红条到角色中心偏移
│   └── create_party_button_*_thres: 0.04  # 按钮匹配阈值
│
├── nametag                # 🏷️ 名字标签检测(已废弃)
│   └── enable: False
│
├── character              # 🧍 角色尺寸(仅template_free模式)
│   ├── width: 100
│   └── height: 150
│
├── monster_detect         # 🐌 怪物检测 ⚠️ Talery需确认
│   ├── mode: "contour_only"
│   ├── diff_thres: 0.8
│   ├── search_box_margin: 50
│   ├── contour_blur: 5
│   ├── with_enemy_hp_bar: True
│   ├── hp_bar_color: [71, 204, 64]  # BGR绿色 ⚠️ Talery需确认
│   └── max_mob_area_trigger: 1500
│
├── channel_change         # 🔁 换频道
│   ├── enable: False
│   ├── mode: "pixel"      # true/pixel
│   └── other_player_move_thres: 10
│
├── scheduled_channel_switching  # ⏰ 定时换线
│   ├── enable: False
│   └── interval_seconds: 1800
│
├── ui_coords              # 🧭 UI坐标 ⚠️ Talery必须更新
│   ├── ui_y_start: 610    # UI区域起始Y坐标
│   ├── menu: [1140, 730]
│   ├── channel: [1140, 666]
│   ├── random_channel: [877, 161]
│   ├── random_channel_confirm: [585, 420]
│   ├── select_character: [888, 275]
│   ├── login_button_thres: 0.05
│   ├── login_button_top_left: [838, 317]
│   └── login_button_bottom_right: [940, 373]
│
├── route                  # 🧭 路线导航
│   ├── search_range: 10   # 搜索半径(像素)
│   ├── jump_down_cooldown: 3.0
│   ├── color_code: {...}  # RGB→指令映射(12种颜色)
│   └── color_code_up_down: {...}  # 上下移动颜色映射
│
├── watchdog               # 🐶 卡住检测
│   ├── range: 10          # 移动阈值(像素)
│   ├── timeout: 10        # 超时(秒)
│   ├── last_attack_timeout: 1200  # 无攻击超时
│   └── last_attack_timeout_action: "change_channel"
│
├── rune_warning_cn/eng    # ⚠️ 符文警告 ⚠️ Talery不需要
├── rune_enable_msg_cn/eng # ⚠️ 符文启用消息 ⚠️ Talery不需要
├── rune_detect            # ✨ 符文检测 ⚠️ Talery不需要
├── rune_find              # 🧭 符文搜索 ⚠️ Talery不需要
├── rune_solver            # 🧩 符文解谜 ⚠️ Talery不需要
│
├── minimap                # 🗺️ 小地图 ⚠️ Talery需确认
│   ├── player_color: [136, 255, 255]    # BGR玩家点(黄)
│   ├── other_player_color: [0, 0, 255]  # BGR其他玩家(红)
│   ├── debug_window_upscale: 4
│   └── offset: [0, 0]
│
├── patrol                 # 🚶 巡逻模式
│   ├── range: [0.2, 0.8]
│   ├── turn_point_thres: 10
│   └── patrol_attack_interval: 2.5
│
├── route_recoder          # 🎥 路线录制器
│   ├── blob_cooldown: 0.7
│   └── map_padding: 30
│
├── game_window            # 🪟 游戏窗口 ⚠️ Talery必须更新
│   ├── title: "MapleStory Worlds"  # 窗口标题
│   ├── size: [693, 1282]           # [高, 宽]
│   ├── ratio_tolerance: 0.08       # 16:9容忍度
│   └── title_bar_height: 59
│
├── email                  # 📩 邮件通知
│   └── enable: False
│
├── system                 # ⚙️ 系统设置
│   ├── fps_limit_main: 10
│   ├── fps_limit_keyboard_controller: 30
│   ├── fps_limit_window_capturor: 15
│   ├── fps_limit_route_recorder: 10
│   ├── fps_limit_auto_dice_roller: 1
│   ├── key_debounce_interval: 1
│   ├── server: "TW"       # ⚠️ 需改为Talery标识
│   └── language: "cn"
│
└── profiler               # ⚙️ 性能分析
    ├── enable: False
    └── print_frequency: 30
```

### 4.2 config_data.yaml 结构

```yaml
eng_to_cn:           # 英文→中文翻译表
  ant_cave_2: 螞蟻洞2
  ...

map_mobs_mapping:    # 地图→怪物映射(每个地图注册的怪物)
  ant_cave_2: [spike_mushroom, zombie_mushroom]
  cloud_balcony: [pink_windup_bear, brown_windup_bear]
  ...共22个地图
```

---

## 五、依赖项

```
opencv-python          # 计算机视觉核心
numpy                  # 数值计算
pyautogui              # 屏幕截图/鼠标点击
pynput                 # 键盘监听
requests               # HTTP请求(怪物下载)
pyyaml                 # YAML解析
PySide6                # UI框架
ruamel.yaml            # YAML带注释读写
pyinstaller            # 打包exe
pywin32                # Windows API
windows-capture        # 高性能窗口截取
pyobjc-framework-Quartz # macOS截图
```

---

## 六、改造关键差异点总结

| 模块 | Artale现状 | Talery需要注意 | 变更级别 |
|------|-----------|---------------|---------|
| 游戏窗口 | 标题"MapleStory Worlds", 1296×759 | 窗口标题不同, 分辨率待确认 | **必须改** |
| 小地图 | 已有22个地图的map.png | 游戏本体一致, 地图资源大多可用 | 少量更新 |
| 路线图 | 已有路线录制 | 部分地图路线可能需要微调 | 少量更新 |
| 怪物图集 | 已有28种怪物PNG | 游戏本体一致, 大多可用 | 少量更新 |
| 符文系统 | Artale有符文机制 | **Talery无符文**, 需禁用 | **必须改** |
| UI坐标 | 基于1296×759计算 | 分辨率不同→坐标需重测 | **必须改** |
| 组队红条HSV | 已标定 | 颜色应一致(同为冒险岛客户端) | 可能不改 |
| 其他校验 | 无 | **Talery有其他校验机制** | **新增功能** |