# Talery 迁移改造进度跟踪

> 📅 创建: 2026-06-16 | 🔄 最后更新: 2026-06-17
> 🎯 总体进度: 2/7 阶段完成 (阶段二完成; 阶段一×分辨率,细化后重新排入)

---

## 进度总览

| 阶段 | 内容 | 预计天数 | 状态 | 完成步骤 |
|------|------|---------|------|---------|
| 一 | 分辨率适配改造 | 1~2天 | 🔴 进行中 | 0/12 |
| 二 | 符文关闭+校验框架 | 2天 | ✅ 已完成 | 8/8 |
| 三 | 地图与路线验证 | 2天 | ⬜ 未开始 | 0/22 |
| 四 | 怪物图集验证 | 1天 | ⬜ 未开始 | 0/18 |
| 五 | 核心参数微调 | 2天 | ⬜ 未开始 | 0/12 |
| 六 | 校验机制适配 | 待定 | ⬜ 未开始 | 0/6 |
| 七 | 集成测试 | 3天 | ⬜ 未开始 | 0/5 |

**总体进度: 9%** (8/90 步骤完成: 阶段二8/8 + 阶段一分析完成)

---

## 阶段一: 分辨率适配改造 (重新细化)

> ⚠️ Talery 不支持手动调分辨率 → 需要从代码中解耦所有 1296×759 硬编码
> 
> 📊 **分析已完成** (2026-06-17): 发现 7 处硬编码依赖，详见 TALERY_MIGRATION_PLAN.md §1.0

#### 1.1 信息收集

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 1.1.1 | 确认 Talery 窗口标题 | ⬜ | 启动游戏后用 SPY++ 或 pygetwindow 查看 |
| 1.1.2 | 列出游戏内可选分辨率 | ⬜ | 打开游戏设置→查看分辨率选项 |
| 1.1.3 | 截图测量窗口/内容区/标题栏尺寸 | ⬜ | 选择 16:9 分辨率后截图 |
| 1.1.4 | 测量所有 UI 按钮坐标 | ⬜ | menu/channel/random_channel/login_button 等 |
| 1.1.5 | 测量符文相关 UI 坐标 | ⬜ | rune_warning/rune_enable/rune_solver (即使关闭,保留完整性) |

#### 1.2 配置文件更新

| # | 任务 | 涉及文件 | 完成日期 | 备注 |
|---|------|---------|---------|------|
| 1.2.1 | 更新 `game_window.title` | `config/config_talery.yaml` | ⬜ | |
| 1.2.2 | 更新 `game_window.size` | `config/config_talery.yaml` | ⬜ | 内容区 [H, W] |
| 1.2.3 | 更新 `game_window.title_bar_height` | `config/config_talery.yaml` | ⬜ | |
| 1.2.4 | 新增 `window_width`/`window_height` | `config/config_talery.yaml` | ⬜ | Talery 填 0 表示不强制 resize |
| 1.2.5 | 更新所有 `ui_coords` 向坐标 | `config/config_talery.yaml` | ⬜ | |
| 1.2.6 | 更新符文相关坐标 | `config/config_talery.yaml` | ⬜ | |

#### 1.3 代码改造

| # | 任务 | 涉及文件 | 改造内容 | 完成日期 | 备注 |
|---|------|---------|---------|---------|------|
| 1.3.1 | 动态计算工作尺寸 | `src/utils/global_var.py` | `WINDOW_WORKING_SIZE` 常量→ `get_window_working_size(cfg)` 函数 | ⬜ | |
| 1.3.2 | 条件化 resize 调用 | `src/input/GameWindowCapturor.py:40` | `window_width>0` 时才调用 resize, Talery 跳过 | ⬜ | |
| 1.3.3 | 条件化 resize 调用 | `src/engine/MapleStoryAutoLevelUp.py:1258` | 切频道重连时同样处理 | ⬜ | |
| 1.3.4 | 替换 WINDOW_WORKING_SIZE | `src/engine/MapleStoryAutoLevelUp.py:968` | 用 `self.window_working_size` | ⬜ | init 中初始化 |
| 1.3.5 | 参数化 normalize | `src/utils/common.py:816` | `(693,1282)` → 从参数或配置传入 | ⬜ | |
| 1.3.6 | 同步改造 routeRecorder | `tools/routeRecorder.py:174` | 同样替换 WINDOW_WORKING_SIZE 引用 | ⬜ | |

#### 1.4 验证

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 1.4.1 | 启动引擎+确认截图尺寸正确 | ⬜ | 观察调试窗口尺寸 |
| 1.4.2 | 确认小地图检测 (get_minimap_loc_size) 正常 | ⬜ | |
| 1.4.3 | 确认玩家定位 (黄色点) 正常 | ⬜ | 若颜色不同需更新 minimap.player_color |
| 1.4.4 | 确认 routeRecorder 录制正常 | ⬜ | 跑一小段路→按 F4 保存 map.png |

---

## 阶段二: 符文关闭+校验框架

### 符文功能禁用

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 2.1.1 | config_talery 设置 rune.enable: false | ✅ | |
| 2.1.2 | 引擎添加 rune.enable 判断 | ✅ | hunting.py check_transitions() |
| 2.1.3 | Hunting 跳过符文检查 | ✅ | hunting.py |
| 2.1.4 | FSM 条件注册符文状态 | ✅ | 始终注册，靠 rune.enable 控制是否触发 |

### 校验框架搭建

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 2.2.1 | 添加 talery_anti_cheat 配置块 | ✅ | config_talery.yaml |
| 2.2.2 | 新建 anti_cheat.py 状态 | ✅ | 空壳占位，待后续完善 |
| 2.2.3 | FSM 注册 anti_cheat 状态 | ✅ | MapleStoryAutoLevelUp.py |
| 2.2.4 | Hunting 添加校验触发检测 | ✅ | hunting.py TODO占位 |

---

## 阶段三: 地图与路线验证

| 地图名 | map.png | route可用 | 完成日期 | 备注 |
|--------|---------|----------|---------|------|
| ant_cave_2 | ⬜ | ⬜ | | |
| cloud_balcony | ⬜ | ⬜ | | |
| dragon_territory | ⬜ | ⬜ | | |
| empty_house | ⬜ | ⬜ | | |
| fire_land_1 | ⬜ | ⬜ | | |
| fire_land_2 | ⬜ | ⬜ | | |
| first_barrack | ⬜ | ⬜ | | |
| land_of_wild_boar | ⬜ | ⬜ | | |
| lost_time_1 | ⬜ | ⬜ | | |
| monkey_swamp_3 | ⬜ | ⬜ | | |
| mushroom_hills | ⬜ | ⬜ | | |
| north_forest_training_ground_2 | ⬜ | ⬜ | | |
| north_forest_training_ground_8 | ⬜ | ⬜ | | |
| pig_shores | ⬜ | ⬜ | | |
| the_path_of_time_1_for_mage | ⬜ | ⬜ | | |
| garden_of_green_2 | ⬜ | ⬜ | | |
| garden_of_red_2 | ⬜ | ⬜ | | |
| foggy_forest_for_mage | ⬜ | ⬜ | | |
| 101_2f_east | ⬜ | ⬜ | | |
| black_mountain | ⬜ | ⬜ | | |
| disposed_flower_garden | ⬜ | ⬜ | | |
| mu_Lung_wild_bear_area_2 | ⬜ | ⬜ | | |

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
| panda | ⬜ | | |
| pig | ⬜ | | |
| pink_windup_bear | ⬜ | | |
| red_cellion | ⬜ | | |
| ribbon_pig | ⬜ | | |
| skeleton_officer | ⬜ | | |
| skeleton_soldier | ⬜ | | |
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

| # | 参数 | 当前值 | 新值 | 完成 |
|---|------|--------|------|------|
| 5.1.1 | party_red_bar HSV | [0,60,60]-[0,100,100] | | ⬜ |
| 5.1.2 | party_red_bar offset | [20, 66] | | ⬜ |
| 5.1.3 | minimap player_color | [136,255,255] | | ⬜ |
| 5.1.4 | minimap other_player | [0,0,255] | | ⬜ |
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
| 6.1 | 收集校验弹窗截图 | ⬜ | 需先游玩Talery |
| 6.2 | 分类+设计检测方案 | ⬜ | |
| 6.3 | 完善 anti_cheat.py | ⬜ | |
| 6.4 | 更新配置参数 | ⬜ | |
| 6.5 | 自动处理测试 | ⬜ | |
| 6.6 | 失败保护逻辑 | ⬜ | |

---

## 阶段七: 集成测试

| # | 任务 | 完成日期 | 备注 |
|---|------|---------|------|
| 7.1 | 逐地图10分钟测试 | ⬜ | |
| 7.2 | 1小时+稳定性测试 | ⬜ | |
| 7.3 | 多职业测试 | ⬜ | |
| 7.4 | 边界情况测试 | ⬜ | |
| 7.5 | 反外挂机制观察 | ⬜ | |

---

## 📝 问题记录

| 日期 | 问题描述 | 解决方案 | 状态 |
|------|---------|---------|------|
| | | | |

---

## 🔗 相关文档

- [项目分析文档](PROJECT_ANALYSIS.md) - 了解项目架构和代码
- [迁移计划文档](TALERY_MIGRATION_PLAN.md) - 详细改造方案
- 上游仓库: https://github.com/KenYu910645/MapleStoryAutoLevelUp