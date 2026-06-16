# 添加新地图 & 新怪物操作指南

> 📅 创建: 2026-06-16 | 🔄 最后更新: 2026-06-16

---

## 一、巡线机制详解

### 1.1 原理

```
玩家全局坐标 → 在 route*.png 中搜索最近的 RGB颜色像素 → 解析为移动指令
```

**每帧执行流程**:
```
1. 通过小地图定位玩家全球位置 (loc_player_global)
2. get_nearest_color_code() 在玩家周围 search_range=10 像素内扫描 route 图
3. 找到最近的颜色指令像素 → 解析为 "left/right + up/down + jump/teleport/attack/stop/goal"
4. update_cmd_by_route() 输出到键盘控制器
```

### 1.2 route*.png 颜色编码表

| 颜色 | RGB | 指令 | 用途 |
|------|-----|------|------|
| 🔴 红 | 255,0,0 | left none none | 向左走 |
| 🔵 蓝 | 0,0,255 | right none none | 向右走 |
| 🟠 橙 | 255,127,0 | left none jump | 向左走+跳跃 |
| 🟦 青 | 0,255,255 | right none jump | 向右走+跳跃 |
| 💚 酸橙绿 | 127,255,0 | none down jump | 向下跳 |
| 💜 品红 | 255,0,255 | none none jump | 原地跳 |
| 🟢 浅绿 | 0,255,127 | stop stop stop | 停止/休息 |
| 🟨 黄 | 255,255,0 | none none goal | 到达路线终点→切换下一条路线 |
| 🌸 粉 | 255,0,127 | none up teleport | 向上瞬移(法师) |
| 🟪 紫 | 127,0,255 | none down teleport | 向下瞬移(法师) |
| 🟩 深绿 | 0,127,0 | left none teleport | 向左瞬移(法师) |
| 🟫 棕 | 139,69,19 | right none teleport | 向右瞬移(法师) |
| ⚪ 灰 | 127,127,127 | none up none | 向上爬(梯子) |
| 🟡 浅黄 | 255,255,127 | none down none | 向下爬(梯子) |

### 1.3 路线切换

```
route1.png → (黄色 goal) → route2.png → ... → route_rest.png (休息路线)
```

到达黄色终点后自动切换下一条路线。

---

## 二、怪物识别机制详解

### 2.1 原理

```
怪物模板PNG → 模板匹配(TM_SQDIFF_NORMED) → 攻击范围内筛选 → 选最近怪物
```

**配置项**: `monster_detect.mode` 决定算法（默认 `contour_only`）

| 模式 | 算法 | 速度 |
|------|------|------|
| `contour_only` (默认) | 提取PNG黑色轮廓→高斯模糊→模板匹配 + HP条颜色验证 | 中 |
| `color` | 彩色模板匹配(带mask) | 慢 |
| `grayscale` | 灰度模板匹配 | 中 |
| `template_free` | 连通组件检测(无视模板) | 快但误检多 |

### 2.2 怪物PNG格式要求

- **文件名**: `monster/<怪物名>/<怪物名>_1.png` (多个动作帧编号递增)
- **背景**: 纯绿色 `(0, 255, 0)` — 代码通过 `get_mask()` 自动将此颜色转为透明mask
- **自动翻转**: 加载时自动生成水平翻转版本

---

## 三、添加新地图 (分步操作)

### 步骤1: 录制路线图

```powershell
# 启动路线录制器
py -m tools.routeRecorder --new_map <地图目录名>
```

| 快捷键 | 功能 |
|--------|------|
| `F1` | 暂停/继续录制 |
| `F2` | 截图保存 |
| `F3` | **保存当前路线图** 并开始录制下一条 |
| `F4` | 保存扫描到的地图画面 |

### 步骤2: 文件产出

操作完成后在 `minimaps/<地图名>/` 下生成:
- `map.png` — 完整小地图截图（F4保存）
- `route1.png`, `route2.png`... — 录制的路线图（F3保存）

### 步骤3: 路线图手工微调 (用画图工具)

用 Paint/Photoshop 编辑 route*.png:
- 用 **精确RGB值** 在路线上画点/线标记移动方向
- **必须用取色器** 确保 RGB 值与上表一致
- 常见错误: 用画笔误写了偏差的色值 → 路线不生效

### 步骤4: 注册到配置

编辑 `config/config_data.yaml`:
```yaml
eng_to_cn:
  新地图目录名: 新地图中文名

map_mobs_mapping:
  新地图目录名: [怪物名1, 怪物名2]
```

---

## 四、添加新怪物 (分步操作)

### 步骤1: 下载怪物图集

```powershell
py tools/mob_maker.py
# 输入怪物英文名
Enter mob name: GreenMushroom
```

> 工具从 `https://maplestory.io/api/GMS/65/mob` 下载，自动排除死亡帧

输出: `monster/<怪物名>/<怪物名>_1.png`, `_2.png`...

### 步骤2: (备选) 手动截取PNG

如果 mob_maker 不支持 Talery 的API:
1. 在游戏中截取怪物截图
2. 用 PS 把怪物抠出来，背景填纯绿色 `#00FF00`
3. 保存到 `monster/<怪物名>/<怪物名>_1.png`

### 步骤3: 注册到配置

编辑 `config/config_data.yaml` 的 `map_mobs_mapping`:
```yaml
  ant_cave_2: [spike_mushroom, zombie_mushroom, 新怪物名]
```

---

## 五、常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 角色不沿路线走 | route图颜色RGB有偏差 | 用取色器确认色值，重新画点 |
| 路线走一半卡住 | 颜色点在 map.png 中被覆盖 | 代码自动 `mask_route_colors` 不过可能漏点 |
| 检测不到怪物 | 怪物PNG与游戏中外观不一致 | 重新截取/下载当前版本怪物图集 |
| 误检太多 | `diff_thres` 太高 | 降低 `monster_detect.diff_thres` |
| 不攻击 | 怪物在攻击范围之外 | 调整 `aoe_skill.range_x/y` 或 `directional_attack.range_x/y` |
| 路线录制器不工作 | 游戏窗口未识别 | 确认窗口标题匹配 `game_window.title` |

---

## 六、最小可用配置 Checklist

添加一个新地图+怪物最少需要:

- [ ] `minimaps/<地图名>/map.png` — 小地图截图
- [ ] `minimaps/<地图名>/route1.png` — 至少一条路线
- [ ] `monster/<怪物名>/<怪物名>_1.png` — 至少一帧怪物PNG(背景纯绿)
- [ ] `config/config_data.yaml` — `map_mobs_mapping` 中注册
- [ ] 选择地图 → 启动测试 → 观察调试窗口验证路线和怪物检测