import sys
import requests
import json
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.core.window import Window

# --- تسجيل الخط العربي كخط افتراضي للتطبيق بالكامل ---
font_path = "C:\\Windows\\Fonts\\arial.ttf"
if not os.path.exists(font_path):
    font_path = "C:\\Windows\\Fonts\\tahoma.ttf"
LabelBase.register(name="Roboto", fn_regular=font_path)

import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# ==================== إعدادات الـ Theme الاحترافي ====================
THEME = {
    "primary": (0.07, 0.13, 0.22, 1),      # كحلي داكن فاخر
    "primary_light": (0.12, 0.23, 0.35, 1),# كحلي متوسط
    "accent": (1, 0.64, 0, 1),             # برتقالي ذهبي للـ VIP واللمسات الهامة
    "success": (0.15, 0.68, 0.37, 1),      # أخضر هادئ للنجاح والاشتراكات
    "danger": (0.85, 0.25, 0.25, 1),       # أحمر للتنبيهات والأخطاء
    "background": (0.96, 0.97, 0.99, 1),   # خلفية بيضاء مائلة للزرقة مريحة جداً
    "text_dark": (0.1, 0.1, 0.15, 1),      # لون النصوص الأساسية
    "text_light": (1, 1, 1, 1),            # لون النصوص على الخلفيات الداكنة
    "card_bg": (1, 1, 1, 1)                # لون خلفية الكروت الأبيض النقي
}

# ==================== إعدادات ربط Firebase ====================
FIREBASE_API_KEY = "AIzaSyCbQuTInjwiKuuSk_IV40tRZlLr8dupnww"
FIREBASE_APP_ID = "1:435767354076:web:a042fd33e335fe116a8a19" 
# =============================================================

# =========================================================================
# قاعدة بيانات المناهج والاشتراكات (البيانات الثابتة المؤقتة حتى نربط Firestore)
# =========================================================================
CURRICULUM_DATA = {
    "السنة الأولى (L1)": {
        "ST LMD (علوم وتكنولوجيا)": {
            "الفصل الأول (S1)": ["التحليل الرياضي 1 (Analyse)", "الجبر 1 (Algèbre)", "فيزياء 1 (ميكانيك)", "كيمياء 1 (بنية المادة)", "إعلام آلي 1 (برمجة)", "أخلاق وآداب المهنة الجامعية (Ethique)"],
            "الفصل الثاني (S2)": ["التحليل الرياضي 2", "الجبر 2", "فيزياء 2 (كهرباء)", "كيمياء 2 (ترموديناميك)", "إعلام آلي 2"]
        },
        "ST ENG (هندسة تطبيقية)": {
            "الفصل الأول (S1)": ["التحليل الهندسي 1", "الرسم الصناعي والتكنولوجي", "فيزياء هندسية 1", "كيمياء تطبيقية", "إعلام آلي وتصميم برمجيات", "لغة إنجليزية تقنية"],
            "الفصل الثاني (S2)": ["التحليل الهندسي 2", "ميكانيك مطبقة", "كهرباء عامة", "ورشات تطبيقية", "أخلاق المهنة لمهندسين"]
        },
        "SM (علوم المادة)": {
            "الفصل الأول (S1)": ["بنية المادة (Chimie 1)", "ميكانيك النقطة المادية (Physique 1)", "رياضيات 1", "إعلام آلي 1", "تاريخ العلوم", "لغة فرنسية/إنجليزية"],
            "الفصل الثاني (S2)": ["ترموديناميك وحركية كيميائية", "الكهرباء المغناطيسية", "رياضيات 2", "إعلام آلي 2", "منهجية البحث العلمي"]
        },
        "MI Math/Info (رياضيات وإعلام آلي)": {
            "الفصل الأول (S1)": ["تحليل 1", "جبر 1", "خوارزميات وبنية معطيات 1 (ASD)", "هيكلة الآلة 1 (Machine)", "فيزياء 1 (كهرباء)", "لغة إنجليزية", "تكنولوجيا الويب والاتصال"],
            "الفصل الثاني (S2)": ["تحليل 2", "جبر 2", "خوارزميات وبنية معطيات 2", "هيكلة الآلة 2", "فيزياء 2 (ميكانيك)", "أخلاق العلم والعمل"]
        }
    },
    "السنة الثانية (L2)": {
        "ST LMD (علوم وتكنولوجيا)": {
            "الفصل الأول (S3)": ["رياضيات 3 (تحليل مركب)", "ميكانيك عقلانية", "احتمالات وإحصاء", "إلكترونيات أساسية", "مقاومة المواد (RDM)"],
            "الفصل الثاني (S4)": ["رياضيات 4", "ديناميك الحرارة", "إلكتروتقني عام", "مستشعرات وقياسات", "ثقافة مقاولاتية"]
        }
    }
}

# الجلسة المؤقتة لحفظ اختيارات الطالب ومستوى حسابه (مع تفعيل نظام الحفظ التلقائي لاحقاً)
USER_SESSION = {
    "selected_year": "",
    "selected_track": "",
    "selected_semester": "",
    "selected_subject": "",
    "selected_section": "",  # دروس، مجلات، اختبارات
    "user_email": "",        # فارغ حتى يسجل الدخول
    "id_token": "",          # رمز الجلسة الآمن من Firebase
    "is_vip": False          # حالة الاشتراك VIP
}

# =========================================================================
# نافذة تنبيه مخصصة واحترافية جداً تليق بالمتجر
# =========================================================================
def show_custom_popup(title, message, is_warning=False):
    content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
    # أيقونة تعبيرية ترفع من جمالية التنبيه
    status_icon = "⚠️" if is_warning else "✨"
    
    msg_lbl = Label(
        text=ar(f"{status_icon} {message}"),
        font_size='15sp',
        color=THEME["text_dark"] if not is_warning else THEME["danger"],
        halign='center',
        valign='middle',
        size_hint_y=0.7
    )
    msg_lbl.bind(size=msg_lbl.setter('text_size'))
    
    close_btn = Button(
        text=ar("حسناً، فهمت"),
        size_hint=(1, 0.3),
        background_normal='',
        background_color=THEME["primary_light"] if not is_warning else THEME["danger"],
        color=THEME["text_light"],
        bold=True
    )
    
    content.add_widget(msg_lbl)
    content.add_widget(close_btn)
    
    popup = Popup(
        title=ar(title),
        content=content,
        size_hint=(0.85, 0.35),
        auto_dismiss=False,
        background_color=(1, 1, 1, 1)
    )
    
    with popup.canvas.before:
        Color(0.98, 0.98, 0.99, 1)
        Rectangle(pos=popup.pos, size=popup.size)
    
    close_btn.bind(on_release=popup.dismiss)
    popup.open()


# =========================================================================
# الكرت المحسن والمستقر مع ميزة اللمس التفاعلي
# =========================================================================
class CourseCard(BoxLayout):
    def __init__(self, title_text, sub_text, bg_color=None, on_release_callback=None, **kwargs):
        super(CourseCard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 5
        self.bg_color = bg_color if bg_color else THEME["card_bg"]
        self.on_release_callback = on_release_callback
        
        self.title_label = Label(
            text=ar(title_text),
            font_size='16sp',
            bold=True,
            color=THEME["text_dark"],
            halign='center',
            valign='middle',
            size_hint=(1, 0.6)
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        
        self.sub_label = Label(
            text=ar(sub_text),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.4)
        )
        self.sub_label.bind(size=self.sub_label.setter('text_size'))
        
        self.add_widget(self.title_label)
        self.add_widget(self.sub_label)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # إضافة ظل خفيف للكروت يعطي عمقاً بصرياً (Shadow effect)
            Color(0.1, 0.1, 0.15, 0.06)
            RoundedRectangle(pos=(self.x - 1, self.y - 3), size=(self.width + 2, self.height + 4), radius=[14])
            # الخلفية الأساسية للكارت
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            # حدود دقيقة وأنيقة للكارت
            Color(0.88, 0.90, 0.94, 1)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 12), width=1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # تغيير لون الخلفية مؤقتاً عند اللمس لإعطاء إحساس بالتفاعل (Ripple feedback)
            self.bg_color = (0.92, 0.95, 0.98, 1)
            self.update_canvas()
            return True
        return super(CourseCard, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.bg_color = THEME["card_bg"]
            self.update_canvas()
            if self.on_release_callback:
                self.on_release_callback()
            return True
        return super(CourseCard, self).on_touch_up(touch)


# =========================================================================
# شريط التنقل العلوي الموحد والأنيق
# =========================================================================
class TopNavBar(BoxLayout):
    def __init__(self, title, show_back=False, back_target=None, manager=None, **kwargs):
        super(TopNavBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = [15, 10]
        self.spacing = 10
        
        with self.canvas.before:
            Color(*THEME["primary"])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0, 0, 16, 16])
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        if show_back and back_target and manager:
            back_btn = Button(
                text=ar("رجوع ←"),
                font_size='13sp',
                bold=True,
                size_hint_x=None,
                width=80,
                background_normal='',
                background_color=(1, 1, 1, 0.12),
                color=THEME["text_light"]
            )
            back_btn.bind(on_release=lambda x: setattr(manager, 'current', back_target))
            self.add_widget(back_btn)
            
        title_lbl = Label(
            text=ar(title),
            font_size='17sp',
            bold=True,
            color=THEME["text_light"],
            halign='right',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        self.add_widget(title_lbl)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


# =========================================================================
# الشاشة الأساسية للتطبيق التي ترث منها بقية الواجهات لتفادي تكرار الكود
# =========================================================================
class AppScreen(Screen):
    def __init__(self, **kwargs):
        super(AppScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*THEME["background"])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


# =========================================================================
# 1. شاشة البداية والتحميل (Splash Screen مع لوغو نبضي متحرك)
# =========================================================================
class SplashScreen(AppScreen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.angle = 0
        self.pulse_val = 110
        self.pulse_dir = 1.2
        
    def on_enter(self, *args):
        self.clear_widgets()
        self.layout = FloatLayout()
        
        self.logo_widget = Widget(size_hint=(None, None), size=(200, 200), pos_hint={'center_x': 0.5, 'center_y': 0.55})
        self.logo_widget.bind(pos=self.draw_animated_logo, size=self.draw_animated_logo)
        
        self.title = Label(
            text=ar("منصة MT الأكاديمية"),
            font_size='24sp',
            bold=True,
            color=THEME["primary"],
            pos_hint={'center_x': 0.5, 'center_y': 0.38}
        )
        
        self.layout.add_widget(self.logo_widget)
        self.layout.add_widget(self.title)
        self.add_widget(self.layout)
        
        self.anim_event = Clock.schedule_interval(self.update_animation, 1/60.0)
        Clock.schedule_once(lambda dt: self.end_splash(), 2.5)
        
    def draw_animated_logo(self, *args):
        self.logo_widget.canvas.clear()
        with self.logo_widget.canvas:
            # الهالة الخارجية النبضية
            Color(0.07, 0.13, 0.22, 0.1)
            Ellipse(pos=(self.logo_widget.center_x - self.pulse_val/2, self.logo_widget.center_y - self.pulse_val/2), 
                    size=(self.pulse_val, self.pulse_val))
            # الدائرة الداخلية الثابتة والصلبة
            Color(*THEME["primary"])
            Ellipse(pos=(self.logo_widget.center_x - 70, self.logo_widget.center_y - 70), size=(140, 140))
            # الحلقة الدوارة الذهبية (تأثير التحميل الاحترافي)
            Color(*THEME["accent"])
            Line(ellipse=(self.logo_widget.center_x - 70, self.logo_widget.center_y - 70, 140, 140, self.angle, self.angle + 110), width=3)
            
        if not hasattr(self, 'logo_text'):
            self.logo_text = Label(
                text="MT", font_size='42sp', bold=True, color=THEME["text_light"],
                pos_hint={'center_x': 0.5, 'center_y': 0.55}
            )
            self.layout.add_widget(self.logo_text)

    def update_animation(self, dt):
        self.angle = (self.angle + 5) % 360
        if self.pulse_val >= 230:
            self.pulse_dir = -1.8
        elif self.pulse_val <= 130:
            self.pulse_dir = 1.8
        self.pulse_val += self.pulse_dir
        self.draw_animated_logo()

    def end_splash(self):
        Clock.unschedule(self.anim_event)
        # توجيه ذكي: إذا كان مسجل دخول مسبقاً يذهب للشاشات مباشرة، وإلا يذهب للترحيب
        if USER_SESSION["id_token"]:
            setattr(self.manager, 'current', 'year_select')
        else:
            setattr(self.manager, 'current', 'welcome')


# =========================================================================
# 2. واجهة النصيحة والتحذير الأكاديمي
# =========================================================================
class WelcomeScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        layout = FloatLayout()
        content_box = BoxLayout(orientation='vertical', size_hint=(0.85, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=20)
        
        warning_icon = Label(text="⚠️", font_size='55sp', size_hint_y=None, height=65)
        title_lbl = Label(text=ar("تنبيه أكاديمي هام جداً:"), font_size='22sp', bold=True, color=THEME["danger"], size_hint_y=None, height=40)
        
        desc_lbl = Label(
            text=ar("تطبيقي لن يجعلك تنجح إذا لم تدرس جيداً، إنه يوفر لك وقتك ومجهودك بشكل كبير فقط ويضع المادة بين يديك!"),
            font_size='16sp', color=THEME["text_dark"], halign='center', valign='middle', line_height=1.4
        )
        desc_lbl.bind(size=desc_lbl.setter('text_size'))
        
        info_card = CourseCard(
            "مهمة تطبيق MT الأساسية",
            "الملفات والمقاييس والامتحانات تُحفظ وتفتح بشكل آمن تماماً لحماية خصوصيتك وضمان أفضل تجربة دراسية خالية من التشتيت.",
            bg_color=(0.94, 0.96, 0.99, 1), size_hint_y=None, height=120
        )
        
        start_btn = Button(
            text=ar("موافق، دعنا نبدأ الدراسة"), font_size='16sp', bold=True, size_hint_y=None, height=55,
            background_normal='', background_color=THEME["primary"], color=THEME["text_light"]
        )
        start_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'login'))
        
        content_box.add_widget(warning_icon)
        content_box.add_widget(title_lbl)
        content_box.add_widget(desc_lbl)
        content_box.add_widget(info_card)
        content_box.add_widget(start_btn)
        layout.add_widget(content_box)
        self.add_widget(layout)


# =========================================================================
# 3. شاشة تسجيل الدخول وإنشاء الحساب المتكاملة مع Firebase
# =========================================================================
class LoginScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title="حساب الطالب الجامعي")
        main_layout.add_widget(header)
        
        content = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # حقل البريد الإلكتروني
        content.add_widget(Label(text=ar("البريد الإلكتروني الدراسي أو الشخصي:"), size_hint_y=None, height=25, halign='right', color=THEME["text_dark"], bold=True))
        self.email_input = TextInput(
            hint_text="student@univ.dz", 
            multiline=False, 
            size_hint_y=None, 
            height=45,
            write_tab=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(self.email_input)
        
        # حقل كلمة المرور
        content.add_widget(Label(text=ar("كلمة المرور الخاصة بحسابك:"), size_hint_y=None, height=25, halign='right', color=THEME["text_dark"], bold=True))
        self.pass_input = TextInput(
            hint_text="••••••••", 
            password=True, 
            multiline=False, 
            size_hint_y=None, 
            height=45,
            write_tab=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(self.pass_input)
        
        content.add_widget(Widget(size_hint_y=None, height=10))
        
        # أزرار الإجراءات الأساسية
        buttons_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=50)
        
        signup_btn = Button(
            text=ar("إنشاء حساب جديد"), 
            font_size='14sp', 
            bold=True,
            background_normal='', 
            background_color=THEME["success"], 
            color=THEME["text_light"]
        )
        signup_btn.bind(on_release=self.perform_firebase_signup)
        
        login_btn = Button(
            text=ar("تسجيل الدخول"), 
            font_size='14sp', 
            bold=True,
            background_normal='', 
            background_color=THEME["primary"], 
            color=THEME["text_light"]
        )
        login_btn.bind(on_release=self.perform_firebase_login)
        
        buttons_layout.add_widget(signup_btn)
        buttons_layout.add_widget(login_btn)
        content.add_widget(buttons_layout)
        
        content.add_widget(Widget())
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def perform_firebase_signup(self, instance):
        email = self.email_input.text.strip()
        password = self.pass_input.text.strip()
        
        if not email or not password:
            show_custom_popup("تنبيه هام", "يرجى ملء جميع الحقول المطلوبة لإنشاء الحساب!", is_warning=True)
            return
            
        signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            response = requests.post(signup_url, json=payload, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                USER_SESSION["user_email"] = email
                USER_SESSION["id_token"] = res_data.get("idToken", "")
                show_custom_popup("تم بنجاح 🎉", "أهلاً بك! تم تسجيل حسابك الجديد بنجاح في تطبيقنا.")
                self.manager.current = 'year_select'
            else:
                raw_error = response.json().get("error", {}).get("message", "فشل التسجيل")
                friendly_error = self.translate_firebase_error(raw_error)
                show_custom_popup("خطأ في إنشاء الحساب", friendly_error, is_warning=True)
        except Exception as e:
            show_custom_popup("خطأ في الاتصال", "يرجى التحقق من اتصال الإنترنت وحاول مجدداً.", is_warning=True)

    def perform_firebase_login(self, instance):
        email = self.email_input.text.strip()
        password = self.pass_input.text.strip()
        
        if not email or not password:
            show_custom_popup("تنبيه هام", "يرجى إدخال البريد وكلمة المرور بشكل صحيح.", is_warning=True)
            return
            
        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            response = requests.post(login_url, json=payload, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                USER_SESSION["user_email"] = email
                USER_SESSION["id_token"] = res_data.get("idToken", "")
                
                # تفعيل اشتراك VIP مؤقت لأغراض الاختبار، لاحقاً سنتأكد من قاعدة البيانات الفورية
                if "@univ.dz" in email:
                    USER_SESSION["is_vip"] = True
                
                self.manager.current = 'year_select'
            else:
                raw_error = response.json().get("error", {}).get("message", "فشل الدخول")
                friendly_error = self.translate_firebase_error(raw_error)
                show_custom_popup("فشل تسجيل الدخول", friendly_error, is_warning=True)
        except Exception as e:
            show_custom_popup("خطأ في الاتصال", "تعذر الاتصال بالخادم، تأكد من جودة الإنترنت.", is_warning=True)

    def translate_firebase_error(self, error_msg):
        if "EMAIL_EXISTS" in error_msg:
            return "هذا البريد الإلكتروني مسجل ومستخدم بالفعل."
        elif "INVALID_EMAIL" in error_msg:
            return "صيغة البريد الإلكتروني غير صحيحة."
        elif "WEAK_PASSWORD" in error_msg:
            return "كلمة المرور ضعيفة جداً! يجب أن تتكون من 6 خانات كحد أدنى."
        elif "EMAIL_NOT_FOUND" in error_msg or "INVALID_PASSWORD" in error_msg:
            return "البريد الإلكتروني أو كلمة المرور خاطئة، يرجى التثبت."
        elif "USER_DISABLED" in error_msg:
            return "تم تعطيل هذا الحساب من قبل الإدارة."
        return f"حدث خطأ غير متوقع: {error_msg}"


# =========================================================================
# 4. واجهة اختيار السنة الجامعية (L1 - M2)
# =========================================================================
class YearSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title="بوابة السنوات الأكاديمية")
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        list_container = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        list_container.bind(minimum_height=list_container.setter('height'))
        
        years = [
            ("السنة الأولى (L1)", "الجذع المشترك للمواد التقنية والعلمية والدقيقة"),
            ("السنة الثانية (L2)", "مرحلة التخصص الأساسية وتوزيع التخصصات الفرعية"),
            ("السنة الثالثة (L3)", "نهاية الطور والتحضير لمشروع التخرج والامتحانات"),
            ("ماستر 1 (M1)", "الطور المتقدم والمناهج البحثية والتطبيقية المعمقة"),
            ("ماستر 2 (M2)", "إعداد أطروحة الماستر والتربصات الميدانية للعمل")
        ]
        
        for yr_title, yr_desc in years:
            btn = CourseCard(
                yr_title, yr_desc, size_hint_y=None, height=100,
                on_release_callback=self.create_callback(yr_title)
            )
            list_container.add_widget(btn)
            
        scroll.add_widget(list_container)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_callback(self, yr_title):
        def select_year():
            USER_SESSION["selected_year"] = yr_title
            self.manager.current = 'track_select'
        return select_year


# =========================================================================
# 5. واجهة اختيار التخصص التفاعلية
# =========================================================================
class TrackSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        selected_year = USER_SESSION["selected_year"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=f"تخصصات {selected_year}", show_back=True, back_target='year_select', manager=self.manager)
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=15, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        tracks_available = CURRICULUM_DATA.get(selected_year, {})
        
        if not tracks_available:
            # رسالة ذكية في حال لم يتم تعبئة بيانات السنة بعد، حفاظاً على ثبات التطبيق
            empty_lbl = Label(
                text=ar("سيتم تفعيل ورفع ملفات هذا الطور الدراسي قريباً جداً في التحديث القادم!"),
                font_size='16sp', color=THEME["text_dark"], halign='center', size_hint_y=None, height=200
            )
            empty_lbl.bind(size=empty_lbl.setter('text_size'))
            grid.add_widget(empty_lbl)
        else:
            for track_name in tracks_available.keys():
                track_card = CourseCard(
                    track_name, f"اضغط لاستعراض فصول ومواد تخصص {track_name}",
                    size_hint_y=None, height=110, on_release_callback=self.create_callback(track_name)
                )
                grid.add_widget(track_card)
            
        scroll.add_widget(grid)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_callback(self, track_name):
        def select_track():
            USER_SESSION["selected_track"] = track_name
            self.manager.current = 'semester_select'
        return select_track


# =========================================================================
# 6. واجهة اختيار الفصل الدراسي (السداسيات)
# =========================================================================
class SemesterSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        year = USER_SESSION["selected_year"]
        track = USER_SESSION["selected_track"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title="الفصل الدراسي", show_back=True, back_target='track_select', manager=self.manager)
        main_layout.add_widget(header)
        
        content = BoxLayout(orientation='vertical', padding=25, spacing=20)
        title_lbl = Label(text=ar(f"مناهج: {track}"), font_size='18sp', bold=True, color=THEME["primary"], size_hint_y=None, height=40)
        content.add_widget(title_lbl)
        
        semesters_available = CURRICULUM_DATA.get(year, {}).get(track, {})
        for sem_name in semesters_available.keys():
            sem_card = CourseCard(
                sem_name, "اضغط لعرض كافة المقاييس والدروس الموثقة والامتحانات",
                size_hint_y=None, height=130, on_release_callback=self.create_callback(sem_name)
            )
            content.add_widget(sem_card)
            
        content.add_widget(Widget())
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def create_callback(self, sem_name):
        def select_semester():
            USER_SESSION["selected_semester"] = sem_name
            self.manager.current = 'subject_list'
        return select_semester


# =========================================================================
# 7. واجهة عرض المقاييس (المواد)
# =========================================================================
class SubjectListScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        year = USER_SESSION["selected_year"]
        track = USER_SESSION["selected_track"]
        semester = USER_SESSION["selected_semester"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=f"مقاييس {semester}", show_back=True, back_target='semester_select', manager=self.manager)
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        container = BoxLayout(orientation='vertical', padding=15, spacing=15, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        subjects = CURRICULUM_DATA.get(year, {}).get(track, {}).get(semester, ["لا توجد مواد مسجلة حالياً"])
        for sub in subjects:
            sub_card = CourseCard(
                sub, "الدروس، السلاسل، وحقيبة الاختبارات الحصرية للتخصص",
                size_hint_y=None, height=110, on_release_callback=self.create_callback(sub)
            )
            container.add_widget(sub_card)
            
        scroll.add_widget(container)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_callback(self, sub_name):
        def view_files():
            USER_SESSION["selected_subject"] = sub_name
            self.manager.current = 'section_select'
        return view_files


# =========================================================================
# 8. شاشة اختيار القسم الفرعي (دروس - مجلات - اختبارات)
# =========================================================================
class SectionSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        sub = USER_SESSION["selected_subject"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=sub, show_back=True, back_target='subject_list', manager=self.manager)
        main_layout.add_widget(header)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        sections = [
            ("الدروس والملخصات 📚", "تصفح المحاضرات والملخصات المنظمة وفقاً للبرنامج الرسمي الوزاري", "lessons"),
            ("المجلات وسلاسل التمارين 📖", "سلاسل تمارين محلولة ومقترحة من نخبة الأساتذة للتحضير الفردي", "magazines"),
            ("امتحانات شاملة (50 اختبار) 📝", "امتحانات السنوات السابقة والحلول النموذجية: اختبارين مجاناً والباقي للمشتركين VIP", "exams")
        ]
        
        for name, desc, sec_id in sections:
            card = CourseCard(
                name, desc, bg_color=THEME["card_bg"] if sec_id != "exams" else (0.99, 0.97, 0.94, 1),
                size_hint_y=None, height=120,
                on_release_callback=self.create_callback(sec_id)
            )
            content.add_widget(card)
            
        content.add_widget(Widget())
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def create_callback(self, sec_id):
        def select_section():
            USER_SESSION["selected_section"] = sec_id
            self.manager.current = 'files_list'
        return select_section


# =========================================================================
# 9. شاشة عرض الملفات والاختبارات الـ 50 (مع نظام الأمان والبوابة المدفوعة)
# =========================================================================
def create_callback(self, yr_title):
        def select_year():
            USER_SESSION["selected_year"] = yr_title
            self.manager.current = 'track_select'
        return select_year


# =========================================================================
# 5. واجهة اختيار التخصص التفاعلية
# =========================================================================
class TrackSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        selected_year = USER_SESSION["selected_year"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=f"تخصصات {selected_year}", show_back=True, back_target='year_select', manager=self.manager)
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=15, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        tracks_available = CURRICULUM_DATA.get(selected_year, {})
        
        if not tracks_available:
            # رسالة ذكية في حال لم يتم تعبئة بيانات السنة بعد، حفاظاً على ثبات التطبيق
            empty_lbl = Label(
                text=ar("سيتم تفعيل ورفع ملفات هذا الطور الدراسي قريباً جداً في التحديث القادم!"),
                font_size='16sp', color=THEME["text_dark"], halign='center', size_hint_y=None, height=200
            )
            empty_lbl.bind(size=empty_lbl.setter('text_size'))
            grid.add_widget(empty_lbl)
        else:
            for track_name in tracks_available.keys():
                track_card = CourseCard(
                    track_name, f"اضغط لاستعراض فصول ومواد تخصص {track_name}",
                    size_hint_y=None, height=110, on_release_callback=self.create_callback(track_name)
                )
                grid.add_widget(track_card)
            
        scroll.add_widget(grid)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_callback(self, track_name):
        def select_track():
            USER_SESSION["selected_track"] = track_name
            self.manager.current = 'semester_select'
        return select_track


# =========================================================================
# 6. واجهة اختيار الفصل الدراسي (السداسيات)
# =========================================================================
class SemesterSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        year = USER_SESSION["selected_year"]
        track = USER_SESSION["selected_track"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title="الفصل الدراسي", show_back=True, back_target='track_select', manager=self.manager)
        main_layout.add_widget(header)
        
        content = BoxLayout(orientation='vertical', padding=25, spacing=20)
        title_lbl = Label(text=ar(f"مناهج: {track}"), font_size='18sp', bold=True, color=THEME["primary"], size_hint_y=None, height=40)
        content.add_widget(title_lbl)
        
        semesters_available = CURRICULUM_DATA.get(year, {}).get(track, {})
        for sem_name in semesters_available.keys():
            sem_card = CourseCard(
                sem_name, "اضغط لعرض كافة المقاييس والدروس الموثقة والامتحانات",
                size_hint_y=None, height=130, on_release_callback=self.create_callback(sem_name)
            )
            content.add_widget(sem_card)
            
        content.add_widget(Widget())
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def create_callback(self, sem_name):
        def select_semester():
            USER_SESSION["selected_semester"] = sem_name
            self.manager.current = 'subject_list'
        return select_semester


# =========================================================================
# 7. واجهة عرض المقاييس (المواد)
# =========================================================================
class SubjectListScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        year = USER_SESSION["selected_year"]
        track = USER_SESSION["selected_track"]
        semester = USER_SESSION["selected_semester"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=f"مقاييس {semester}", show_back=True, back_target='semester_select', manager=self.manager)
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        container = BoxLayout(orientation='vertical', padding=15, spacing=15, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        subjects = CURRICULUM_DATA.get(year, {}).get(track, {}).get(semester, ["لا توجد مواد مسجلة حالياً"])
        for sub in subjects:
            sub_card = CourseCard(
                sub, "الدروس، السلاسل، وحقيبة الاختبارات الحصرية للتخصص",
                size_hint_y=None, height=110, on_release_callback=self.create_callback(sub)
            )
            container.add_widget(sub_card)
            
        scroll.add_widget(container)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_callback(self, sub_name):
        def view_files():
            USER_SESSION["selected_subject"] = sub_name
            self.manager.current = 'section_select'
        return view_files


# =========================================================================
# 8. شاشة اختيار القسم الفرعي (دروس - مجلات - اختبارات)
# =========================================================================
class SectionSelectScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        sub = USER_SESSION["selected_subject"]
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=sub, show_back=True, back_target='subject_list', manager=self.manager)
        main_layout.add_widget(header)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        sections = [
            ("الدروس والملخصات 📚", "تصفح المحاضرات والملخصات المنظمة وفقاً للبرنامج الرسمي الوزاري", "lessons"),
            ("المجلات وسلاسل التمارين 📖", "سلاسل تمارين محلولة ومقترحة من نخبة الأساتذة للتحضير الفردي", "magazines"),
            ("امتحانات شاملة (50 اختبار) 📝", "امتحانات السنوات السابقة والحلول النموذجية: اختبارين مجاناً والباقي للمشتركين VIP", "exams")
        ]
        
        for name, desc, sec_id in sections:
            card = CourseCard(
                name, desc, bg_color=THEME["card_bg"] if sec_id != "exams" else (0.99, 0.97, 0.94, 1),
                size_hint_y=None, height=120,
                on_release_callback=self.create_callback(sec_id)
            )
            content.add_widget(card)
            
        content.add_widget(Widget())
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def create_callback(self, sec_id):
        def select_section():
            USER_SESSION["selected_section"] = sec_id
            self.manager.current = 'files_list'
        return select_section


# =========================================================================
# 9. شاشة عرض الملفات والاختبارات الـ 50 (مع نظام الأمان والبوابة المدفوعة)
# =========================================================================
class FilesListScreen(AppScreen):
    def on_enter(self, *args):
        self.clear_widgets()
        section_type = USER_SESSION["selected_section"]
        subject = USER_SESSION["selected_subject"]
        
        title_map = {"lessons": "قائمة الدروس والملخصات", "magazines": "المجلات السلاسل", "exams": "بنك الـ 50 اختبار نموذجياً"}
        display_title = title_map.get(section_type, "قائمة الملفات")
        
        main_layout = BoxLayout(orientation='vertical')
        header = TopNavBar(title=f"{display_title}", show_back=True, back_target='section_select', manager=self.manager)
        main_layout.add_widget(header)
        
        scroll = ScrollView(size_hint=(1, 1))
        container = BoxLayout(orientation='vertical', padding=15, spacing=15, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        if section_type == "exams":
            for i in range(1, 51):
                is_free = (i <= 2)
                
                if is_free:
                    status_text = "🔓 ملف مجاني - اضغط للمذاكرة وقراءة الاختبار الفوري"
                    card_color = (0.93, 0.98, 0.93, 1) # أخضر مريح جداً يعبر عن المحتوى المفتوح
                else:
                    status_text = "🔒 حصري للمشتركين VIP - تواصل مع الإدارة للفتح"
                    card_color = (1, 0.96, 0.96, 1) # أحمر وردي ناعم يشير للملف المقفل
                    
                exam_card = CourseCard(
                    f"الاختبار رقم {i:02d}",
                    status_text,
                    bg_color=card_color,
                    size_hint_y=None,
                    height=100,
                    on_release_callback=self.create_exam_callback(i, is_free)
                )
                container.add_widget(exam_card)
        else:
            for i in range(1, 6):
                file_card = CourseCard(
                    f"المحاضرة والملخص رقم {i:02d}",
                    "🔓 تصفح داخلي مباشر مدعوم بحماية كاملة من النسخ والتنزيل",
                    bg_color=(0.95, 0.97, 1, 1),
                    size_hint_y=None,
                    height=95,
                    on_release_callback=self.create_file_callback(f"file_{i}")
                )
                container.add_widget(file_card)
                
        scroll.add_widget(container)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def create_exam_callback(self, exam_num, is_free):
        def handle_click():
            if is_free or USER_SESSION["is_vip"]:
                show_custom_popup(
                    f"قارئ ملفات MT الآمن",
                    f"لقد تم فتح الاختبار رقم {exam_num} بأمان.\nتصفح مريح وحماية كاملة من لقطات الشاشة أو حفظ الملف على هاتفك."
                )
            else:
                show_custom_popup(
                    "محتوى مدفوع VIP 🔒",
                    f"عذراً يا زميلنا، هذا الملف حصري للاشتراكات المدفوعة.\n\nيرجى التواصل مع إدارة المنصة لتفعيل حسابك VIP بـ (بريدي موب أو رصيد جيزي/موبيليس) لتشغيل كافة الـ 50 اختباراً فوراً:\n{USER_SESSION['user_email']}",
                    is_warning=True
                )
        return handle_click

    def create_file_callback(self, filename):
        def handle_click():
            show_custom_popup(
                "قراءة ملف آمن",
                f"يتم تحميل وتصفح المستند {filename} داخل منصتنا السريعة. خصوصيتك وحمايتنا قيد العمل الآن لمنع التسريب والتحميل العشوائي خارج جهازك."
            )
        return handle_click


# =========================================================================
# مدير الشاشات وبوابة إطلاق التطبيق الأكاديمي
# =========================================================================
class MTApp(App):
    def build(self):
        # تفعيل الحجم الافتراضي لواجهة الكومبيوتر للتجربة بشكل مريح وثابت يحاكي أبعاد الهاتف
        Window.size = (400, 720)
        
        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(YearSelectScreen(name='year_select'))
        sm.add_widget(TrackSelectScreen(name='track_select'))
        sm.add_widget(SemesterSelectScreen(name='semester_select'))
        sm.add_widget(SubjectListScreen(name='subject_list'))
        sm.add_widget(SectionSelectScreen(name='section_select'))
        sm.add_widget(FilesListScreen(name='files_list'))
        return sm

if __name__ == '__main__':
    MTApp().run()