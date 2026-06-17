# Talery 私服迁移改造计划

> 📅 创建日期: 2026-06-16
> 🔄 最后更新: 2026-06-16
> 🎯 目标: 将 Artale 自动练级工具适配到 Talery 私服
> 👥 协同开发: 是 (请阅读后更新进度)

---

## 一、核心改造策略

### 1.1 基本原则

| 原则 | 说明 |
|------|------|
| **保留原代码** | 不直接修改 Artale 源码，通过新增文件和配置切换实现适配 |
| **配置驱动** | 所有服务器差异通过 YAML 配置文件管理，运行时根据 `server` 参数切换 |
| **模块替换** | 对于完全不同的系统(如符文→校验)，编写新模块替换旧模块 |
| **渐进式适配** | 先跑通基础功能(窗口识别+玩家定位+路线导航+怪物检测)，再逐步调整细节参数 |

### 1.2 差异分析速查表

| 模块 | Artale | Talery | 适配策略 |
|------|--------|--------|---------|
| 游戏客户端 | MapleStory Worlds 客户端 | **基本相同** | 资源大多可复用 |
| 窗口分辨率 | 1296×759 | **可能不同** | 需确认并更新配置 |
| 窗口标题 | "MapleStory Worlds" | **不同** | 需获取并更新 |
| 小地图/路线 | 已有22个地图 | **多数一致** | 复用为主，验证后微调 |
| 怪物图集 | 已有28种怪物 | **多数一致** | 复用为主，新增差异怪物 |
| 道具/UI图集 | 标准样式 | **多数一致** | 复用为主 |
| 符文系统 (Rune) | 有符文(警告→搜索→触发→解谜) | **无符文** | **关闭符文功能，保留开关** |
| 其他校验机制 | 无 | **有不同的校验机制** | **新增校验处理模块** |
| 技能数值 | Artale 数值 | **可能有差异** | 核对后调整配置 |
| 地图路线 | Artale 布局 | **可能有局部差异** | 验证后微调路线图 |

---

## 二、改造阶段划分

### 🏗️ 阶段一: 基础环境适配 - 分辨率改造 (预计 1~2 天)

**目标**: 让项目在 Talery 的固定分辨率下正常工作

> ⚠️ **关键差异**: Talery 不支持手动调整窗口分辨率(不能调用 `win32gui.MoveWindow`)，只能从游戏内提供的几个固定分辨率中选择一个。Artale 则将窗口强制调整为 1296×759。

#### 1.0 分辨率硬编码依赖全景图

整个项目的视觉处理基于严格的分辨率假设链，需要从以下 7 处硬编码中解耦：

| # | 硬编码值 | 说明 | 位置 |
|---|---------|------|------|
| ① | `1296, 759` | resize_window 目标尺寸 | `GameWindowCapturor.py:40` |
| ② | `1296, 759` | 切频道重连后 resize | `MapleStoryAutoLevelUp.py:1258` |
| ③ | `59` px | 标题栏裁剪高度 | `config_default.yaml:307` → `get_img_frame()` |
| ④ | `[693, 1282]` | 内容区期望尺寸校验 | `config_default.yaml:305` → `get_img_frame()` 每帧校验 |
| ⑤ | `(1296, 700)` | cv2.resize 目标尺寸 | `global_var.py:3` → `get_img_frame()` 和 `routeRecorder.py` |
| ⑥ | `(693, 1282)` | normalize 标准尺寸 | `common.py:816` → `normalize_pixel_coordinate()` |
| ⑦ | 所有 `ui_coords` 坐标 | 按钮点击坐标 | `config_default.yaml` → `channel_change()` 等 |

数据流链：
```
resize_window(1296,759) → 截图 → 裁剪 title_bar_height(59) → 校验 size[693,1282]
  → cv2.resize 到 WINDOW_WORKING_SIZE(1296,700) → 所有 CV 操作基于此尺寸
  → UI 坐标也基于此尺寸 → click_in_game_window 加上 title_bar_height 偏移
```

#### 1.1 改造步骤

| 步骤 | 任务 | 涉及文件 | 改造内容 | 状态 |
|------|------|---------|---------|------|
| 1.1.1 | 确定 Talery 可用分辨率 | 启动游戏查看设置 | 记录游戏内可选分辨率列表，选择一个 16:9 的分辨率 | ⬜ |
| 1.1.2 | 截图测量各尺寸参数 | 截图工具 | 测量：窗口总尺寸、标题栏高度、内容区尺寸(h×w) | ⬜ |
| 1.1.3 | 填充 `config_talery.yaml` 分辨率配置 | `config/config_talery.yaml` | 更新 `game_window.title` / `size` / `title_bar_height`，新增 `window_width` / `window_height` | ⬜ |
| 1.1.4 | 改造 `WINDOW_WORKING_SIZE` 为动态计算 | `src/utils/global_var.py` | 改为函数 `get_window_working_size(cfg)`，根据配置中 `game_window.size` 按比例缩放 | ⬜ |
| 1.1.5 | 改造 `resize_window` 调用逻辑 | `src/input/GameWindowCapturor.py` | 加条件判断：配置中 `window_width>0` 时才调用 resize；Talery 配置设为 0 跳过 | ⬜ |
| 1.1.6 | 改造引擎中 `resize_window` 调用 | `src/engine/MapleStoryAutoLevelUp.py` | 第 1258 行同样加条件判断或从配置读取尺寸 | ⬜ |
| 1.1.7 | 改造 `get_img_frame()` 中的 WINDOW_WORKING_SIZE | `src/engine/MapleStoryAutoLevelUp.py` | 第 968 行替换为 `self.window_working_size`（从 init 中初始化） | ⬜ |
| 1.1.8 | 改造 `normalize_pixel_coordinate` 标准尺寸 | `src/utils/common.py` | 将 `(693, 1282)` 改为从参数传入，调用方传递 `cfg["game_window"]["size"]` | ⬜ |
| 1.1.9 | 同步改造 `routeRecorder.py` | `tools/routeRecorder.py` | 第 174 行的 resize 同样改为从配置动态获取 | ⬜ |
| 1.1.10 | 重新测量所有 UI 坐标 | 截图→标注坐标 | 更新 `config_talery.yaml` 中所有 `ui_coords` 值 | ⬜ |
| 1.1.11 | 重新测量符文相关坐标 | 截图→标注坐标 | 更新 rune_warning/rune_enable/rune_solver 坐标（即使符文关闭，保留配置完整性） | ⬜ |
| 1.1.12 | 验证窗口截图功能正常 | 启动引擎→观察调试窗口 | 确认截图尺寸、小地图检测、玩家定位正常 | ⬜ |

#### 1.2 配置变更说明 (`config_talery.yaml`)

```yaml
game_window:
  title: "<Talery实际窗口标题>"    # 1.1.1 获取
  size: [<H>, <W>]                 # 1.1.2 测量：内容区高度×宽度
  title_bar_height: <N>            # 1.1.2 测量：标题栏像素高度
  window_width: <W2>               # 新增：窗口总宽度(含边框)，若不需 resize 则填 0
  window_height: <H2>              # 新增：窗口总高度(含标题栏)，若不需 resize 则填 0
  ratio_tolerance: 0.08            # 保持，用于 aux 模式的 16:9 检查
```

#### 1.3 代码改造模板

**`global_var.py` 改为函数**：
```python
# 原: WINDOW_WORKING_SIZE = (1296, 700)
# 改为函数:
def get_window_working_size(cfg):
    """根据配置动态计算内部工作尺寸，保持宽度约 1296 基准"""
    h, w = cfg["game_window"]["size"]
    target_w = cfg.get("game_window", {}).get("working_width", 1296)
    scale = target_w / w
    target_h = int(h * scale)
    return (target_w, target_h)
```

**`GameWindowCapturor.py:40` 条件化 resize**：
```python
# 原:
resize_window(self.window_title, width=1296, height=759)
# 改为:
win_w = cfg.get("game_window", {}).get("window_width", 0)
win_h = cfg.get("game_window", {}).get("window_height", 0)
if win_w > 0 and win_h > 0:
    resize_window(self.window_title, width=win_w, height=win_h)
else:
    logger.info("[Talery] Using native resolution — resize_window skipped")
```

**`MapleStoryAutoLevelUp.py` init 中初始化工作尺寸**：
```python
from src.utils.global_var import get_window_working_size
self.window_working_size = get_window_working_size(cfg)
```

**`MapleStoryAutoLevelUp.py:968` 替换**：
```python
# 原: cv2.resize(frame_no_title, WINDOW_WORKING_SIZE, ...)
# 改为:
cv2.resize(frame_no_title, self.window_working_size, ...)
```

**`common.py:811` normalize 改为参数化**：
```python
def normalize_pixel_coordinate(coord, window_size, std_size=None):
    if std_size is None:
        std_size = (693, 1282)  # 默认兼容 Artale
    h_win, w_win = window_size
    h_std, w_std = std_size
    ...
```

**关键文件清单**:
- `config/config_talery.yaml` — 填充真实分辨率参数
- `src/utils/global_var.py` — `WINDOW_WORKING_SIZE` 改为函数
- `src/input/GameWindowCapturor.py` — 条件化 resize 调用
- `src/engine/MapleStoryAutoLevelUp.py` — 初始化 + get_img_frame 替换
- `src/utils/common.py` — normalize_pixel_coordinate 参数化
- `tools/routeRecorder.py` — 同步适配

#### 1.4 对 routeRecorder 的影响分析

`routeRecorder.py` 的 `get_img_frame()` (第 157-175 行) 与引擎中的逻辑几乎相同：
- 同样裁剪 `title_bar_height`、校验 `game_window.size`、resize 到 `WINDOW_WORKING_SIZE`
- **小地图拼接算法本身与分辨率无关** (通过白色边框连通区域检测定位)，只需帧被正确 resize
- 改造方案：复用上述 `global_var.py` 的函数化改造，同步替换 `WINDOW_WORKING_SIZE` 引用

#### 1.5 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| `get_minimap_loc_size` 白色边框粗细不同 | 小地图定位失败 | 算法基于连通区域面积过滤(≥100px)，不依赖固定尺寸 |
| 玩家点颜色 (136,255,255) 不同 | 玩家定位失败 | 需实测后更新 `minimap.player_color` 配置 |
| 怪物模板匹配率下降 | 怪物检测不准 | 若分辨率差异大，需用 `mob_maker.py` 重新截取模板 |
| 不同分辨率下 CV 阈值敏感 | 误检/漏检 | 先选一个分辨率跑通，后续可支持多分辨率 |

---

### 🚫 阶段二: 符文系统关闭与新校验框架搭建 (预计 2 天)

**目标**: 关闭符文系统但保留代码和开关，同时搭建新校验处理框架

**设计思路**: 
- 原符文系统代码完全保留不修改
- 在配置中新增 `talery_anti_cheat` 配置块控制校验行为
- 新增 `src/states/anti_cheat.py` 状态，替换符文状态机流转
- FSM 中新增 Talery 模式的状态路由

#### 2.1 符文功能禁用

| 步骤 | 任务 | 涉及文件 | 状态 |
|------|------|---------|------|
| 2.1.1 | 在 `config_talery.yaml` 中设置 `rune.enable: false` | `config/config_talery.yaml` | ⬜ 待做 |
| 2.1.2 | 在核心引擎中添加对 `rune.enable` 的判断 | `src/engine/MapleStoryAutoLevelUp.py` | ⬜ 待做 |
| 2.1.3 | Hunting 状态中跳过符文检查（当 rune.enable=false） | `src/states/hunting.py` | ⬜ 待做 |
| 2.1.4 | FSM 中不注册符文相关状态(配置控制) | `src/engine/MapleStoryAutoLevelUp.py` | ⬜ 待做 |

**修改逻辑**:
```python
# 在 MapleStoryAutoLevelUp.__init__ 中：
if cfg.get("rune", {}).get("enable", True):
    self.fsm.add_state(FindingRuneState("finding_rune", self))
    self.fsm.add_state(NearRuneState("near_rune", self))
    self.fsm.add_state(SolvingRuneState("solving_rune", self))
    # 注册符文相关转换...
else:
    logger.info("[Talery] Rune system disabled")

# 如果有新校验系统：
if cfg.get("talery_anti_cheat", {}).get("enable", False):
    self.fsm.add_state(AntiCheatState("anti_cheat", self))
    # 注册校验相关转换...
```

#### 2.2 新校验框架搭建

| 步骤 | 任务 | 涉及文件 | 状态 |
|------|------|---------|------|
| 2.2.1 | 在 `config_talery.yaml` 中添加 `talery_anti_cheat` 配置块 | `config/config_talery.yaml` | ⬜ 待做 |
| 2.2.2 | 新建 `src/states/anti_cheat.py` 校验状态 | 新建文件 | ⬜ 待做 |
| 2.2.3 | FSM 注册 anti_cheat 状态和相关转换 | `src/engine/MapleStoryAutoLevelUp.py` | ⬜ 待做 |
| 2.2.4 | Hunting 状态中加入校验触发检测 | `src/states/hunting.py` | ⬜ 待做 |

**`talery_anti_cheat` 配置块设计(模板)**:
```yaml
talery_anti_cheat:
  enable: true                     # 启用校验系统
  # 以下具体参数待确认Talery校验形式后填充
  detection:
    mode: "template"               # 检测模式: template/pixel_change/color
    check_interval: 5              # 检测间隔(秒)
    region_top_left: [0, 0]        # 检测区域(左上)
    region_bottom_right: [0, 0]    # 检测区域(右下)
    template_path: ""              # 校验弹窗模板路径
    diff_thres: 0.2                # 匹配阈值
  response:
    mode: "keypress"               # 响应模式: keypress/click/sequence
    key_sequence: ["enter"]        # 响应按键序列
    click_coord: [0, 0]            # 响应点击坐标
    timeout: 30                    # 处理超时(秒)
  recovery:
    max_retries: 3                 # 最大重试次数
    fallback_action: "change_channel"  # 失败后回退动作
```

**`src/states/anti_cheat.py` 状态模板**:
```python
class AntiCheatState(State):
    """Talery 反作弊/校验处理状态"""
    
    def on_enter(self):
        """进入校验处理状态，停止攻击"""
        self.bot.kb.set_command("stop stop stop")
    
    def on_exit(self):
        """退出校验状态，恢复狩猎"""
        pass
    
    def check_transitions(self):
        """检查是否完成校验，回到 hunting"""
        # 校验通过 → hunting
        # 超时 → recovery → hunting
        pass
    
    def on_frame(self):
        """每帧检测校验UI并执行响应"""
        # 1. 检测校验弹窗
        # 2. 按配置执行按键/点击响应
        # 3. 检查校验是否完成
        pass
```

---

### 🗺️ 阶段三: 地图与路线验证 (预计 2 天)

**目标**: 验证现有22个地图资源在 Talery 上的可用性，修正差异

| 步骤 | 任务 | 涉及目录 | 状态 |
|------|------|---------|------|
| 3.1 | 逐个地图验证 `map.png` 小地图匹配 | `minimaps/<map>/map.png` | ⬜ 待做 |
| 3.2 | 逐个地图验证 `route*.png` 路线可用性 | `minimaps/<map>/route*.png` | ⬜ 待做 |
| 3.3 | 对不一致的地图用 RouteRecorder 重新录制 | `tools/routeRecorder.py` | ⬜ 待做 |
| 3.4 | 更新 `config_data.yaml` 中的地图-怪物映射 | `config/config_data.yaml` | ⬜ 待做 |

**验证清单** (每个地图):

| 地图名 | map.png 可用 | route1 可用 | 备注 |
|--------|-------------|-------------|------|
| ant_cave_2 | ⬜ | ⬜ | |
| cloud_balcony | ⬜ | ⬜ | |
| dragon_territory | ⬜ | ⬜ | |
| empty_house | ⬜ | ⬜ | |
| fire_land_1 | ⬜ | ⬜ | |
| fire_land_2 | ⬜ | ⬜ | |
| first_barrack | ⬜ | ⬜ | |
| land_of_wild_boar | ⬜ | ⬜ | |
| lost_time_1 | ⬜ | ⬜ | |
| monkey_swamp_3 | ⬜ | ⬜ | |
| mushroom_hills | ⬜ | ⬜ | |
| north_forest_training_ground_2 | ⬜ | ⬜ | |
| north_forest_training_ground_8 | ⬜ | ⬜ | |
| pig_shores | ⬜ | ⬜ | |
| the_path_of_time_1_for_mage | ⬜ | ⬜ | |
| garden_of_green_2 | ⬜ | ⬜ | |
| garden_of_red_2 | ⬜ | ⬜ | |
| foggy_forest_for_mage | ⬜ | ⬜ | |
| 101_2f_east | ⬜ | ⬜ | |
| black_mountain | ⬜ | ⬜ | |
| disposed_flower_garden | ⬜ | ⬜ | |
| mu_Lung_wild_bear_area_2 | ⬜ | ⬜ | |

---

### 👾 阶段四: 怪物图集验证 (预计 1 天)

**目标**: 验证现有28种怪物模板在 Talery 上的检测准确率

| 步骤 | 任务 | 涉及目录 | 状态 |
|------|------|---------|------|
| 4.1 | 逐个怪物验证模板匹配准确率 | `monster/<mob>/` | ⬜ 待做 |
| 4.2 | 对检测失败的怪物重新截取图集 | `monster/<mob>/` | ⬜ 待做 |
| 4.3 | 如有新地图独有怪物，用 mob_maker 下载 | `tools/mob_maker.py` | ⬜ 待做 |
| 4.4 | 验证怪物 HP 条颜色是否一致 | 配置 `monster_detect.hp_bar_color` | ⬜ 待做 |

**验证清单** (核心怪物):

| 怪物名 | 检测正常 | 备注 |
|--------|---------|------|
| green_mushroom | ⬜ | |
| mushroom | ⬜ | |
| spike_mushroom | ⬜ | |
| zombie_mushroom | ⬜ | |
| pig | ⬜ | |
| ribbon_pig | ⬜ | |
| wild_boar | ⬜ | |
| fire_boar | ⬜ | |
| black_axe_stump | ⬜ | |
| pink_windup_bear | ⬜ | |
| brown_windup_bear | ⬜ | |
| evolved_ghost | ⬜ | |
| zombie_lupin | ⬜ | |
| cold_eye | ⬜ | |
| wind_single_eye_beast | ⬜ | |
| skeleton_soldier | ⬜ | |
| skeleton_officer | ⬜ | |
| wild_kargo | ⬜ | |
| ...等其余怪物 | ⬜ | |

---

### 🔧 阶段五: 核心参数微调 (预计 2 天)

**目标**: 调整视觉检测参数以适应 Talery 的显示差异

#### 5.1 玩家定位相关

| 步骤 | 任务 | 配置项 | 状态 |
|------|------|--------|------|
| 5.1.0a | ⬇️ 箭头定位: 启用 player_arrow | `player_arrow.enable` = true | ✅ 已完成 (2026-06-18) |
| 5.1.0b | 箭头 HSV 下限 (暗红色) | `player_arrow.lower_arrow` = [0, 30, 10] | ✅ 已完成 |
| 5.1.0c | 箭头 HSV 上限 | `player_arrow.upper_arrow` = [15, 100, 80] | ✅ 已完成 |
| 5.1.0d | 箭头→角色中心偏移 | `player_arrow.offset` = [22, 120] | ✅ 已完成 |
| 5.1.0e | 最小/最大轮廓面积 | `player_arrow.min/max_area` = 100/3000 | ✅ 已完成 |
| 5.1.1 | ~~验证组队红条 HSV~~ | 替换为箭头定位, 不再使用 party_red_bar | ~~取消~~ |
| 5.1.2 | ~~验证红条偏移量~~ | 替换为箭头定位 | ~~取消~~ |
| 5.1.3 | 验证小地图玩家点颜色 | `minimap.player_color` | ⬜ 待做 |
| 5.1.4 | 验证其他玩家点颜色 | `minimap.other_player_color` | ⬜ 待做 |
| 5.1.5 | 验证小地图全局偏移 | `minimap.offset` | ⬜ 待做 |

#### 5.2 怪物检测相关

| 步骤 | 任务 | 配置项 | 状态 |
|------|------|--------|------|
| 5.2.1 | 验证怪物 HP 条 BGR 颜色 | `monster_detect.hp_bar_color` | ⬜ 待做 |
| 5.2.2 | 调整模板匹配合适阈值 | `monster_detect.diff_thres` | ⬜ 待做 |
| 5.2.3 | 调整轮廓模糊参数 | `monster_detect.contour_blur` | ⬜ 待做 |
| 5.2.4 | 调整最大怪物面积触发值 | `monster_detect.max_mob_area_trigger` | ⬜ 待做 |

#### 5.3 攻击与技能

| 步骤 | 任务 | 配置项 | 状态 |
|------|------|--------|------|
| 5.3.1 | 验证 AoE 技能范围 | `aoe_skill.range_x/y` | ⬜ 待做 |
| 5.3.2 | 验证定向攻击范围 | `directional_attack.range_x/y` | ⬜ 待做 |
| 5.3.3 | 调整攻击冷却时间 | `directional_attack.cooldown` | ⬜ 待做 |
| 5.3.4 | 更新 buff 技能键位和冷却 | `buff_skill.keys/cooldown` | ⬜ 待做 |

#### 5.4 平台检测

| 步骤 | 任务 | 配置项 | 状态 |
|------|------|--------|------|
| 5.4.1 | 验证平台边缘颜色码 | `edge_teleport.color_code` | ⬜ 待做 |
| 5.4.2 | 调整边缘检测框尺寸 | `edge_teleport.trigger_box_*` | ⬜ 待做 |

#### 5.5 UI 模板

| 步骤 | 任务 | 涉及文件 | 状态 |
|------|------|---------|------|
| 5.5.1 | 验证登录按钮模板 | `misc/login_button_*` | ⬜ 待做 |
| 5.5.2 | 验证组队按钮模板 | `misc/party_button_*` | ⬜ 待做 |

---

### 🧪 阶段六: 校验机制适配 (待确认具体形式后细化)

**目标**: 根据 Talery 实际校验机制开发响应模块

> ⚠️ 此阶段需要先观察 Talery 的校验机制具体形式：
> - 是弹窗验证码？
> - 是随机问题？
> - 是行为检测告警？
> - 是 GM 巡逻检测？
> - 确定后再制定详细方案

| 步骤 | 任务 | 状态 |
|------|------|------|
| 6.1 | 游玩Talery→截图收集所有校验弹窗/appearance | ⬜ 待做 |
| 6.2 | 分类校验类型→设计检测模板 | ⬜ 待做 |
| 6.3 | 完善 `src/states/anti_cheat.py` 校验处理逻辑 | ⬜ 待做 |
| 6.4 | 更新 `talery_anti_cheat` 配置块 | ⬜ 待做 |
| 6.5 | 测试校验自动处理 | ⬜ 待做 |
| 6.6 | 添加校验失败保护(切频道/回城) | ⬜ 待做 |

---

### 🧪 阶段七: 集成测试与稳定性 (预计 3 天)

| 步骤 | 任务 | 状态 |
|------|------|------|
| 7.1 | 每个地图挂机 10 分钟验证 | ⬜ 待做 |
| 7.2 | 长时间挂机稳定性测试 (1小时+) | ⬜ 待做 |
| 7.3 | 不同职业配置测试 | ⬜ 待做 |
| 7.4 | 边界情况: 断线重连、被抢图换频道、死亡复活 | ⬜ 待做 |
| 7.5 | 观察 Talery 是否有反外挂机制需要额外处理 | ⬜ 待做 |

---

## 三、配置文件设计方案

### 3.1 配置文件加载顺序

```
config_default.yaml          → 基础默认参数(原始Artale)
     ↓ 被覆盖
config_talery.yaml           → Talery 特有参数覆盖
     ↓ 被覆盖
config_edit_me.yaml          → 用户个人设置(final override)
```

### 3.2 config_talery.yaml 模板

```yaml
# ====== Talery Server Configuration ======
# This config overrides config_default.yaml for Talery server

system:
  server: "Talery"         # 服务器标识

game_window:
  title: "TO_BE_DETERMINED"   # ⚠️ 待确认 Talery 窗口标题
  size: [693, 1282]           # ⚠️ 待确认分辨率 [高, 宽]

ui_coords:
  ui_y_start: 610             # ⚠️ 待测量
  menu: [1140, 730]           # ⚠️ 待测量
  channel: [1140, 666]        # ⚠️ 待测量
  # ...所有UI坐标待测量

rune:
  enable: false               # 🚫 Talery无符文系统

talery_anti_cheat:
  enable: true                # ✅ 启用校验处理
  detection:
    mode: "template"          # 待确认具体形式
    check_interval: 5
    region_top_left: [0, 0]   # ⚠️ 待测量
    region_bottom_right: [0, 0]  # ⚠️ 待测量
  response:
    mode: "keypress"
    key_sequence: ["enter"]
    timeout: 30
  recovery:
    max_retries: 3
    fallback_action: "change_channel"
```

---

## 四、需要新增/修改的代码文件清单

### 4.1 新建文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `config/config_talery.yaml` | Talery 专用配置 | P0 |
| `src/states/anti_cheat.py` | 校验处理状态 | P1 |
| `docs/PROJECT_ANALYSIS.md` | 项目分析文档 ✅已创建 | P0 |
| `docs/TALERY_MIGRATION_PLAN.md` | 本计划文档 ✅已创建 | P0 |
| `docs/PROGRESS.md` | 进度跟踪文档 | P0 |

### 4.2 需修改的现有文件

| 文件 | 修改内容 | 修改原则 | 优先级 |
|------|---------|---------|--------|
| `src/utils/global_var.py` | 容纳新分辨率 | 加条件判断 | P0 |
| `src/engine/MapleStoryAutoLevelUp.py` | 加载 `rune.enable` / `talery_anti_cheat` 配置；条件注册FSM状态 | **最小侵入**，if-else分支 | P0 |
| `src/states/hunting.py` | 根据 `rune.enable` 跳过符文检查；添加校验触发检测 | **最小侵入** | P0 |
| `src/input/GameWindowCapturor.py` | 支持 Talery 窗口标题 | 复用现有模糊匹配 | P0 |

### 4.3 不需要修改的文件(保留原样)

| 文件/目录 | 原因 |
|-----------|------|
| `src/engine/RuneSolver.py` | **完全保留**，通过配置控制是否加载 |
| `src/states/finding_rune.py` | **完全保留**，通过配置控制是否注册 |
| `src/states/near_rune.py` | **完全保留**，通过配置控制是否注册 |
| `src/states/solving_rune.py` | **完全保留**，通过配置控制是否注册 |
| `rune/` 目录 | **完全保留**，不含符文服务器不加载该资源 |
| `tools/mob_maker.py` | **保留**，可能用于补充怪物图集 |
| `tools/routeRecorder.py` | **保留**，用于重新录制路线 |

---

## 五、待确认事项清单

> 🔴 以下是开始编码前必须确认的关键信息

| # | 事项 | 重要性 | 确认方式 | 状态 |
|---|------|--------|---------|------|
| 1 | Talery 游戏窗口标题是什么？ | 🔴 必须 | 启动游戏后 SPY++ 查看 | ⬜ |
| 2 | Talery 游戏窗口分辨率？ | 🔴 必须 | 截图测量或 SPY++ | ⬜ |
| 3 | Talery 是否有校验弹窗？什么形式？ | 🟡 高 | 实际游玩体验 | ⬜ |
| 4 | Talery 是否有反外挂检测？频率？ | 🟡 高 | 观察+社区调研 | ⬜ |
| 5 | 怪物外观是否和 Artale 一致？ | 🟢 中 | 截图对比 | ⬜ |
| 6 | 小地图布局是否和 Artale 一致？ | 🟢 中 | 逐个地图对比 | ⬜ |
| 7 | 技能范围/伤害机制是否和 Artale 一致？ | 🟢 中 | 游戏内测试 | ⬜ |
| 8 | 组队红条颜色样式是否一致？ | 🟢 中 | 截图对比 | ⬜ |

---

## 六、协同开发指南

### 6.1 如何继续开发

1. **阅读顺序**: 先读 `docs/PROJECT_ANALYSIS.md`(了解项目) → 再读本文件(了解改造计划)
2. **查看进度**: 打开 `docs/PROGRESS.md` 查看当前完成状态
3. **选择任务**: 从本计划的"状态"列找 ⬜ 待做的步骤
4. **更新进度**: 完成步骤后将本文件和 `PROGRESS.md` 中对应状态改为 ✅

### 6.2 代码修改注意事项

- 对 `MapleStoryAutoLevelUp.py` 的修改**必须保持最小侵入**，使用条件分支而非删除原代码
- 每次修改后运行 `python -m src.main` 确认 UI 能正常启动
- 资源目录新增以 `talery_` 前缀命名，避免覆盖 Artale 资源