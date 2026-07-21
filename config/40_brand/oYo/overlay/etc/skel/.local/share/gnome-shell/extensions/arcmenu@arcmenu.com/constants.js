import {domain} from 'gettext';
const {gettext: _} = domain('arcmenu');

export const DASH_TO_PANEL_UUID = 'dash-to-panel@jderose9.github.com';
export const AZTASKBAR_UUID = 'aztaskbar@aztaskbar.gitlab.com';
export const RESOURCE_PATH = 'resource:///org/gnome/shell/extensions/arcmenu/icons/scalable';

export const ClutterAction = {
    CLICK: 0,
    PAN: 1,
};

export const SearchbarLocation = {
    BOTTOM: 0,
    TOP: 1,
};

export const MenuItemLocation = {
    BOTTOM: 0,
    TOP: 1,
};

export const DisplayType = {
    LIST: 0,
    GRID: 1,
    BUTTON: 2,
};

export const AvatarStyle = {
    ROUND: 0,
    SQUARE: 1,
};

export const CategoryType = {
    FAVORITES: 0,
    FREQUENT_APPS: 1,
    ALL_PROGRAMS: 2,
    PINNED_APPS: 3,
    RECENT_FILES: 4,
    HOME_SCREEN: 5,
    SEARCH_RESULTS: 6,
    CATEGORIES_LIST: 7,
};

export const DefaultMenuView = {
    PINNED_APPS: 0,
    CATEGORIES_LIST: 1,
    FREQUENT_APPS: 2,
    ALL_PROGRAMS: 3,
    PINNED_AND_FREQUENT_APPS: 4,
};

export const SettingsPage = {
    MAIN: 0,
    MENU_LAYOUT: 1,
    BUTTON_APPEARANCE: 2,
    LAYOUT_TWEAKS: 3,
    ABOUT: 4,
    CUSTOMIZE_MENU: 5,
    RUNNER_TWEAKS: 6,
    GENERAL: 7,
    MENU_THEME: 8,
    DIRECTORY_SHORTCUTS: 9,
    APPLICATION_SHORTCUTS: 10,
    SEARCH_OPTIONS: 11,
    POWER_OPTIONS: 12,
    EXTRA_CATEGORIES: 13,
    PINNED_APPS: 14,
    DONATE: 15,
    WHATS_NEW: 16,
};

export const AllAppsButtonAction = {
    CATEGORIES_LIST: 0,
    ALL_PROGRAMS: 1,
};

export const SoftwareManagerIDs = ['org.manjaro.pamac.manager.desktop', 'pamac-manager.desktop',
    'io.elementary.appcenter.desktop', 'snap-store_ubuntu-software.desktop', 'snap-store_snap-store.desktop',
    'org.gnome.Software.desktop', 'tr.org.pardus.software.desktop'];

export const Categories = [
    {CATEGORY: CategoryType.FAVORITES, NAME: _('Favorites'), IMAGE: 'emote-love-symbolic'},
    {CATEGORY: CategoryType.FREQUENT_APPS, NAME: _('Frequent Apps'), IMAGE: 'user-bookmarks-symbolic'},
    {CATEGORY: CategoryType.ALL_PROGRAMS, NAME: _('All Apps'), IMAGE: 'view-app-grid-symbolic'},
    {CATEGORY: CategoryType.PINNED_APPS, NAME: _('Pinned Apps'), IMAGE: 'view-pin-symbolic'},
    {CATEGORY: CategoryType.RECENT_FILES, NAME: _('Recent Files'), IMAGE: 'document-open-recent-symbolic'},
];

export const TooltipLocation = {
    TOP_CENTERED: 0,
    BOTTOM_CENTERED: 1,
    BOTTOM: 2,
};

export const ContextMenuLocation = {
    DEFAULT: 0,
    BOTTOM_CENTERED: 1,
    RIGHT: 2,
};

export const SeparatorAlignment = {
    VERTICAL: 0,
    HORIZONTAL: 1,
};

export const SeparatorStyle = {
    SHORT: 0,
    MEDIUM: 1,
    LONG: 2,
    MAX: 3,
    HEADER_LABEL: 4,
    NORMAL: 5,
    EMPTY: 6,
};

export const CaretPosition = {
    END: -1,
    START: 0,
    MIDDLE: 2,
};

export const CategoryIconType = {
    FULL_COLOR: 0,
    SYMBOLIC: 1,
};

export const MenuLocation = {
    OFF: 0,
    TOP_CENTERED: 1,
    TOP_LEFT: 2,
    TOP_RIGHT: 3,
    BOTTOM_CENTERED: 4,
    BOTTOM_LEFT: 5,
    BOTTOM_RIGHT: 6,
    LEFT_CENTERED: 7,
    RIGHT_CENTERED: 8,
    MONITOR_CENTERED: 9,
};

export const IconSize = {
    DEFAULT: 0,
    EXTRA_SMALL: 1,
    SMALL: 2,
    MEDIUM: 3,
    LARGE: 4,
    EXTRA_LARGE: 5,
    HIDDEN: 6,
};

export const GridIconSize = {
    DEFAULT: 0,
    SMALL: 1,
    MEDIUM: 2,
    LARGE: 3,
    SMALL_RECT: 4,
    MEDIUM_RECT: 5,
    LARGE_RECT: 6,
    CUSTOM: 7,
    EXTRA_LARGE: 8,
};

export const GridIconInfo = [
    {ENUM: GridIconSize.SMALL, WIDTH: 80, HEIGHT: 80, ICON_SIZE: 36},
    {ENUM: GridIconSize.MEDIUM, WIDTH: 87, HEIGHT: 87, ICON_SIZE: 42},
    {ENUM: GridIconSize.LARGE, WIDTH: 95, HEIGHT: 95, ICON_SIZE: 52},
    {ENUM: GridIconSize.SMALL_RECT, WIDTH: 85, HEIGHT: 70, ICON_SIZE: 28},
    {ENUM: GridIconSize.MEDIUM_RECT, WIDTH: 92, HEIGHT: 78, ICON_SIZE: 34},
    {ENUM: GridIconSize.LARGE_RECT, WIDTH: 95, HEIGHT: 85, ICON_SIZE: 42},
    {ENUM: GridIconSize.EXTRA_LARGE, WIDTH: 148, HEIGHT: 148, ICON_SIZE: 68},
];

export const ICON_HIDDEN = 0;
export const EXTRA_SMALL_ICON_SIZE = 16;
export const SMALL_ICON_SIZE = 20;
export const MEDIUM_ICON_SIZE = 25;
export const LARGE_ICON_SIZE = 30;
export const EXTRA_LARGE_ICON_SIZE = 35;
export const MISC_ICON_SIZE = 24;

export const SUPER_L = 'Super_L';
export const SUPER_R = 'Super_R';
export const SUPER = 'Super';

export const SECTIONS = [
    'devices',
    'network',
    'bookmarks',
];

export const Direction = {
    GO_NEXT: 0,
    GO_PREVIOUS: 1,
};

export const MenuPosition = {
    LEFT: 0,
    CENTER: 1,
    RIGHT: 2,
};

export const RavenPosition = {
    LEFT: 0,
    RIGHT: 1,
};

export const DiaglogType = {
    DEFAULT: 0,
    OTHER: 1,
    APPLICATIONS: 2,
    DIRECTORIES: 3,
};

export const MenuSettingsListType = {
    PINNED_APPS: 0,
    APPLICATIONS: 1,
    DIRECTORIES: 2,
    EXTRA_SHORTCUTS: 3,
    POWER_OPTIONS: 4,
    EXTRA_CATEGORIES: 5,
    QUICK_LINKS: 6,
    CONTEXT_MENU: 7,
    FOLDER_PINNED_APPS: 8,
};

export const MenuButtonAppearance = {
    ICON: 0,
    TEXT: 1,
    ICON_TEXT: 2,
    TEXT_ICON: 3,
    NONE: 4,
};

export const MenuButtonClickAction = {
    ARCMENU: 0,
    CONTEXT_MENU: 1,
    NONE: 2,
};

export const PowerType = {
    LOGOUT: 0,
    LOCK: 1,
    RESTART: 2,
    POWER_OFF: 3,
    SUSPEND: 4,
    HYBRID_SLEEP: 5,
    HIBERNATE: 6,
    SWITCH_USER: 7,
};

export const PowerDisplayStyle = {
    DEFAULT: 0,
    IN_LINE: 1,
    MENU: 2,
};

export const PowerOptions = [
    {TYPE: PowerType.LOGOUT, IMAGE: 'system-log-out-symbolic', NAME: _('Log Out...')},
    {TYPE: PowerType.LOCK, IMAGE: 'changes-prevent-symbolic', NAME: _('Lock')},
    {TYPE: PowerType.RESTART, IMAGE: 'system-reboot-symbolic', NAME: _('Restart...')},
    {TYPE: PowerType.POWER_OFF, IMAGE: 'system-shutdown-symbolic', NAME: _('Power Off...')},
    {TYPE: PowerType.SUSPEND, IMAGE: 'media-playback-pause-symbolic', NAME: _('Suspend')},
    {TYPE: PowerType.HYBRID_SLEEP, IMAGE: 'weather-clear-night-symbolic', NAME: _('Hybrid Sleep')},
    {TYPE: PowerType.HIBERNATE, IMAGE: 'document-save-symbolic', NAME: _('Hibernate')},
    {TYPE: PowerType.SWITCH_USER, IMAGE: 'system-switch-user-symbolic', NAME: _('Switch User')},
];

export const LayoutCategoriesInfo = [
    {id: 'traditional', title: _('Traditional'), image: 'menustyle-traditional-symbolic'},
    {id: 'modern',      title: _('Modern'),      image: 'menustyle-modern-symbolic'},
    {id: 'touch',       title: _('Touch'),       image: 'menustyle-touch-symbolic'},
    {id: 'launcher',    title: _('Launcher'),    image: 'menustyle-launcher-symbolic'},
    {id: 'alternative', title: _('Alternative'), image: 'menustyle-alternative-symbolic'},
];

export const MenuLayoutsInfo = [
    {id: 'arcmenu',        title: _('ArcMenu'),        category: 'traditional'},
    {id: 'brisk',          title: _('Brisk'),          category: 'traditional'},
    {id: 'budgie',         title: _('Budgie'),         category: 'traditional'},
    {id: 'gnome-menu',     title: _('GNOME Menu'),     category: 'traditional'},
    {id: 'mint',           title: _('Mint'),           category: 'traditional'},
    {id: 'whisker',        title: _('Whisker'),        category: 'traditional'},
    {id: '11',             title: _('11'),             category: 'modern'},
    {id: 'az',             title: _('a.z.'),           category: 'modern'},
    {id: 'enterprise',     title: _('Enterprise'),     category: 'modern'},
    {id: 'insider',        title: _('Insider'),        category: 'modern'},
    {id: 'plasma',         title: _('Plasma'),         category: 'modern'},
    {id: 'pop',            title: _('Pop'),            category: 'modern'},
    {id: 'redmond',        title: _('Redmond'),        category: 'modern'},
    {id: 'sleek',          title: _('Sleek'),          category: 'modern'},
    {id: 'tognee',         title: _('tognee'),         category: 'modern'},
    {id: 'unity',          title: _('Unity'),          category: 'modern'},
    {id: 'windows',        title: _('Windows'),        category: 'modern'},
    {id: 'zest',           title: _('Zest'),           category: 'modern'},
    {id: 'chromebook',     title: _('Chromebook'),     category: 'touch'},
    {id: 'elementary',     title: _('Elementary'),     category: 'touch'},
    {id: 'gnome-overview', title: _('GNOME Overview'), category: 'launcher'},
    {id: 'runner',         title: _('Runner'),         category: 'launcher'},
    {id: 'raven',          title: _('Raven'),          category: 'alternative'},
];

export const ArcMenuLogoSymbolic = 'arcmenu-logo-symbolic';

export const TranslatableSettingsStrings = [_('Software'), _('Settings'), _('Tweaks'), _('Terminal'),
    _('Activities Overview'), _('ArcMenu Settings'), _('Files')];

export const ShortcutCommands = {
    SUSPEND: 'ArcMenu_Suspend',
    LOG_OUT: 'ArcMenu_LogOut',
    POWER_OFF: 'ArcMenu_PowerOff',
    LOCK: 'ArcMenu_Lock',
    RESTART: 'ArcMenu_Restart',
    HYBRID_SLEEP: 'ArcMenu_HybridSleep',
    HIBERNATE: 'ArcMenu_Hibernate',
    SWITCH_USER: 'ArcMenu_SwitchUser',
    COMPUTER: 'ArcMenu_Computer',
    NETWORK: 'ArcMenu_Network',
    RECENT: 'ArcMenu_Recent',
    SOFTWARE: 'ArcMenu_Software',
    HOME: 'ArcMenu_Home',
    DOCUMENTS: 'ArcMenu_Documents',
    DOWNLOADS: 'ArcMenu_Downloads',
    MUSIC: 'ArcMenu_Music',
    PICTURES: 'ArcMenu_Pictures',
    VIDEOS: 'ArcMenu_Videos',
    ARCMENU_SETTINGS: 'gnome-extensions prefs arcmenu@arcmenu.com',
    FOLDER: 'ArcMenu_Folder',
    OVERVIEW: 'ArcMenu_ActivitiesOverview',
    SHOW_APPS: 'ArcMenu_ShowAllApplications',
    RUN_COMMAND: 'ArcMenu_RunCommand',
    SEPARATOR: 'ArcMenu_Separator',
    SPACER: 'ArcMenu_Spacer',
    SETTINGS: 'ArcMenu_Settings',
    SHOW_DESKTOP: 'ArcMenu_ShowDesktop',
    POWER_OPTIONS: 'ArcMenu_PowerOptions',
    SETTINGS_MENU: 'ArcMenu_SettingsMenu',
    SETTINGS_LAYOUT: 'ArcMenu_SettingsLayout',
    SETTINGS_BUTTON: 'ArcMenu_SettingsButton',
    SETTINGS_ABOUT: 'ArcMenu_SettingsAbout',
    SETTINGS_THEME: 'ArcMenu_SettingsTheme',
    PANEL_EXTENSION_SETTINGS: 'ArcMenu_PanelExtensionSettings',
    ARCMENU_ICON: 'ArcMenu_ArcMenuIcon',
};
