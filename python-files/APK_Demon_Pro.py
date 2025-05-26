import os
import sys
import subprocess
import time
import random
import shutil
import platform
from pathlib import Path
import traceback
import ctypes
from colorama import init, Fore, Back, Style
import questionary
from questionary import Style as QStyle
from simple_chalk import chalk
from tabulate import tabulate

# حل مشكلة sys.stdin للأنظمة المجمعة
if sys.stdin is None or not sys.stdin.isatty():
    sys.stdin = open(os.devnull)

# تهيئة وحدة التحكم على Windows
if platform.system() == 'Windows':
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

init(autoreset=True)

class UltimateApkDemonPro:
    def __init__(self):
        self.version = "3.2.0"
        self.demon_name = "ULTIMATE APK DEMON"
        self.temp_dir = "DEMON_TEMP"
        self.clones_dir = "DEMON_CLONES"
        self.decompiled_dir = "DEMON_DECOMPILED"
        self.selected_apk = ""
        self.errors = []
        
        # إعدادات الواجهة
        self.custom_style = QStyle([
            ('question', 'fg:#ff00ff bold'),
            ('selected', 'fg:#00ff00 bg:#000000'),
            ('pointer', 'fg:#ff0000 bold'),
        ])

    def clear_screen(self):
        """مسح الشاشة آمن لجميع الأنظمة"""
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            print("\n" * 100)

    def show_banner(self):
        """عرض بانر متحرك"""
        self.clear_screen()
        
        try:
            # تأثيرات بصرية للبانر
            colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.MAGENTA]
            banner = pyfiglet.figlet_format(self.demon_name, font="slant")
            
            for i, line in enumerate(banner.split('\n')):
                print(colors[i % len(colors)] + line)
                time.sleep(0.03)
            
            print(chalk.blue("=" * 80))
            print(chalk.yellow(f"🔥 الإصدار {self.version} | أداة خارقة لفك تشفير APK 🔥"))
            print(chalk.blue("=" * 80))
            
            if self.errors:
                print(chalk.red("\n[!] الأخطاء السابقة:"))
                for error in self.errors[-3:]:
                    print(chalk.red(f" - {error}"))
                
        except Exception as e:
            # واجهة بديلة إذا فشل البانر
            print(chalk.red("\n" + "=" * 80))
            print(chalk.yellow("🔥 Ultimate APK Demon 🔥"))
            print(chalk.red("=" * 80 + "\n"))
            self.log_error(f"فشل عرض البانر: {str(e)}")

    def log_error(self, message):
        """تسجيل الأخطاء"""
        self.errors.append(message)
        try:
            with open("demon_errors.log", "a", encoding="utf-8") as f:
                f.write(f"[{time.ctime()}] {message}\n")
        except:
            pass

    def run_command(self, command):
        """تنفيذ الأوامر بشكل آمن"""
        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True if platform.system() == "Windows" else False
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self.log_error(f"فشل الأمر: {' '.join(command)} | {error_msg}")
            return False, error_msg

    def show_main_menu(self):
        """القائمة الرئيسية المحسنة"""
        while True:
            try:
                self.show_banner()
                
                choices = [
                    {"name": "🔓 فك التشفير فقط", "value": "decompile"},
                    {"name": "👹 فك التشفير + استنساخ", "value": "clone"},
                    {"name": "⚙️ فحص الأدوات", "value": "check_tools"},
                    {"name": "❌ خروج", "value": "exit"}
                ]
                
                try:
                    action = questionary.select(
                        "اختر مهمتك:",
                        choices=choices,
                        style=self.custom_style,
                        use_shortcuts=True
                    ).ask()
                except EOFError:
                    action = "exit"
                
                if action == "exit":
                    print(chalk.red("\nوداعًا!"))
                    break
                elif action == "decompile":
                    self.decompile_apk()
                elif action == "clone":
                    self.clone_apk()
                elif action == "check_tools":
                    self.check_tools()
                    
            except KeyboardInterrupt:
                print(chalk.red("\nتم الإيقاف بواسطة المستخدم!"))
                break
            except Exception as e:
                self.log_error(f"خطأ في القائمة: {str(e)}")
                input("\nحدث خطأ! اضغط Enter للمحاولة مرة أخرى...")

    def decompile_apk(self):
        """فك تشفير APK"""
        if not self.selected_apk:
            if not self.select_apk_file():
                return
        
        try:
            # تنظيف المجلدات القديمة
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            shutil.rmtree(self.decompiled_dir, ignore_errors=True)
            os.makedirs(self.decompiled_dir, exist_ok=True)
            
            # استخدام apktool لاستخراج الموارد
            self.log_error("بدء استخراج الموارد باستخدام apktool...")
            success, output = self.run_command(["apktool", "d", self.selected_apk, "-o", f"{self.decompiled_dir}/extracted", "-f"])
            
            if success:
                print(chalk.green("✅ تم استخراج الموارد بنجاح!"))
                
                # استخدام jadx لفك تشفير الكود
                self.log_error("بدء فك تشفير الكود باستخدام jadx...")
                success, output = self.run_command(["jadx", "-d", f"{self.decompiled_dir}/java_sources", self.selected_apk])
                
                if success:
                    print(chalk.green("✅ تم فك تشفير الكود بنجاح!"))
                    self.show_file_stats()
                else:
                    print(chalk.red("❌ فشل فك تشفير الكود!"))
            else:
                print(chalk.red("❌ فشل استخراج الموارد!"))
            
        except Exception as e:
            self.log_error(f"حدث خطأ غير متوقع أثناء التفكيك: {str(e)}")
            traceback.print_exc()
            
        input("\nاضغط Enter للعودة...")

    def clone_apk(self):
        """استنساخ APK"""
        if not self.decompile_apk():
            return
        
        try:
            # تعديل Manifest
            self.modify_manifest()
            
            # بناء APK جديد
            self.build_new_apk()
            
        except Exception as e:
            self.log_error(f"فشل عملية الاستنساخ: {str(e)}")
            traceback.print_exc()
            
        input("\nاضغط Enter للعودة...")

    def modify_manifest(self):
        """تعديل AndroidManifest.xml"""
        manifest_path = f"{self.decompiled_dir}/extracted/AndroidManifest.xml"
        if not os.path.exists(manifest_path):
            raise FileNotFoundError("لا يمكن العثور على AndroidManifest.xml!")
        
        try:
            # قراءة المحتوى
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # تغيير package name
            new_pkg = self.generate_new_package_name()
            content = content.replace('package="', f'package="{new_pkg}"')
            
            # كتابة المحتوى المعدل
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(chalk.green(f"✅ تم تغيير package name إلى: {new_pkg}"))
            return True
            
        except Exception as e:
            raise Exception(f"فشل تعديل AndroidManifest.xml: {str(e)}")

    def generate_new_package_name(self):
        """إنشاء اسم حزمة جديد عشوائي"""
        prefixes = ["com", "net", "org", "dev"]
        names = ["demon", "clone", "shadow", "phantom", "ghost"]
        return f"{random.choice(prefixes)}.{random.choice(names)}{random.randint(100,999)}"

    def build_new_apk(self):
        """بناء APK جديد"""
        try:
            # بناء APK غير موقّع
            print(chalk.blue("\n[🏗️] بدء بناء APK غير موقّع..."))
            success, output = self.run_command(["apktool", "b", f"{self.decompiled_dir}/extracted", "-o", "temp_unsigned.apk"])
            
            if not success:
                raise Exception("فشل بناء APK غير موقّع")
            
            # إنشاء مفتاح توقيع إذا لم يكن موجودًا
            if not os.path.exists("demon.keystore"):
                print(chalk.blue("\n[🔑] إنشاء مفتاح توقيع جديد..."))
                success, output = self.run_command([
                    "keytool", "-genkey", "-v", "-keystore", "demon.keystore",
                    "-alias", "demon_key", "-keyalg", "RSA", "-keysize", "2048",
                    "-validity", "10000", "-storepass", "demondemo", 
                    "-keypass", "demondemo", "-dname", "CN=DEMON"
                ])
                
                if not success:
                    raise Exception("فشل إنشاء مفتاح التوقيع")
            
            # توقيع APK
            print(chalk.blue("\n[✍️] بدء توقيع APK..."))
            success, output = self.run_command([
                "jarsigner", "-verbose", "-sigalg", "SHA1withRSA",
                "-digestalg", "SHA1", "-keystore", "demon.keystore",
                "-storepass", "demondemo", "-keypass", "demondemo",
                "temp_unsigned.apk", "demon_key"
            ])
            
            if not success:
                raise Exception("فشل توقيع APK")
            
            # تحسين APK باستخدام zipalign
            os.makedirs(self.clones_dir, exist_ok=True)
            output_name = f"DEMON_CLONE_{time.strftime('%Y%m%d_%H%M%S')}.apk"
            output_path = os.path.join(self.clones_dir, output_name)
            
            print(chalk.blue("\n[⚡] بدء تحسين APK باستخدام zipalign..."))
            success, output = self.run_command(["zipalign", "-v", "4", "temp_unsigned.apk", output_path])
            
            if not success:
                raise Exception("فشل تحسين APK")
            
            # تنظيف الملف المؤقت
            if os.path.exists("temp_unsigned.apk"):
                os.remove("temp_unsigned.apk")
            
            print(chalk.green(f"\n🎉 تم بناء التطبيق المستنسخ بنجاح: {output_path}"))
            return True
            
        except Exception as e:
            raise Exception(f"حدث خطأ أثناء البناء: {str(e)}")

    def check_tools(self):
        """فحص الأدوات المطلوبة"""
        tools = [
            ("apktool", "https://ibotpeaches.github.io/Apktool/"),
            ("jadx", "https://github.com/skylot/jadx"),
            ("keytool", "https://docs.oracle.com/javase/8/docs/technotes/tools/windows/keytool.html"),
            ("jarsigner", "https://docs.oracle.com/javase/8/docs/technotes/tools/windows/jarsigner.html"),
            ("zipalign", "https://developer.android.com/studio/command-line/zipalign")
        ]
        
        table = []
        for tool, url in tools:
            try:
                subprocess.run([tool], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                status = chalk.green("✓ مثبت")
            except:
                status = chalk.red("✗ غير مثبت")
            table.append([tool, url, status])
        
        self.clear_screen()
        print(tabulate(table, 
                     headers=["الأداة", "رابط التثبيت", "الحالة"], 
                     tablefmt="fancy_grid",
                     colalign=("center", "left", "center")))
        
        input("\nاضغط Enter للعودة...")

    def show_file_stats(self):
        """عرض إحصائيات الملفات"""
        stats = {
            "📂 المجلدات": 0,
            "📝 ملفات XML": 0,
            "🖼️ صور": 0,
            "📜 ملفات Java/Kotlin": 0,
            "🔧 ملفات أخرى": 0
        }
        
        if os.path.exists(f"{self.decompiled_dir}/extracted"):
            for root, dirs, files in os.walk(f"{self.decompiled_dir}/extracted"):
                stats["📂 المجلدات"] += len(dirs)
                for f in files:
                    if f.endswith('.xml'):
                        stats["📝 ملفات XML"] += 1
                    elif f.endswith(('.png', '.jpg', '.webp')):
                        stats["🖼️ صور"] += 1
                    else:
                        stats["🔧 ملفات أخرى"] += 1
        
        if os.path.exists(f"{self.decompiled_dir}/java_sources"):
            for root, dirs, files in os.walk(f"{self.decompiled_dir}/java_sources"):
                stats["📂 المجلدات"] += len(dirs)
                for f in files:
                    if f.endswith(('.java', '.kt')):
                        stats["📜 ملفات Java/Kotlin"] += 1
                    else:
                        stats["🔧 ملفات أخرى"] += 1
        
        table = [[k, v] for k, v in stats.items()]
        print(chalk.cyan("\n📊 إحصائيات الملفات المستخرجة:"))
        print(tabulate(table, headers=["النوع", "العدد"], tablefmt="pretty"))

    def run(self):
        """تشغيل البرنامج"""
        try:
            self.show_main_menu()
        except Exception as e:
            print(chalk.red(f"حدث خطأ فادح: {str(e)}"))
            traceback.print_exc()
            input("اضغط Enter للخروج...")
            sys.exit(1)

if __name__ == "__main__":
    try:
        # حل نهائي لمشكلة sys.stdin
        if sys.stdin is None or not sys.stdin.isatty():
            sys.stdin = open(os.devnull)
            
        app = UltimateApkDemonPro()
        app.run()
    except Exception as e:
        print(chalk.red(f"خطأ في التشغيل: {str(e)}"))
        input("اضغط Enter للخروج...")
        sys.exit(1)