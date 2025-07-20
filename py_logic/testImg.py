from __future__ import annotations

import pathlib
import numpy as np

class TestImg:
    """
    מחלקה מקבילה לבדיקות שמדמה את פעולות Img
    ומדפיסה מידע לניפוי שגיאות במקום להציג תמונות
    """
    
    def __init__(self):
        self.img = None
        self.width = 0
        self.height = 0
        self.channels = 0
        self.operations_log = []

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = None) -> "TestImg":
        """
        מדמה קריאת תמונה וחישוב המידות החדשות
        """
        path = str(path)
        
        # דמה קריאת תמונה בגודל אקראי (או קבוע למטרות בדיקה)
        # יכול להיות מותאם לגדלים ספציפיים לפי שם הקובץ
        self.width = 800  # גודל ברירת מחדל
        self.height = 600
        self.channels = 3
        
        # יצירת מטריצה דמה
        self.img = np.zeros((self.height, self.width, self.channels), dtype=np.uint8)
        
        print(f"📖 קריאת תמונה: {path}")
        print(f"   גודל מקורי: {self.width}x{self.height}, ערוצים: {self.channels}")
        
        self.operations_log.append(f"READ: {path} ({self.width}x{self.height})")
        
        if size is not None:
            target_w, target_h = size
            original_w, original_h = self.width, self.height
            
            print(f"   גודל יעד: {target_w}x{target_h}")
            print(f"   שמירת יחס גובה-רוחב: {keep_aspect}")
            
            if keep_aspect:
                scale = min(target_w / original_w, target_h / original_h)
                new_w, new_h = int(original_w * scale), int(original_h * scale)
                print(f"   יחס שינוי גודל: {scale:.3f}")
                print(f"   גודל חדש (עם שמירת יחס): {new_w}x{new_h}")
            else:
                new_w, new_h = target_w, target_h
                print(f"   גודל חדש (מדויק): {new_w}x{new_h}")
            
            self.width, self.height = new_w, new_h
            self.img = np.zeros((self.height, self.width, self.channels), dtype=np.uint8)
            
            self.operations_log.append(f"RESIZE: {original_w}x{original_h} -> {new_w}x{new_h}")
        
        print(f"   ✅ תמונה נטענה בהצלחה\n")
        return self

    def draw_on(self, other_img, x, y):
        """
        מדמה ציור תמונה על תמונה אחרת ובודק התאמה
        """
        if self.img is None or other_img.img is None:
            raise ValueError("שתי התמונות חייבות להיות טעונות לפני הציור.")
        
        print(f"🎨 ציור תמונה:")
        print(f"   תמונה מקור: {self.width}x{self.height} (ערוצים: {self.channels})")
        print(f"   תמונה יעד: {other_img.width}x{other_img.height} (ערוצים: {other_img.channels})")
        print(f"   מיקום: ({x}, {y})")
        
        # שמירה של ערוצי המקור הנוכחיים לפני השינוי
        original_self_channels = self.channels
        original_other_channels = other_img.channels
        
        # בדיקת התאמת ערוצים
        if self.channels != other_img.channels:
            print(f"   ⚠️  אי-התאמת ערוצים: {self.channels} vs {other_img.channels}")
            if self.channels == 3 and other_img.channels == 4:
                self.channels = 4
                print("   🔄 המרה: BGR -> BGRA")
            elif self.channels == 4 and other_img.channels == 3:
                self.channels = 3
                print("   🔄 המרה: BGRA -> BGR")
        
        # בדיקת גבולות
        if y + self.height > other_img.height or x + self.width > other_img.width:
            print(f"   ❌ התמונה לא נכנסת במיקום הנתון:")
            print(f"      גבול ימין: {x + self.width} > {other_img.width}")
            print(f"      גבול תחתון: {y + self.height} > {other_img.height}")
            raise ValueError("הלוגו לא נכנס במיקום הנתון.")
        
        # החלטה על סוג הציור בהתבסס על הערוצים הסופיים
        final_channels = max(original_self_channels, original_other_channels)
        if final_channels == 4 or original_self_channels == 4:
            print("   🌟 מבוצע אלפא בלנדינג")
        else:
            print("   📋 העתקה ישירה (ללא שקיפות)")
        
        print(f"   ✅ ציור הושלם בהצלחה\n")
        
        self.operations_log.append(f"DRAW: {self.width}x{self.height} at ({x},{y})")
        other_img.operations_log.append(f"DRAWN_ON: {self.width}x{self.height} at ({x},{y})")

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        """
        מדמה הוספת טקסט לתמונה
        """
        if self.img is None:
            raise ValueError("התמונה לא נטענה.")
        
        print(f"✏️  הוספת טקסט:")
        print(f"   טקסט: '{txt}'")
        print(f"   מיקום: ({x}, {y})")
        print(f"   גודל פונט: {font_size}")
        print(f"   צבע: {color}")
        print(f"   עובי: {thickness}")
        print(f"   ✅ טקסט נוסף בהצלחה\n")
        
        self.operations_log.append(f"TEXT: '{txt}' at ({x},{y}) size={font_size}")

    def show(self):
        """
        מדמה הצגת התמונה - מדפיס מידע במקום להציג
        """
        if self.img is None:
            raise ValueError("התמונה לא נטענה.")
        
        print(f"🖼️  הצגת תמונה:")
        print(f"   גודל: {self.width}x{self.height}")
        print(f"   ערוצים: {self.channels}")
        print(f"   📊 סך הפעולות שבוצעו: {len(self.operations_log)}")
        print(f"   רשימת פעולות:")
        for i, op in enumerate(self.operations_log, 1):
            print(f"     {i}. {op}")
        print(f"   📺 התמונה הוצגה (מדומה)\n")

    def get_info(self):
        """
        החזרת מידע מפורט על התמונה למטרות בדיקה
        """
        return {
            'width': self.width,
            'height': self.height,
            'channels': self.channels,
            'operations': self.operations_log.copy(),
            'loaded': self.img is not None
        }

    def print_summary(self):
        """
        הדפסת סיכום של כל הפעולות שבוצעו
        """
        print("=" * 50)
        print("📊 סיכום פעולות התמונה")
        print("=" * 50)
        info = self.get_info()
        print(f"מידות: {info['width']}x{info['height']}")
        print(f"ערוצי צבע: {info['channels']}")
        print(f"נטענה: {'כן' if info['loaded'] else 'לא'}")
        print(f"מספר פעולות: {len(info['operations'])}")
        print("\nפירוט פעולות:")
        for i, op in enumerate(info['operations'], 1):
            print(f"  {i}. {op}")
        print("=" * 50)