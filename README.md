# Sultan of Karaya Telegram Bot

## 注意事項
偷看時會把對方身份用彈跳通知給你
不要按太快 會跑掉

通知內容會在查看中暫時保留

原始規則 蘇丹可以在任何時候登基
但因為現在AI動作太快 所以目前沒有這個功能

## command 指令

### newgame
方式：`/newgame`
效果：新遊戲 輸入者會有管理權限

### general
方式：`/general`
效果：跳出通用按鈕

### tutorial
方式：`/tutorial`
效果：私訊給你教學文件

### visual
方式：`/tutorial`
效果：視覺化遊戲狀況

## 規則

### 勝利條件
活著 且

若 保皇黨：蘇丹登基
若 反叛軍：刺客殺死蘇丹 奴隸革命成功
若 中立：見以下

### 回合動作
動作可以選擇以下其中一種
1. 交換身份
若身份公開 則秘密選擇其他隱藏身份的人交換身份
交換後自己的身份變為隱藏 可以選擇自己

若身份隱藏 則公開選擇其他隱藏身份的人交換身份
交換後自己的身份維持隱藏

2. 偷看身份
選擇其他隱藏身份的人交換身份

3. 身份特有動作
只有身份公開時可以使用
若使用前身份並非公開 則必須公開

#### 蘇丹
##### 特有動作：處決
選擇一公開反叛軍
殺死他

##### 被動：登基
在任何時候公開身份後
若維持一整輪的公開不隱藏
保皇黨勝利

##### 被動：避免關押
可以公開自己的保皇黨身份以避免關押

#### 守衛
特有動作：關押
選擇任何人
嘗試關押他

若成功關押 對方跳過下一個行動回合
且下一個行動回合前內不能使用自己的被動

##### 被動：阻止刺殺
當刺客刺殺時
你若在目標兩側或刺客兩側
可以公開自己的身份以阻止刺殺
殺死刺客

##### 被動：避免關押
可以公開自己的保皇黨身份以避免關押

#### 刺客
特有動作：刺殺
選擇任何人
嘗試刺殺他

#### 奴隸
特有動作：號召
觸發其他奴隸的響應

##### 被動：響應
當有奴隸號召時
可以立即選擇公開自己的身份

##### 被動：革命
當有三個以上的公開自由奴隸相鄰彼此時
反叛軍勝利

#### 販子
##### 特有動作：抓捕
抓捕一名角色

如果該名角色為一名公開奴隸
囚禁他

如果該名角色為一名隱藏奴隸
囚禁他 並獲得額外一回合動作

被囚禁的奴隸持續喪失回合且無法革命
直到販子死亡或隱藏

##### 獲勝條件：
若公開 勝利條件同保皇派
若隱藏 勝利條件同反叛軍


#### 舞孃
##### 特有動作：跳舞
維持公開狀態

##### 被動：
公開狀態時
兩旁的守衛不能關押也不能阻止刺殺

##### 獲勝條件：
若公開 勝利條件同反叛軍
若隱藏 勝利條件同保皇派


#### 大官
##### 特有動作：操弄
第一次公開時 
選擇一個隊伍作為支持隊伍

選擇一名隱藏角色 公開他的身份
強制該玩家進行一次角色動作
對象由該玩家決定

下一次輪到該玩家時
該玩家不能進行任何角色動作
只能偷看或交換

##### 獲勝條件：
若公開 支持隊伍勝利則勝利
若隱藏 兩旁玩家勝利則勝利

#### 先知
##### 特有動作：預言
偷看最多三名隱藏角色的身份 不能偷看白板

選擇一個隊伍作為預言對象

下一次輪到你時
必須使用交換

##### 獲勝條件：
若公開 預言對象勝利則勝利
若隱藏 則一定失敗
