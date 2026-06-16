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

### 🏗️ 阶段一: 基础环境适配 (预计 1 天)

**目标**: 让项目能识别 Talery 游戏窗口并启动基础功能

| 步骤 | 任务 | 涉及文件 | 状态 |
|------|------|---------|------|
| 1.1 | 获取 Talery 窗口标题和分辨率 | 启动游戏→用SPY++或pygetwindow获取 | ⬜ 待做 |
| 1.2 | 创建 Talery 专用配置文件 | 新建 `config/config_talery.yaml` | ⬜ 待做 |
| 1.3 | 更新 `game_window.title` 和 `game_window.size` | 修改配置 | ⬜ 待做 |
| 1.4 | 更新 `WINDOW_WORKING_SIZE` | `src/utils/global_var.py` | ⬜ 待做 |
| 1.5 | 更新 `ui_coords` 所有按钮坐标 | 截图测量 | ⬜ 待做 |
| 1.6 | 更新 `system.server` 为 Talery 标识 | 配置文件 | ⬜ 待做 |
| 1.7 | 验证窗口截图功能正常 | 启动引擎→观察调试窗口 | ⬜ 待做 |

**关键文件清单**:
- `config/config_talery.yaml` (新建)
- `src/utils/global_var.py` (修改 WINDOW_WORKING_SIZE)
- `config/config_default.yaml` (参考，不直接修改)

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
| 5.1.1 | 验证组队红条 HSV 颜色范围 | `party_red_bar.lower_red/upper_red` | ⬜ 待做 |
| 5.1.2 | 验证红条偏移量 (offset) | `party_red_bar.offset` | ⬜ 待做 |
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