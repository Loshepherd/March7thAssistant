from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QStackedWidget, QSpacerItem
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup, PushSettingCard, ScrollArea, InfoBar, PrimaryPushSettingCard, Pivot
from .common.style_sheet import StyleSheet
from .card.comboboxsettingcard1 import ComboBoxSettingCard1
from .card.comboboxsettingcard2 import ComboBoxSettingCard2
from .card.switchsettingcard1 import SwitchSettingCard1
from .card.rangesettingcard1 import RangeSettingCard1
from .card.pushsettingcard1 import PushSettingCardInstance, PushSettingCardEval, PushSettingCardDate, PushSettingCardKey, PushSettingCardTeam
from managers.config_manager import config
from tasks.base.tasks import start_task
from .tools.check_update import checkUpdate
import os


class SettingInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)

        self.settingLabel = QLabel(self.tr("设置"), self)

        self.__initWidget()
        self.__initCard()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self):
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setViewportMargins(0, 140, 0, 5)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setObjectName('settingInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

    def __initCard(self):
        self.PowerGroup = SettingCardGroup(self.tr("体力设置"), self.scrollWidget)
        self.instanceTypeCard = ComboBoxSettingCard1(
            "instance_type",
            FIF.ALIGNMENT,
            self.tr('副本类型'),
            None,
            texts=['拟造花萼（金）', '拟造花萼（赤）', '凝滞虚影', '侵蚀隧洞']
        )
        self.calyxGoldenPreferenceCard = ComboBoxSettingCard2(
            "calyx_golden_preference",
            FIF.PIE_SINGLE,
            self.tr('拟造花萼（金）偏好地区'),
            '',
            texts={'雅利洛-VI': 'Jarilo-VI', '仙舟「罗浮」': 'XianzhouLuofu', '匹诺康尼': 'Penacony'}
        )
        self.instanceNameCard = PushSettingCardInstance(
            self.tr('修改'),
            FIF.PALETTE,
            self.tr("副本名称"),
            "instance_names",
            "./assets/config/instance_names.json"
        )
        self.breakDownLevelFourRelicsetEnableCard = SwitchSettingCard1(
            FIF.FILTER,
            self.tr('自动分解四星遗器'),
            self.tr('侵蚀隧洞、历战余响和模拟宇宙（开启领取沉浸奖励）完成后自动分解四星及以下遗器'),
            "break_down_level_four_relicset"
        )
        self.instanceTeamEnableCard = SwitchSettingCard1(
            FIF.EDIT,
            self.tr('自动切换队伍'),
            None,
            "instance_team_enable"
        )
        self.instanceTeamNumberCard = ComboBoxSettingCard1(
            "instance_team_number",
            FIF.FLAG,
            self.tr('队伍编号'),
            None,
            texts=['3', '4', '5', '6', '7']
        )
        self.mergeImmersifierEnableCard = SwitchSettingCard1(
            FIF.BASKETBALL,
            self.tr('优先合成沉浸器'),
            "达到上限八个后停止，可搭配每天一定次数的模拟宇宙实现循环",
            "merge_immersifier"
        )
        self.useReservedTrailblazePowerEnableCard = SwitchSettingCard1(
            FIF.HEART,
            self.tr('使用后备开拓力'),
            "单次上限240点，全部使用需要将“任务完成后”选项修改为“循环”，然后点击“完整运行”",
            "use_reserved_trailblaze_power"
        )
        self.useFuelEnableCard = SwitchSettingCard1(
            FIF.CAFE,
            self.tr('使用燃料'),
            "单次上限5个，全部使用需要将“任务完成后”选项修改为“循环”，然后点击“完整运行”",
            "use_fuel"
        )
        self.echoofwarEnableCard = SwitchSettingCard1(
            FIF.MEGAPHONE,
            self.tr('启用历战余响'),
            "每周体力优先完成三次「历战余响」，仅限完整运行生效",
            "echo_of_war_enable"
        )
        self.echoofwarRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次完成历战余响的时间"),
            "echo_of_war_timestamp"
        )

        self.BorrowGroup = SettingCardGroup(self.tr("支援设置"), self.scrollWidget)
        self.borrowEnableCard = SwitchSettingCard1(
            FIF.PIN,
            self.tr('启用使用支援角色'),
            '',
            "borrow_enable"
        )
        self.borrowCharacterEnableCard = SwitchSettingCard1(
            FIF.UNPIN,
            self.tr('强制使用支援角色'),
            self.tr('无论何时都要使用支援角色，即使日常实训中没有要求'),
            "borrow_character_enable"
        )
        self.borrowCharacterFromCard = PushSettingCardEval(
            self.tr('修改'),
            FIF.PEOPLE,
            self.tr("指定好友的支援角色（填写用户名，模糊匹配模式）"),
            "borrow_character_from"
        )
        self.borrowCharacterInfoCard = PrimaryPushSettingCard(
            self.tr('打开角色文件夹'),
            FIF.INFO,
            self.tr("↓↓支援角色↓↓"),
            self.tr("角色对应的英文名字可以在 \"March7thAssistant\\assets\\images\\share\\character\" 中查看")
        )
        self.borrowCharacterCard = PushSettingCardEval(
            self.tr('修改'),
            FIF.ARROW_DOWN,
            self.tr("支援角色优先级（从高到低）"),
            "borrow_character"
        )

        self.DailyGroup = SettingCardGroup(self.tr("日常设置"), self.scrollWidget)
        self.dispatchEnableCard = SwitchSettingCard1(
            FIF.STOP_WATCH,
            self.tr('领取委托奖励'),
            None,
            "reward_dispatch_enable"
        )
        self.mailEnableCard = SwitchSettingCard1(
            FIF.MAIL,
            self.tr('领取邮件奖励'),
            None,
            "reward_mail_enable"
        )
        self.assistEnableCard = SwitchSettingCard1(
            FIF.BRUSH,
            self.tr('领取支援奖励'),
            None,
            "reward_assist_enable"
        )
        self.dailyEnableCard = SwitchSettingCard1(
            FIF.CALENDAR,
            self.tr('启用每日实训'),
            "关闭后可通过手动配置每天一次模拟宇宙来完成500活跃度（推荐每天四次）",
            "daily_enable"
        )
        self.dailyHimekoTryEnableCard = SwitchSettingCard1(
            FIF.CHECKBOX,
            self.tr('通过 “姬子试用” 完成任务'),
            "",
            "daily_himeko_try_enable"
        )
        self.dailyMemoryOneEnableCard = SwitchSettingCard1(
            FIF.CHECKBOX,
            self.tr('通过 “回忆一” 完成任务'),
            "请解锁混沌回忆并配置了队伍后再打开该选项，部分任务需要反复运行至多三次",
            "daily_memory_one_enable"
        )
        self.dailyMemoryOneTeamCard = PushSettingCardTeam(
            self.tr('修改'),
            FIF.FLAG,
            self.tr("回忆一队伍"),
            "daily_memory_one_team"
        )
        self.lastRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次检测日常的时间"),
            "last_run_timestamp"
        )

        self.ActivityGroup = SettingCardGroup(self.tr("活动设置"), self.scrollWidget)
        self.activityEnableCard = SwitchSettingCard1(
            FIF.CERTIFICATE,
            self.tr('启用活动检测'),
            None,
            "activity_enable"
        )
        self.activityGiftOfOdysseyEnableCard = SwitchSettingCard1(
            FIF.COMPLETED,
            self.tr('启用巡星之礼'),
            "自动领取「星轨专票x10」",
            "activity_giftofodyssey_enable"
        )
        self.activityGiftOfRadianceEnableCard = SwitchSettingCard1(
            FIF.COMPLETED,
            self.tr('启用巡光之礼'),
            "自动领取「星琼x800」",
            "activity_giftofradiance_enable"
        )
        self.activityGardenOfPlentyEnableCard = SwitchSettingCard1(
            FIF.CALORIES,
            self.tr('启用花藏繁生'),
            "存在双倍次数时体力优先「拟造花萼」",
            "activity_gardenofplenty_enable"
        )
        self.activityGardenOfPlentyTypeCard = ComboBoxSettingCard1(
            "activity_gardenofplenty_instance_type",
            FIF.CLEAR_SELECTION,
            self.tr('花藏繁生副本类型'),
            None,
            texts=['拟造花萼（金）', '拟造花萼（赤）']
        )
        self.activityRealmOfTheStrangeEnableCard = SwitchSettingCard1(
            FIF.CALORIES,
            self.tr('启用异器盈界'),
            "存在双倍次数时体力优先「侵蚀隧洞」",
            "activity_realmofthestrange_enable"
        )
        self.activityPlanarFissureEnableCard = SwitchSettingCard1(
            FIF.CALORIES,
            self.tr('启用位面分裂'),
            "存在双倍次数时体力优先「合成沉浸器」",
            "activity_planarfissure_enable"
        )

        self.FightGroup = SettingCardGroup(self.tr("锄大地"), self.scrollWidget)
        self.fightEnableCard = SwitchSettingCard1(
            FIF.BUS,
            self.tr('启用锄大地'),
            "",
            "fight_enable"
        )
        self.fightOperationModeCard = ComboBoxSettingCard2(
            "fight_operation_mode",
            FIF.COMMAND_PROMPT,
            self.tr('运行模式'),
            '',
            texts={'集成': 'exe', '源码': 'source'}
        )
        self.fightTimeoutCard = RangeSettingCard1(
            "fight_timeout",
            [1, 10],
            FIF.HISTORY,
            self.tr("锄大地超时"),
            self.tr("超过设定时间强制停止（单位小时）"),
        )
        self.fightTeamEnableCard = SwitchSettingCard1(
            FIF.EDIT,
            self.tr('自动切换队伍'),
            None,
            "fight_team_enable"
        )
        self.fightTeamNumberCard = ComboBoxSettingCard1(
            "fight_team_number",
            FIF.FLAG,
            self.tr('队伍编号'),
            None,
            texts=['3', '4', '5', '6', '7']
        )
        self.FightRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次运行锄大地的时间"),
            "fight_timestamp"
        )
        self.guiFightCard = PrimaryPushSettingCard(
            self.tr('启动'),
            FIF.SHARE,
            self.tr('原版运行'),
            self.tr('启动调试模式，可以选择指定地图继续锄大地'),
        )
        self.updateFightCard = PrimaryPushSettingCard(
            self.tr('更新'),
            FIF.UPDATE,
            self.tr('更新锄大地 (Fhoe-Rail)'),
            None
        )

        self.UniverseGroup = SettingCardGroup(self.tr("模拟宇宙"), self.scrollWidget)
        self.universeEnableCard = SwitchSettingCard1(
            FIF.VPN,
            self.tr('启用模拟宇宙'),
            "",
            "universe_enable"
        )
        self.universeOperationModeCard = ComboBoxSettingCard2(
            "universe_operation_mode",
            FIF.COMMAND_PROMPT,
            self.tr('运行模式'),
            '',
            texts={'集成': 'exe', '源码': 'source'}
        )
        self.universeTimeoutCard = RangeSettingCard1(
            "universe_timeout",
            [1, 24],
            FIF.HISTORY,
            self.tr("模拟宇宙超时"),
            self.tr("超过设定时间强制停止（单位小时）"),
        )
        self.universeRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次运行模拟宇宙的时间"),
            "universe_timestamp"
        )
        self.universeBonusEnableCard = SwitchSettingCard1(
            FIF.IOT,
            self.tr('领取沉浸奖励'),
            None,
            "universe_bonus_enable"
        )
        self.universeFrequencyCard = ComboBoxSettingCard2(
            "universe_frequency",
            FIF.MINIMIZE,
            self.tr('运行频率'),
            '',
            texts={'每周': 'weekly', '每天': 'daily'}
        )
        self.universeCountCard = RangeSettingCard1(
            "universe_count",
            [0, 34],
            FIF.HISTORY,
            self.tr("运行次数"),
            self.tr("注意中途停止不会计数，0 代表不指定，使用模拟宇宙原版逻辑"),
        )
        self.guiUniverseCard = PrimaryPushSettingCard(
            self.tr('启动'),
            FIF.SHARE,
            self.tr('原版运行'),
            self.tr('启动后可以修改命途和难度等'),
        )
        self.updateUniverseCard = PrimaryPushSettingCard(
            self.tr('更新'),
            FIF.UPDATE,
            self.tr('更新模拟宇宙 (Auto_Simulated_Universe)'),
            None
        )

        self.ForgottenhallGroup = SettingCardGroup(self.tr("忘却之庭"), self.scrollWidget)
        self.forgottenhallEnableCard = SwitchSettingCard1(
            FIF.SPEED_HIGH,
            self.tr('启用混沌回忆'),
            "",
            "forgottenhall_enable"
        )
        self.forgottenhallLevelCard = PushSettingCardEval(
            self.tr('修改'),
            FIF.MINIMIZE,
            self.tr("关卡范围"),
            "forgottenhall_level"
        )
        self.forgottenhallRetriesCard = RangeSettingCard1(
            "forgottenhall_retries",
            [0, 10],
            FIF.REMOVE_FROM,
            self.tr("重试次数"),
        )
        self.forgottenhallTeam1Card = PushSettingCardTeam(
            self.tr('修改'),
            FIF.FLAG,
            self.tr("混沌回忆队伍1"),
            "forgottenhall_team1"
        )
        self.forgottenhallTeam2Card = PushSettingCardTeam(
            self.tr('修改'),
            FIF.FLAG,
            self.tr("混沌回忆队伍2"),
            "forgottenhall_team2"
        )
        self.forgottenhallRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次运行混沌回忆的时间"),
            "forgottenhall_timestamp"
        )

        self.PureFictionGroup = SettingCardGroup(self.tr("虚构叙事"), self.scrollWidget)
        self.purefictionEnableCard = SwitchSettingCard1(
            FIF.SPEED_HIGH,
            self.tr('启用虚构叙事'),
            "",
            "purefiction_enable"
        )
        self.purefictionLevelCard = PushSettingCardEval(
            self.tr('修改'),
            FIF.MINIMIZE,
            self.tr("关卡范围"),
            "purefiction_level"
        )
        self.purefictionTeam1Card = PushSettingCardTeam(
            self.tr('修改'),
            FIF.FLAG,
            self.tr("虚构叙事队伍1"),
            "purefiction_team1"
        )
        self.purefictionTeam2Card = PushSettingCardTeam(
            self.tr('修改'),
            FIF.FLAG,
            self.tr("虚构叙事队伍2"),
            "purefiction_team2"
        )
        self.purefictionRunTimeCard = PushSettingCardDate(
            self.tr('修改'),
            FIF.DATE_TIME,
            self.tr("上次运行虚构叙事的时间"),
            "purefiction_timestamp"
        )

        self.ProgramGroup = SettingCardGroup(self.tr('程序设置'), self.scrollWidget)
        self.logLevelCard = ComboBoxSettingCard2(
            "log_level",
            FIF.TAG,
            self.tr('日志等级'),
            "",
            texts={'简洁': 'INFO', '详细': 'DEBUG'}
        )
        self.importConfigCard = PushSettingCard(
            self.tr('导入'),
            FIF.ADD_TO,
            self.tr('导入配置'),
            self.tr('选择需要导入的 config.yaml 文件（重启后生效）')
        )
        self.checkUpdateCard = SwitchSettingCard1(
            FIF.SYNC,
            self.tr('启动时检测更新'),
            "新版本将更加稳定并拥有更多功能（建议启用）",
            "check_update"
        )
        self.afterFinishCard = ComboBoxSettingCard2(
            "after_finish",
            FIF.POWER_BUTTON,
            self.tr('任务完成后'),
            self.tr('其中“退出”指退出游戏，“循环”指根据开拓力7×24小时无人值守循环运行程序（仅限完整运行生效）'),
            texts={'无': 'None', '退出': 'Exit', '循环': 'Loop',
                   '关机': 'Shutdown', '休眠': 'Hibernate', '睡眠': 'Sleep'}
        )
        self.playAudioCard = SwitchSettingCard1(
            FIF.ALBUM,
            self.tr('声音提示'),
            self.tr('任务完成后列车长唱歌提示帕！'),
            "play_audio"
        )
        self.powerLimitCard = RangeSettingCard1(
            "power_limit",
            [10, 240],
            FIF.HEART,
            # self.tr("循环运行再次启动所需开拓力（游戏刷新后优先级更高）"),
            self.tr("循环运行再次启动所需开拓力"),
            self.tr("游戏刷新后优先级更高"),
        )
        self.refreshHourEnableCard = RangeSettingCard1(
            "refresh_hour",
            [0, 23],
            FIF.DATE_TIME,
            self.tr("游戏刷新时间"),
            self.tr("用于循环运行及判断任务状态，默认凌晨四点"),
        )
        self.gamePathCard = PushSettingCard(
            self.tr('修改'),
            FIF.GAME,
            self.tr("游戏路径"),
            config.game_path
        )

        self.NotifyGroup = SettingCardGroup(self.tr("消息推送"), self.scrollWidget)
        self.testNotifyCard = PrimaryPushSettingCard(
            self.tr('发送消息'),
            FIF.RINGER,
            self.tr("测试消息推送"),
            ""
        )
        self.winotifyEnableCard = SwitchSettingCard1(
            FIF.BACK_TO_WINDOW,
            self.tr('启用 Windows 原生通知'),
            None,
            "notify_winotify_enable"
        )

        self.MiscGroup = SettingCardGroup(self.tr("杂项"), self.scrollWidget)
        self.autoBattleDetectEnableCard = SwitchSettingCard1(
            FIF.ROBOT,
            self.tr('启用自动战斗检测'),
            "只对清体力和忘却之庭场景生效",
            "auto_battle_detect_enable"
        )
        self.autoSetResolutionEnableCard = SwitchSettingCard1(
            FIF.FULL_SCREEN,
            self.tr('启用自动修改分辨率并关闭自动 HDR'),
            "通过软件启动游戏会自动修改 1920x1080 分辨率并关闭自动 HDR，不影响手动启动游戏（未测试国际服）",
            "auto_set_resolution_enable"
        )
        self.autoSetGamePathEnableCard = SwitchSettingCard1(
            FIF.GAME,
            self.tr('启用自动配置游戏路径'),
            "通过快捷方式、官方启动器、运行中的游戏进程等方式尝试自动配置游戏路径（未测试国际服）",
            "auto_set_game_path_enable"
        )
        self.keybindingTechniqueCard = PushSettingCardKey(
            self.tr('按住以修改'),
            FIF.LEAF,
            self.tr("秘技（只对清体力和忘却之庭场景生效）"),
            "hotkey_technique"
        )

        self.AboutGroup = SettingCardGroup(self.tr('关于'), self.scrollWidget)
        self.githubCard = PrimaryPushSettingCard(
            self.tr('项目主页'),
            FIF.GITHUB,
            self.tr('项目主页'),
            "https://github.com/moesnow/March7thAssistant"
        )
        self.qqGroupCard = PrimaryPushSettingCard(
            self.tr('加入群聊'),
            FIF.EXPRESSIVE_INPUT_ENTRY,
            self.tr('QQ群'),
            "855392201"
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('提供反馈'),
            self.tr('帮助我们改进 March7thAssistant')
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.INFO,
            self.tr('关于'),
            self.tr('当前版本：') + " " + config.version
        )
        self.updatePrereleaseEnableCard = SwitchSettingCard1(
            FIF.TRAIN,
            self.tr('加入预览版更新渠道'),
            "",
            "update_prerelease_enable"
        )
        self.updateFullEnableCard = SwitchSettingCard1(
            FIF.GLOBE,
            self.tr('更新时下载完整包'),
            "包含模拟宇宙和锄大地等，但压缩包体积更大",
            "update_full_enable"
        )

    def __initLayout(self):
        self.settingLabel.move(36, 30)
        self.pivot.move(40, 80)
        # self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.stackedWidget, 0, Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)

        self.PowerGroup.addSettingCard(self.instanceTypeCard)
        self.PowerGroup.addSettingCard(self.calyxGoldenPreferenceCard)
        self.PowerGroup.addSettingCard(self.instanceNameCard)
        self.PowerGroup.addSettingCard(self.breakDownLevelFourRelicsetEnableCard)
        self.PowerGroup.addSettingCard(self.instanceTeamEnableCard)
        self.PowerGroup.addSettingCard(self.instanceTeamNumberCard)
        self.PowerGroup.addSettingCard(self.mergeImmersifierEnableCard)
        self.PowerGroup.addSettingCard(self.useReservedTrailblazePowerEnableCard)
        self.PowerGroup.addSettingCard(self.useFuelEnableCard)
        self.PowerGroup.addSettingCard(self.echoofwarEnableCard)
        self.PowerGroup.addSettingCard(self.echoofwarRunTimeCard)

        self.BorrowGroup.addSettingCard(self.borrowEnableCard)
        self.BorrowGroup.addSettingCard(self.borrowCharacterEnableCard)
        self.BorrowGroup.addSettingCard(self.borrowCharacterFromCard)
        self.BorrowGroup.addSettingCard(self.borrowCharacterInfoCard)
        self.BorrowGroup.addSettingCard(self.borrowCharacterCard)

        self.DailyGroup.addSettingCard(self.dispatchEnableCard)
        self.DailyGroup.addSettingCard(self.mailEnableCard)
        self.DailyGroup.addSettingCard(self.assistEnableCard)
        self.DailyGroup.addSettingCard(self.dailyEnableCard)
        self.DailyGroup.addSettingCard(self.dailyHimekoTryEnableCard)
        self.DailyGroup.addSettingCard(self.dailyMemoryOneEnableCard)
        self.DailyGroup.addSettingCard(self.dailyMemoryOneTeamCard)
        self.DailyGroup.addSettingCard(self.lastRunTimeCard)

        self.ActivityGroup.addSettingCard(self.activityEnableCard)
        self.ActivityGroup.addSettingCard(self.activityGiftOfOdysseyEnableCard)
        self.ActivityGroup.addSettingCard(self.activityGiftOfRadianceEnableCard)
        self.ActivityGroup.addSettingCard(self.activityGardenOfPlentyEnableCard)
        self.ActivityGroup.addSettingCard(self.activityGardenOfPlentyTypeCard)
        self.ActivityGroup.addSettingCard(self.activityRealmOfTheStrangeEnableCard)
        self.ActivityGroup.addSettingCard(self.activityPlanarFissureEnableCard)

        self.FightGroup.addSettingCard(self.fightEnableCard)
        self.FightGroup.addSettingCard(self.fightOperationModeCard)
        self.FightGroup.addSettingCard(self.fightTimeoutCard)
        self.FightGroup.addSettingCard(self.fightTeamEnableCard)
        self.FightGroup.addSettingCard(self.fightTeamNumberCard)
        self.FightGroup.addSettingCard(self.FightRunTimeCard)
        self.FightGroup.addSettingCard(self.guiFightCard)
        self.FightGroup.addSettingCard(self.updateFightCard)

        self.UniverseGroup.addSettingCard(self.universeEnableCard)
        self.UniverseGroup.addSettingCard(self.universeOperationModeCard)
        self.UniverseGroup.addSettingCard(self.universeTimeoutCard)
        self.UniverseGroup.addSettingCard(self.universeBonusEnableCard)
        self.UniverseGroup.addSettingCard(self.universeFrequencyCard)
        self.UniverseGroup.addSettingCard(self.universeCountCard)
        self.UniverseGroup.addSettingCard(self.universeRunTimeCard)
        self.UniverseGroup.addSettingCard(self.guiUniverseCard)
        self.UniverseGroup.addSettingCard(self.updateUniverseCard)

        self.ForgottenhallGroup.addSettingCard(self.forgottenhallEnableCard)
        self.ForgottenhallGroup.addSettingCard(self.forgottenhallLevelCard)
        self.ForgottenhallGroup.addSettingCard(self.forgottenhallRetriesCard)
        self.ForgottenhallGroup.addSettingCard(self.forgottenhallTeam1Card)
        self.ForgottenhallGroup.addSettingCard(self.forgottenhallTeam2Card)
        self.ForgottenhallGroup.addSettingCard(self.forgottenhallRunTimeCard)

        self.PureFictionGroup.addSettingCard(self.purefictionEnableCard)
        self.PureFictionGroup.addSettingCard(self.purefictionLevelCard)
        self.PureFictionGroup.addSettingCard(self.purefictionTeam1Card)
        self.PureFictionGroup.addSettingCard(self.purefictionTeam2Card)
        self.PureFictionGroup.addSettingCard(self.purefictionRunTimeCard)

        self.ProgramGroup.addSettingCard(self.logLevelCard)
        self.ProgramGroup.addSettingCard(self.importConfigCard)
        self.ProgramGroup.addSettingCard(self.checkUpdateCard)
        self.ProgramGroup.addSettingCard(self.afterFinishCard)
        self.ProgramGroup.addSettingCard(self.playAudioCard)
        self.ProgramGroup.addSettingCard(self.powerLimitCard)
        self.ProgramGroup.addSettingCard(self.refreshHourEnableCard)
        self.ProgramGroup.addSettingCard(self.gamePathCard)

        self.NotifyGroup.addSettingCard(self.testNotifyCard)
        self.NotifyGroup.addSettingCard(self.winotifyEnableCard)

        self.MiscGroup.addSettingCard(self.autoBattleDetectEnableCard)
        self.MiscGroup.addSettingCard(self.autoSetResolutionEnableCard)
        self.MiscGroup.addSettingCard(self.autoSetGamePathEnableCard)
        self.MiscGroup.addSettingCard(self.keybindingTechniqueCard)

        self.AboutGroup.addSettingCard(self.githubCard)
        self.AboutGroup.addSettingCard(self.qqGroupCard)
        self.AboutGroup.addSettingCard(self.feedbackCard)
        self.AboutGroup.addSettingCard(self.aboutCard)
        self.AboutGroup.addSettingCard(self.updatePrereleaseEnableCard)
        self.AboutGroup.addSettingCard(self.updateFullEnableCard)

        self.addSubInterface(self.PowerGroup, 'PowerInterface', self.tr('体力'))
        self.addSubInterface(self.BorrowGroup, 'BorrowInterface', self.tr('支援'))
        self.addSubInterface(self.DailyGroup, 'DailyInterface', self.tr('日常'))
        self.addSubInterface(self.ActivityGroup, 'ActivityInterface', self.tr('活动'))
        self.addSubInterface(self.FightGroup, 'FightInterface', self.tr('锄大地'))
        self.addSubInterface(self.UniverseGroup, 'UniverseInterface', self.tr('模拟宇宙'))
        self.addSubInterface(self.ForgottenhallGroup, 'ForgottenhallInterface', self.tr('忘却'))
        self.addSubInterface(self.PureFictionGroup, 'PureFictionInterface', self.tr('虚构'))

        self.pivot.addItem(
            routeKey='verticalBar',
            text="|",
            onClick=lambda: self.pivot.setCurrentItem(self.stackedWidget.currentWidget().objectName()),
        )

        self.addSubInterface(self.ProgramGroup, 'programInterface', self.tr('程序'))
        self.addSubInterface(self.NotifyGroup, 'NotifyInterface', self.tr('推送'))
        self.addSubInterface(self.MiscGroup, 'KeybindingInterface', self.tr('杂项'))
        self.addSubInterface(self.AboutGroup, 'AboutInterface', self.tr('关于'))

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.pivot.setCurrentItem(self.stackedWidget.currentWidget().objectName())
        self.stackedWidget.setFixedHeight(self.stackedWidget.currentWidget().sizeHint().height())

    def __connectSignalToSlot(self):
        self.importConfigCard.clicked.connect(self.__onImportConfigCardClicked)
        self.gamePathCard.clicked.connect(self.__onGamePathCardClicked)

        self.borrowCharacterInfoCard.clicked.connect(self.__openCharacterFolder())

        self.guiUniverseCard.clicked.connect(lambda: start_task("universe_gui"))
        self.guiFightCard.clicked.connect(lambda: start_task("fight_gui"))
        self.updateUniverseCard.clicked.connect(lambda: start_task("universe_update"))
        self.updateFightCard.clicked.connect(lambda: start_task("fight_update"))

        self.testNotifyCard.clicked.connect(lambda: start_task("notify"))

        self.githubCard.clicked.connect(self.__openUrl("https://github.com/moesnow/March7thAssistant"))
        self.qqGroupCard.clicked.connect(self.__openUrl("https://qm.qq.com/q/9gFqUrUGVq"))
        self.feedbackCard.clicked.connect(self.__openUrl("https://github.com/moesnow/March7thAssistant/issues"))

        self.aboutCard.clicked.connect(lambda: checkUpdate(self.parent))

    def addSubInterface(self, widget: QLabel, objectName, text):
        def remove_spacing(layout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if isinstance(item, QSpacerItem):
                    layout.removeItem(item)
                    break

        remove_spacing(widget.vBoxLayout)
        widget.titleLabel.setHidden(True)

        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

        self.verticalScrollBar().setValue(0)
        self.stackedWidget.setFixedHeight(self.stackedWidget.currentWidget().sizeHint().height())

    def __onImportConfigCardClicked(self):
        configdir, _ = QFileDialog.getOpenFileName(self, "选取配置文件", "./", "Config Files (*.yaml)")
        if (configdir != ""):
            config._load_config(configdir)
            config.save_config()
            self.__showRestartTooltip()

    def __onGamePathCardClicked(self):
        game_path, _ = QFileDialog.getOpenFileName(self, "选择游戏路径", "", "All Files (*)")
        if not game_path or config.game_path == game_path:
            return
        config.set_value("game_path", game_path)
        self.gamePathCard.setContent(game_path)

    def __openCharacterFolder(self):
        return lambda: os.startfile(os.path.abspath("./assets/images/share/character"))

    def __openUrl(self, url):
        return lambda: QDesktopServices.openUrl(QUrl(url))

    def __showRestartTooltip(self):
        InfoBar.success(
            self.tr('更新成功'),
            self.tr('配置在重启软件后生效'),
            duration=1500,
            parent=self
        )
