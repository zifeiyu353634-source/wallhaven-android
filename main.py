"""
Wallhaven 壁纸浏览器 - Kivy 安卓版
作者：夜辰
版本：1.0
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import json
import os
# 设置窗口大小（PC调试用）
Window.size = (400, 700)
class WallhavenApp(App):
    """Wallhaven 壁纸浏览器主应用"""
    
    def build(self):
        self.title = "Wallhaven 壁纸浏览器"
        self.wallpapers = []
        self.current_page = 1
        self.total_pages = 1
        self.api_key = ""
        self.load_config()
        return self.build_ui()
    
    def load_config(self):
        """加载配置"""
        config_file = os.path.join(self.user_data_dir, 'config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
            except:
                pass
    
    def save_config(self):
        """保存配置"""
        config_file = os.path.join(self.user_data_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump({'api_key': self.api_key}, f)
    
    def build_ui(self):
        """构建主界面"""
        # 主布局
        root = BoxLayout(orientation='vertical', padding=5, spacing=5)
        root.canvas.before.add(Color(0.1, 0.1, 0.15, 1))
        root.canvas.before.add(Rectangle(size=root.size, pos=root.pos))
        
        # 顶部栏
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        # 搜索框
        self.search_input = TextInput(
            hint_text='搜索关键词...',
            multiline=False,
            size_hint_x=0.7,
            background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        top_bar.add_widget(self.search_input)
        
        # 搜索按钮
        search_btn = Button(
            text='🔍',
            size_hint_x=0.15,
            background_color=(0.4, 0.4, 0.9, 1)
        )
        search_btn.bind(on_press=self.search)
        top_bar.add_widget(search_btn)
        
        # 设置按钮
        settings_btn = Button(
            text='⚙️',
            size_hint_x=0.15,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        settings_btn.bind(on_press=self.show_settings)
        top_bar.add_widget(settings_btn)
        
        root.add_widget(top_bar)
        
        # 筛选栏
        filter_bar = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        # 排序选择
        self.sort_spinner = Spinner(
            text='最新添加',
            values=['最新添加', '最多浏览', '最多收藏', '随机'],
            size_hint_x=0.33
        )
        filter_bar.add_widget(self.sort_spinner)
        
        # 分辨率选择
        self.res_spinner = Spinner(
            text='全部分辨率',
            values=['全部分辨率', '4K', '2K', '1080p'],
            size_hint_x=0.33
        )
        filter_bar.add_widget(self.res_spinner)
        
        # 分类选择
        self.cat_spinner = Spinner(
            text='全部分类',
            values=['全部分类', '人物', '风景', '动漫'],
            size_hint_x=0.34
        )
        filter_bar.add_widget(self.cat_spinner)
        
        root.add_widget(filter_bar)
        
        # 图片网格（可滚动）
        self.scroll = ScrollView()
        self.gallery = GridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        self.gallery.bind(minimum_height=self.gallery.setter('height'))
        self.scroll.add_widget(self.gallery)
        root.add_widget(self.scroll)
        
        # 底部栏
        bottom_bar = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        self.prev_btn = Button(
            text='⬅ 上一页',
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.prev_btn.bind(on_press=self.prev_page)
        bottom_bar.add_widget(self.prev_btn)
        
        self.page_label = Label(
            text='第 1 页',
            size_hint_x=0.4
        )
        bottom_bar.add_widget(self.page_label)
        
        self.next_btn = Button(
            text='下一页 ➡',
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.next_btn.bind(on_press=self.next_page)
        bottom_bar.add_widget(self.next_btn)
        
        root.add_widget(bottom_bar)
        
        # 加载初始数据
        Clock.schedule_once(lambda dt: self.search(None), 0.5)
        
        return root
    
    def search(self, instance):
        """搜索壁纸"""
        query = self.search_input.text.strip()
        sort_map = {
            '最新添加': 'date_added',
            '最多浏览': 'views',
            '最多收藏': 'favorites',
            '随机': 'random'
        }
        sorting = sort_map.get(self.sort_spinner.text, 'date_added')
        
        # 构建URL
        url = f"https://wallhaven.cc/api/v1/search?page={self.current_page}&sorting={sorting}"
        if query:
            url += f"&q={query}"
        
        # 分辨率筛选
        res_map = {
            '4K': '3840x2160',
            '2K': '2560x1440',
            '1080p': '1920x1080'
        }
        if self.res_spinner.text in res_map:
            url += f"&resolutions={res_map[self.res_spinner.text]}"
        
        # 分类筛选
        cat_map = {
            '人物': '100',
            '风景': '010',
            '动漫': '001'
        }
        if self.cat_spinner.text in cat_map:
            url += f"&categories={cat_map[self.cat_spinner.text]}"
        
        headers = {'User-Agent': 'WallhavenApp/1.0'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        UrlRequest(
            url,
            on_success=self.on_search_success,
            on_failure=self.on_search_failure,
            req_headers=headers,
            timeout=30
        )
    
    def on_search_success(self, request, result):
        """搜索成功回调"""
        if isinstance(result, str):
            result = json.loads(result)
        
        self.gallery.clear_widgets()
        self.wallpapers = result.get('data', [])
        meta = result.get('meta', {})
        self.total_pages = meta.get('last_page', 1)
        
        if not self.wallpapers:
            self.gallery.add_widget(Label(
                text='😔 未找到壁纸',
                size_hint_y=None,
                height=100
            ))
            return
        
        for wp in self.wallpapers:
            card = self.create_card(wp)
            self.gallery.add_widget(card)
        
        self.update_pagination()
    
    def on_search_failure(self, request, error):
        """搜索失败回调"""
        self.gallery.clear_widgets()
        self.gallery.add_widget(Label(
            text=f'❌ 加载失败: {error}',
            size_hint_y=None,
            height=100,
            color=(1, 0.3, 0.3, 1)
        ))
    
    def create_card(self, wp):
        """创建壁纸卡片"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=220,
            spacing=5
        )
        card.canvas.before.add(Color(0.2, 0.2, 0.25, 1))
        from kivy.graphics import RoundedRectangle
        card.canvas.before.add(RoundedRectangle(
            size=card.size,
            pos=card.pos,
            radius=[10]
        ))
        
        # 缩略图
        thumb = Image(
            source=wp.get('thumbs', {}).get('small', ''),
            allow_stretch=True,
            keep_ratio=False,
            size_hint_y=0.8
        )
        card.add_widget(thumb)
        
        # 信息栏
        info = BoxLayout(size_hint_y=0.2)
        
        purity = wp.get('purity', '100')
        purity_text = 'SFW' if purity == '100' else ('Sketchy' if purity == '010' else 'NSFW')
        purity_color = {
            'SFW': (0.2, 0.8, 0.3, 1),
            'Sketchy': (0.9, 0.6, 0.1, 1),
            'NSFW': (0.9, 0.3, 0.3, 1)
        }.get(purity_text, (1, 1, 1, 1))
        
        purity_label = Label(
            text=purity_text,
            color=purity_color,
            size_hint_x=0.5,
            font_size='12sp'
        )
        info.add_widget(purity_label)
        
        res_label = Label(
            text=wp.get('resolution', 'N/A'),
            size_hint_x=0.5,
            font_size='12sp'
        )
        info.add_widget(res_label)
        
        card.add_widget(info)
        
        # 绑定点击事件
        card.bind(on_touch_down=lambda instance, touch: 
                  self.open_preview(wp) if instance.collide_point(*touch.pos) else None)
        
        return card
    
    def open_preview(self, wp):
        """打开预览"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # 图片
        preview_img = Image(
            source=wp.get('path', ''),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.7
        )
        content.add_widget(preview_img)
        
        # 信息
        info_text = f"分辨率: {wp.get('resolution', 'N/A')}\n分类: {wp.get('category', 'N/A')}"
        content.add_widget(Label(
            text=info_text,
            size_hint_y=0.1,
            font_size='14sp'
        ))
        
        # 按钮栏
        btn_bar = BoxLayout(size_hint_y=0.15, spacing=10)
        
        download_btn = Button(
            text='💾 下载',
            background_color=(0.3, 0.7, 0.3, 1)
        )
        download_btn.bind(on_press=lambda x: self.download_wallpaper(wp))
        btn_bar.add_widget(download_btn)
        
        close_btn = Button(
            text='✖ 关闭',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        btn_bar.add_widget(close_btn)
        
        content.add_widget(btn_bar)
        
        popup = Popup(
            title='图片预览',
            content=content,
            size_hint=(0.95, 0.95)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def download_wallpaper(self, wp):
        """下载壁纸"""
        from android.storage import app_storage_path
        from android.permissions import request_permissions, Permission
        
        # 请求权限
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
        
        url = wp.get('path', '')
        filename = f"wallhaven_{wp.get('id', 'unknown')}.{url.split('.')[-1]}"
        
        # 下载文件
        download_path = os.path.join('/sdcard/Download/', filename)
        UrlRequest(
            url,
            on_success=lambda req, res: self.save_file(download_path, res),
            on_failure=lambda req, err: print(f"下载失败: {err}"),
            file_path=download_path
        )
    
    def save_file(self, path, data):
        """保存文件"""
        print(f"已保存到: {path}")
    
    def show_settings(self, instance):
        """显示设置"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(
            text='API Key (可选)',
            size_hint_y=None,
            height=30
        ))
        
        api_input = TextInput(
            text=self.api_key,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=40
        )
        content.add_widget(api_input)
        
        content.add_widget(Label(
            text='提示: 配置 API Key 后可访问 Sketchy 和 NSFW 内容',
            size_hint_y=None,
            height=30,
            font_size='12sp'
        ))
        
        btn_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        save_btn = Button(
            text='保存',
            background_color=(0.3, 0.7, 0.3, 1)
        )
        btn_bar.add_widget(save_btn)
        
        cancel_btn = Button(
            text='取消',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        btn_bar.add_widget(cancel_btn)
        
        content.add_widget(btn_bar)
        
        popup = Popup(
            title='设置',
            content=content,
            size_hint=(0.9, 0.5)
        )
        
        def save_settings(instance):
            self.api_key = api_input.text.strip()
            self.save_config()
            popup.dismiss()
        
        save_btn.bind(on_press=save_settings)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_pagination(self):
        """更新分页"""
        self.page_label.text = f'第 {self.current_page} / {self.total_pages} 页'
        self.prev_btn.disabled = self.current_page <= 1
        self.next_btn.disabled = self.current_page >= self.total_pages
    
    def prev_page(self, instance):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.search(None)
    
    def next_page(self, instance):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.search(None)
if __name__ == '__main__':
    WallhavenApp().run()