# Talery 迁移改造进度跟踪

> 📅 创建: 2026-06-16 | 🔄 最后更新: 2026-06-18
> 🎯 总体进度: 阶段一分辨率适配完成, 阶段三开始(map.png重录制+引擎验证)

---

## 进度总览

| 阶段 | 内容 | 预计天数 | 状态 | 完成步骤 |
|------|------|---------|------|---------|
| 一 | 分辨率适配改造 | 1~2天 | ✅ 已完成 | 12/12 |
| 二 | 符文关闭+校验框架 | 2天 | ✅ 已完成 | 8/8 |
| 三 | 地图与路线验证 | 2天 | 🔴 进行中 | 1/22 (talery_ant_cave_2 录制完成) |
| 四 | 怪物图集验证 | 1天 | ⬜ 未开始 | 0/18 |
| 五 | 核心参数微调 | 2天 | ⬜ 未开始 | 0/12 |
| 六 | 校验机制适配 | 待定 | ⬜ 未开始 | 0/6 |
| 七 | 集成测试 | 3天 | ⬜ 未开始 | 0/5 |

**总体进度: 23%** (21/90 步骤完成)

---

## 阶段一: 分辨率适配改造 ✅

> ✅ 2026-06-18 完成。Talery 1280×720 分辨率已完全适配。

### 关键发现

| 参数 | Artale | Talery (实测) | 差异 |
|------|--------|---------------|------|
| 原始帧尺寸 | 1296×759 | **747×1282** | WindowsCapture 含标题栏 |
| 标题栏高度 | 59px | **27px** | 更小 |
| 内容区尺寸 | 693×1282 | **720×1282** | 宽度一致, 高度+27px |
| WINDOW_WORKING_SIZE | (1296, 700) | **(1296, 728)** | 保持原始宽高比 |

### 1.1 信息收集

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 1.1.1 | 确认 Talery 窗口标题 | ✅ 2026-06-18 | 标题为 TaleryMS-XXX (动态后缀), 模糊匹配 "TaleryMS" |
| 1.1.2 | 列出游戏内可选分辨率 | ✅ | 1280×720 原生 |
| 1.1.3 | 截图测量窗口/内容区/标题栏尺寸 | ✅ | 原始帧 747×1282, 标题栏 27px, 内容区 720×1282 |
| 1.1.4 | 测量 UI 按钮坐标 | ⬜ | 暂用 Artale 值, 待后续微调 |
| 1.1.5 | 测量符文相关 UI 坐标 | ⬜ | 符文已关闭, 低优先级 |

### 1.2 配置文件更新 (config_talery.yaml)

| # | 任务 | 值 |
|---|------|-----|
| 1.2.1 | `game_window.title` | `"TaleryMS"` (模糊匹配) |
| 1.2.2 | `game_window.size` | `[720, 1282]` |
| 1.2.3 | `game_window.title_bar_height` | `27` |
| 1.2.4 | `window_width` / `window_height` | `0` (跳过强制 resize) |

### 1.3 代码改造

| # | 文件 | 改动内容 |
|---|------|---------|
| 1.3.1 | `src/utils/global_var.py` | **新增** `get_window_working_size(cfg)` 函数 — 根据内容区尺寸动态计算工作尺寸, 保持原始宽高比 |
| 1.3.2 | `src/input/GameWindowCapturor.py` | resize_window 条件化 — `window_width > 0` 时才调用; Talery 配置为 0 则跳过 |
| 1.3.3 | `src/engine/MapleStoryAutoLevelUp.py` | 切频道重连时 resize 同样条件化 |
| 1.3.4 | `src/engine/MapleStoryAutoLevelUp.py` | `get_img_frame()` 改用 `get_window_working_size(self.cfg)` 替代 `WINDOW_WORKING_SIZE` |
| 1.3.5 | `src/engine/MapleStoryAutoLevelUp.py` | `VideoWriter` 初始化同样用动态尺寸 |
| 1.3.6 | `tools/routeRecorder.py` | `get_img_frame()` 同步改用 `get_window_working_size(self.cfg)` |

### 1.4 其他改动

| # | 说明 |
|---|------|
| `config_talery.yaml` | `ui_y_start: 660` — 按比例调整 (原 610 × 728/700 ≈ 634, 再加余量) |
| `src/engine/MapleStoryAutoLevelUp.py` | `ensure_is_in_party()` 添加 None 守卫 — 防止首帧未就绪崩溃 |
| `src/engine/MapleStoryAutoLevelUp.py` | minimap 绘制颜色从红色 `(0,0,255)` 改为绿色 `(0,255,0)` |

### 1.5 WINDOW_WORKING_SIZE 重要修复

**根因**: `WINDOW_WORKING_SIZE = (1296, 700)` 是为 Artale `693×1282` 设计的。Talery `720×1282` resize 到此尺寸时被**纵向压扁 2.8%**, 导致 `find_pattern_sqdiff` 模板匹配完全失败。

**修复**: 新增 `get_window_working_size(cfg)` 动态计算:

| 平台 | content size | 缩放比 | working size |
|------|-------------|-------|-------------|
| Artale | (693, 1282) | 1296/1282 ≈ 1.011 | (1296, **700**) |
| Talery | (720, 1282) | 1296/1282 ≈ 1.011 | (1296, **728**) |

**影响**: 引擎和 routeRecorder 的 `get_img_frame()` 均改用动态尺寸, 小地图不再变形。

---

## 阶段二: 符文关闭+校验框架 ✅

### 符文功能禁用

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 2.1.1 | config_talery 设置 rune.enable: false | ✅ | |
| 2.1.2 | 引擎添加 rune.enable 判断 | ✅ | hunting.py check_transitions() |
| 2.1.3 | Hunting 跳过符文检查 | ✅ | hunting.py |
| 2.1.4 | FSM 条件注册符文状态 | ✅ | 始终注册, 靠 rune.enable 控制是否触发 |

### 校验框架搭建

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 2.2.1 | 添加 talery_anti_cheat 配置块 | ✅ | config_talery.yaml |
| 2.2.2 | 新建 anti_cheat.py 状态 | ✅ | 空壳占位, 待后续完善 |
| 2.2.3 | FSM 注册 anti_cheat 状态 | ✅ | MapleStoryAutoLevelUp.py |
| 2.2.4 | Hunting 添加校验触发检测 | ✅ | hunting.py TODO占位 |

---

## 阶段三: 地图与路线验证 🔴

> 2026-06-18: talery_ant_cave_2 录制完成, 引擎验证进行中

### 地图资源状态

| 地图名 | Talery map.png | Talery route | 验证状态 | 备注 |
|--------|---------------|-------------|---------|------|
| talery_ant_cave_2 | ✅ 已录制 | ✅ route1.png | 🔴 验证中 | 怪物: spike_mushroom, zombie_mushroom |
| ant_cave_2 (Artale) | 🔒 原始 | 🔒 原始 | — | 仅 Artale 使用 |
| cloud_balcony | ⬜ | ⬜ | — | |
| dragon_territory | ⬜ | ⬜ | — | |
| empty_house | ⬜ | ⬜ | — | |
| fire_land_1 | ⬜ | ⬜ | — | |
| fire_land_2 | ⬜ | ⬜ | — | |
| first_barrack | ⬜ | ⬜ | — | |
| land_of_wild_boar | ⬜ | ⬜ | — | |
| lost_time_1 | ⬜ | ⬜ | — | |
| monkey_swamp_3 | ⬜ | ⬜ | — | |
| mushroom_hills | ⬜ | ⬜ | — | |
| north_forest_training_ground_2 | ⬜ | ⬜ | — | |
| north_forest_training_ground_8 | ⬜ | ⬜ | — | |
| pig_shores | ⬜ | ⬜ | — | |
| the_path_of_time_1_for_mage | ⬜ | ⬜ | — | |
| garden_of_green_2 | ⬜ | ⬜ | — | |
| garden_of_red_2 | ⬜ | ⬜ | — | |
| foggy_forest_for_mage | ⬜ | ⬜ | — | |
| 101_2f_east | ⬜ | ⬜ | — | |
| black_mountain | ⬜ | ⬜ | — | |
| disposed_flower_garden | ⬜ | ⬜ | — | |
| mu_Lung_wild_bear_area_2 | ⬜ | ⬜ | — | |

### config_data.yaml 更新

```yaml
map_mobs_mapping:
  ant_cave_2: [spike_mushroom, zombie_mushroom]
  talery_ant_cave_2: [spike_mushroom, zombie_mushroom]   # 新增 Talery 蚂蚁洞2
```

### 录制 map.png 步骤 (供后续地图参考)

```cmd
python -m tools.routeRecorder.py --cfg talery --new_map talery_<地图名>
```
- 跑遍地图全貌 → 按 **F4** 保存 map.png
- 按 **F3** 保存 route (可选)
- 按 **Q** 退出

---

## 阶段四: 怪物图集验证

| 怪物名 | 检测OK | 完成日期 | 备注 |
|--------|--------|---------|------|
| black_axe_stump | ⬜ | | |
| blue_perfume | ⬜ | | |
| brown_windup_bear | ⬜ | | |
| cold_eye | ⬜ | | |
| dark_nependeath | ⬜ | | |
| evolved_ghost | ⬜ | | |
| fire_boar | ⬜ | | |
| green_mushroom | ⬜ | | |
| grizzly | ⬜ | | |
| grupin | ⬜ | | |
| hodori | ⬜ | | |
| moon_bunny | ⬜ | | |
| mushroom | ⬜ | | |
| nependeath | ⬜ | | |
| nest_golem | ⬜ | | |
| panda | ⬜ | | |
| pig | ⬜ | | |
| pink_windup_bear | ⬜ | | |
| red_cellion | ⬜ | | |
| ribbon_pig | ⬜ | | |
| skeleton_officer | ⬜ | | |
| skeleton_soldier | ⬜ | | |
| skelosaurus | ⬜ | | |
| spike_mushroom | ⬜ | | |
| the_book_ghost | ⬜ | | |
| wild_boar | ⬜ | | |
| wild_kargo | ⬜ | | |
| wind_single_eye_beast | ⬜ | | |
| zombie_lupin | ⬜ | | |
| zombie_mushroom | ⬜ | | |

---

## 阶段五: 核心参数微调

### 玩家定位

#### 5.1 箭头定位 (新增, 替代 party_red_bar)

> ✅ 2026-06-18 完成。Talery 无组队红条，改为识别角色头顶的暗红色向下箭头。

| # | 参数 | 值 | 说明 | 完成 |
|---|------|-----|------|------|
| 5.1.0a | player_arrow.enable | true (Talery) | 启用箭头定位, 默认关闭 | ✅ |
| 5.1.0b | player_arrow.lower_arrow | [0, 30, 10] | HSV 下限 (暗红色箭头) | ✅ |
| 5.1.0c | player_arrow.upper_arrow | [15, 100, 80] | HSV 上限 | ✅ |
| 5.1.0d | player_arrow.offset | [22, 120] | 箭头左上→角色中心偏移 | ✅ |
| 5.1.0e | player_arrow.min_area | 100 | 最小轮廓面积 | ✅ |
| 5.1.0f | player_arrow.max_area | 3000 | 最大轮廓面积 | ✅ |

**箭头 BGR 分析结果 (基于 tools/2.png):**
- 尺寸: 45×102 (宽×高)
- BGR 均值: B≈28, G≈29, R≈111 (暗红色)
- HSV 均值: H≈62°, S≈72%, V≈43%
- Top 颜色: BGR(0,0,133) RGB(133,0,0) 出现 54 次
- BGR(0,0,112), BGR(0,0,111), BGR(0,0,127) 等暗红色系

**检测流水线:**
```
img_camera → HSV → inRange([0,30,10], [15,100,80]) → findContours
  → 过滤 100 ≤ area ≤ 3000 → 取最大面积 → 加 offset [22,120] → loc_player
```

**代码改动:**
| 文件 | 改动 |
|------|------|
| `config/config_default.yaml` | 新增 `player_arrow` 配置节 (默认 enable: false) |
| `config/config_talery.yaml` | 新增 `player_arrow` 配置节 (enable: true) |
| `src/engine/MapleStoryAutoLevelUp.py` | 新增 `get_player_location_by_arrow()` 方法 |
| `src/engine/MapleStoryAutoLevelUp.py` | `run_once()` 调用链: nametag → player_arrow → party_red_bar |

#### 5.1.x 原有 party_red_bar 参数 (Talery 不再使用)

| # | 参数 | 当前值 | 新值 | 完成 |
|---|------|--------|------|------|
| 5.1.1 | party_red_bar HSV | [0,60,60]-[0,100,100] | (Talery 不适用) | ⬜ |
| 5.1.2 | party_red_bar offset | [20, 66] | (Talery 不适用) | ⬜ |
| 5.1.3 | minimap player_color | [136,255,255] | | ⬜ |
| 5.1.4 | minimap other_player_color | [0,0,255] | | ⬜ |
| 5.1.5 | minimap offset | [0, 0] | | ⬜ |

### 怪物检测

| # | 参数 | 当前值 | 新值 | 完成 |
|---|------|--------|------|------|
| 5.2.1 | hp_bar_color | [71,204,64] | | ⬜ |
| 5.2.2 | diff_thres | 0.8 | | ⬜ |
| 5.2.3 | contour_blur | 5 | | ⬜ |

### 攻击与技能

| # | 参数 | 当前值 | 新值 | 完成 |
|---|------|--------|------|------|
| 5.3.1 | aoe_skill range | 400×170 | | ⬜ |
| 5.3.2 | directional range | 350×70 | | ⬜ |
| 5.3.3 | buff_skill 配置 | keys=[],cooldown=[] | | ⬜ |

---

## 阶段六: 校验机制适配

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 6.1 | 收集校验弹窗截图 | ⬜ | 需先游玩 Talery |
| 6.2 | 分类+设计检测方案 | ⬜ | |
| 6.3 | 完善 anti_cheat.py | ⬜ | |
| 6.4 | 更新配置参数 | ⬜ | |
| 6.5 | 自动处理测试 | ⬜ | |
| 6.6 | 失败保护逻辑 | ⬜ | |

---

## 阶段七: 集成测试

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 7.1 | 逐地图 10 分钟测试 | ⬜ | |
| 7.2 | 1 小时+稳定性测试 | ⬜ | |
| 7.3 | 多职业测试 | ⬜ | |
| 7.4 | 边界情况测试 | ⬜ | |
| 7.5 | 反外挂机制观察 | ⬜ | |

---

## 改动文件清单

### 修改的现有文件

| 文件 | 改动内容 |
|------|---------|
| `config/config_talery.yaml` | 填充窗口标题、分辨率、标题栏高度; 跳过 resize; ui_y_start 调整; **新增 player_arrow 箭头定位** |
| `config/config_data.yaml` | 新增 `talery_ant_cave_2` 地图和怪物映射 |
| `src/utils/global_var.py` | **新增** `get_window_working_size(cfg)` 动态计算工作尺寸 |
| `src/input/GameWindowCapturor.py` | resize_window 条件调用 — Talery 跳过 |
| `src/engine/MapleStoryAutoLevelUp.py` | ① resize 条件化 ② get_img_frame 动态尺寸 ③ VideoWriter 动态尺寸 ④ ensure_is_in_party None 守卫 ⑤ minimap 框颜色改绿色 |
| `tools/routeRecorder.py` | get_img_frame 动态尺寸 |

### 新增文件

| 文件 | 说明 |
|------|------|
| `minimaps/talery_ant_cave_2/map.png` | Talery 1280×720 下录制的全局地图 |
| `minimaps/talery_ant_cave_2/route1.png` | 路线图 |

### 未修改的文件 (保留原样)

| 文件 | 原因 |
|------|------|
| `config/config_default.yaml` | Artale 默认配置, 不修改 |
| `src/states/finding_rune.py` / `near_rune.py` / `solving_rune.py` | 通过配置控制是否触发 |
| `rune/` 目录 | 保留完整性 |
| `monster/` 目录 | 复用 Artale 怪物图集 |

---

## 📝 问题记录

| 日期 | 问题 | 解决方案 | 状态 |
|------|------|---------|------|
| 2026-06-18 | `ensure_is_in_party` 因 get_img_frame 返回 None 崩溃 | 添加 None 守卫, 优雅跳过 | ✅ |
| 2026-06-18 | 内容区尺寸反复变动 (688/720/747) | 最终确认为 747→裁剪27→720 | ✅ |
| 2026-06-18 | routeRecorder 小地图拼接偏移 | WINDOW_WORKING_SIZE 纵向压扁, 改为动态计算 | ✅ |
| 2026-06-18 | engine 中 routeMap 对不上 | Talery 的小地图比例与 Artale 录制的 map.png 不同, 需重新录制 | ✅ |

---

## 🔗 相关文档

- [项目分析文档](PROJECT_ANALYSIS.md)
- [迁移计划文档](TALERY_MIGRATION_PLAN.md)
- 上游仓库: https://github.com/KenYu910645/MapleStoryAutoLevelUp