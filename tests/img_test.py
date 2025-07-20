import pytest
import numpy as np
from unittest.mock import patch
from io import StringIO
import sys

from py_logic.testImg import TestImg

class TestTestImg:
    """טסטים עבור מחלקת TestImg"""
    
    def test_init(self):
        """בדיקת אתחול המחלקה"""
        img = TestImg()
        
        assert img.img is None
        assert img.width == 0
        assert img.height == 0
        assert img.channels == 0
        assert img.operations_log == []

    def test_read_basic(self, capsys):
        """בדיקת קריאת תמונה בסיסית"""
        img = TestImg()
        result = img.read("test.jpg")
        
        # בדיקת חזרת ההפניה העצמית (method chaining)
        assert result is img
        
        # בדיקת מידות ברירת המחדל
        assert img.width == 800
        assert img.height == 600
        assert img.channels == 3
        assert img.img is not None
        assert img.img.shape == (600, 800, 3)
        
        # בדיקת רישום הפעולה
        assert len(img.operations_log) == 1
        assert "READ: test.jpg" in img.operations_log[0]
        
        # בדיקת הפלט
        captured = capsys.readouterr()
        assert "📖 קריאת תמונה: test.jpg" in captured.out
        assert "גודל מקורי: 800x600" in captured.out

    def test_read_with_resize_exact(self, capsys):
        """בדיקת קריאה עם שינוי גודל מדויק"""
        img = TestImg()
        img.read("test.png", size=(200, 150), keep_aspect=False)
        
        assert img.width == 200
        assert img.height == 150
        assert img.img.shape == (150, 200, 3)
        
        # בדיקת רישום שתי הפעולות
        assert len(img.operations_log) == 2
        assert "READ: test.png" in img.operations_log[0]
        assert "RESIZE: 800x600 -> 200x150" in img.operations_log[1]
        
        captured = capsys.readouterr()
        assert "גודל יעד: 200x150" in captured.out
        assert "שמירת יחס גובה-רוחב: False" in captured.out
        assert "גודל חדש (מדויק): 200x150" in captured.out

    def test_read_with_aspect_ratio(self, capsys):
        """בדיקת קריאה עם שמירת יחס גובה-רוחב"""
        img = TestImg()
        img.read("test.jpg", size=(400, 400), keep_aspect=True)
        
        # חישוב הגודל הצפוי עם שמירת יחס
        # גודל מקורי: 800x600, יעד: 400x400
        # יחס: min(400/800, 400/600) = min(0.5, 0.667) = 0.5
        # גודל חדש: 800*0.5 = 400, 600*0.5 = 300
        
        assert img.width == 400
        assert img.height == 300
        
        captured = capsys.readouterr()
        assert "יחס שינוי גודל: 0.500" in captured.out
        assert "גודל חדש (עם שמירת יחס): 400x300" in captured.out

    def test_draw_on_success(self, capsys):
        """בדיקת ציור מוצלח"""
        sprite = TestImg().read("sprite.png", (64, 64))
        background = TestImg().read("bg.jpg", (800, 600))
        
        sprite.draw_on(background, 100, 100)
        
        # בדיקת רישום הפעולות
        assert "DRAW: 64x64 at (100,100)" in sprite.operations_log
        assert "DRAWN_ON: 64x64 at (100,100)" in background.operations_log
        
        captured = capsys.readouterr()
        assert "🎨 ציור תמונה:" in captured.out
        assert "תמונה מקור: 64x64" in captured.out
        assert "תמונה יעד: 800x600" in captured.out
        assert "מיקום: (100, 100)" in captured.out
        assert "✅ ציור הושלם בהצלחה" in captured.out

    def test_draw_on_boundary_error(self):
        """בדיקת שגיאה בציור מחוץ לגבולות"""
        sprite = TestImg().read("sprite.png", (100, 100))
        background = TestImg().read("bg.jpg", (200, 200))
        
        # ניסיון ציור מחוץ לגבולות
        with pytest.raises(ValueError, match="הלוגו לא נכנס במיקום הנתון"):
            sprite.draw_on(background, 150, 150)

    def test_draw_on_channel_mismatch(self, capsys):
        """בדיקת התמודדות עם אי-התאמת ערוצים"""
        # יצירת תמונות עם ערוצים שונים - עם גדלים מתאימים לציור
        sprite = TestImg()
        sprite.read("sprite.png", (64, 64))  # גודל קטן שיכנס בתמונת הרקע
        sprite.channels = 3  # BGR
        
        background = TestImg()
        background.read("bg.png", (800, 600))  # גודל גדול שהספרייט יכנס בו
        background.channels = 4  # BGRA
        
        sprite.draw_on(background, 50, 50)
        
        # בדיקת המרת הערוצים
        assert sprite.channels == 4  # צריך להיות מומר ל-BGRA
        
        captured = capsys.readouterr()
        assert "אי-התאמת ערוצים: 3 vs 4" in captured.out
        assert "המרה: BGR -> BGRA" in captured.out

    def test_draw_on_unloaded_images(self):
        """בדיקת שגיאה בציור תמונות לא טעונות"""
        sprite = TestImg()  # לא נטענה
        background = TestImg().read("bg.jpg")
        
        with pytest.raises(ValueError, match="שתי התמונות חייבות להיות טעונות"):
            sprite.draw_on(background, 0, 0)

    def test_put_text(self, capsys):
        """בדיקת הוספת טקסט"""
        img = TestImg().read("test.jpg")
        
        img.put_text("Hello World", 50, 100, 2.5, (0, 255, 0, 255), 2)
        
        # בדיקת רישום הפעולה
        assert "TEXT: 'Hello World' at (50,100) size=2.5" in img.operations_log
        
        captured = capsys.readouterr()
        assert "✏️  הוספת טקסט:" in captured.out
        assert "טקסט: 'Hello World'" in captured.out
        assert "מיקום: (50, 100)" in captured.out
        assert "גודל פונט: 2.5" in captured.out
        assert "צבע: (0, 255, 0, 255)" in captured.out
        assert "עובי: 2" in captured.out

    def test_put_text_unloaded(self):
        """בדיקת שגיאה בהוספת טקסט לתמונה לא טעונה"""
        img = TestImg()
        
        with pytest.raises(ValueError, match="התמונה לא נטענה"):
            img.put_text("Test", 0, 0, 1.0)

    def test_show(self, capsys):
        """בדיקת הצגת תמונה"""
        img = TestImg()
        img.read("test.jpg", (400, 300))
        img.put_text("Test", 10, 20, 1.0)
        
        img.show()
        
        captured = capsys.readouterr()
        assert "🖼️  הצגת תמונה:" in captured.out
        assert "גודל: 400x300" in captured.out
        assert "ערוצים: 3" in captured.out
        assert "📊 סך הפעולות שבוצעו: 3" in captured.out  # READ + RESIZE + TEXT
        assert "רשימת פעולות:" in captured.out

    def test_show_unloaded(self):
        """בדיקת שגיאה בהצגת תמונה לא טעונה"""
        img = TestImg()
        
        with pytest.raises(ValueError, match="התמונה לא נטענה"):
            img.show()

    def test_get_info(self):
        """בדיקת קבלת מידע על התמונה"""
        img = TestImg()
        img.read("test.jpg", (200, 150))
        img.put_text("Hello", 0, 0, 1.0)
        
        info = img.get_info()
        
        assert info['width'] == 200
        assert info['height'] == 150
        assert info['channels'] == 3
        assert info['loaded'] is True
        assert len(info['operations']) == 3  # READ + RESIZE + TEXT
        assert "READ: test.jpg" in info['operations'][0]

    def test_print_summary(self, capsys):
        """בדיקת הדפסת סיכום"""
        img = TestImg()
        img.read("test.png", (100, 100))
        img.put_text("Summary Test", 5, 15, 1.5)
        
        img.print_summary()
        
        captured = capsys.readouterr()
        assert "📊 סיכום פעולות התמונה" in captured.out
        assert "מידות: 100x100" in captured.out
        assert "ערוצי צבע: 3" in captured.out
        assert "נטענה: כן" in captured.out
        assert "מספר פעולות: 3" in captured.out
        assert "פירוט פעולות:" in captured.out

    def test_method_chaining(self):
        """בדיקת שרשור פונקציות (method chaining)"""
        img = TestImg().read("chain.jpg", (300, 200), keep_aspect=True)
        
        # עם שמירת יחס, הגודל החדש יהיה: 
        # scale = min(300/800, 200/600) = min(0.375, 0.333) = 0.333
        # new_w = 800 * 0.333 = 266, new_h = 600 * 0.333 = 200
        assert img.width == 266  # לא 300!
        assert img.height == 200
        assert len(img.operations_log) == 2

    @pytest.mark.parametrize("size,keep_aspect,expected_w,expected_h", [
        ((400, 300), False, 400, 300),  # שינוי גודל מדויק
        ((400, 400), True, 400, 300),   # שמירת יחס - רוחב מוגבל
        ((600, 300), True, 400, 300),   # שמירת יחס - גובה מוגבל
        (None, False, 800, 600),        # ללא שינוי גודל
    ])
    def test_resize_scenarios(self, size, keep_aspect, expected_w, expected_h):
        """בדיקת תרחישי שינוי גודל שונים"""
        img = TestImg().read("test.jpg", size=size, keep_aspect=keep_aspect)
        
        assert img.width == expected_w
        assert img.height == expected_h

    def test_multiple_operations_log(self):
        """בדיקת רישום פעולות מרובות"""
        img = TestImg()
        img.read("complex.jpg", (200, 200))
        img.put_text("Title", 10, 30, 2.0)
        img.put_text("Subtitle", 10, 60, 1.5)
        
        operations = img.operations_log
        assert len(operations) == 4  # READ + RESIZE + TEXT + TEXT
        assert operations[0].startswith("READ:")
        assert operations[1].startswith("RESIZE:")
        assert operations[2].startswith("TEXT: 'Title'")
        assert operations[3].startswith("TEXT: 'Subtitle'")

    def test_alpha_blending_detection(self, capsys):
        """בדיקת זיהוי אלפא בלנדינג"""
        sprite = TestImg()
        sprite.read("sprite.png", (64, 64))  # גודל קטן
        sprite.channels = 4  # RGBA
        
        background = TestImg().read("bg.jpg", (800, 600))  # גודל גדול
        sprite.draw_on(background, 0, 0)
        
        captured = capsys.readouterr()
        assert "🌟 מבוצע אלפא בלנדינג" in captured.out

    def test_direct_copy_detection(self, capsys):
        """בדיקת זיהוי העתקה ישירה"""
        sprite = TestImg()
        sprite.read("sprite.png", (64, 64))  # גודל קטן
        sprite.channels = 3  # RGB
        
        background = TestImg().read("bg.jpg", (800, 600))  # גודל גדול
        sprite.draw_on(background, 0, 0)
        
        captured = capsys.readouterr()
        assert "📋 העתקה ישירה (ללא שקיפות)" in captured.out


# פיקסצ'רים לשימוש בטסטים
@pytest.fixture
def sample_sprite():
    """יצירת ספרייט לדוגמה"""
    return TestImg().read("sprite.png", (64, 64))

@pytest.fixture
def sample_background():
    """יצירת רקע לדוגמה"""
    return TestImg().read("background.jpg", (800, 600))


class TestIntegration:
    """טסטי אינטגרציה מורכבים"""
    
    def test_complete_workflow(self, capsys):
        """בדיקת זרימת עבודה מלאה"""
        # יצירת רקע
        background = TestImg().read("game_bg.jpg", (1024, 768))
        
        # יצירת ספרייטים
        player = TestImg().read("player.png", (64, 64), keep_aspect=True)
        logo = TestImg().read("logo.png", (128, 64))
        
        # ציור הספרייטים
        player.draw_on(background, 100, 200)
        logo.draw_on(background, 50, 50)
        
        # הוספת טקסט
        background.put_text("Score: 1500", 900, 50, 1.0, (255, 255, 0))
        background.put_text("Lives: 3", 900, 80, 1.0, (255, 0, 0))
        
        # הצגה
        background.show()
        
        # בדיקות - התאמה למימוש האמיתי של TestImg
        assert len(background.operations_log) >= 4
        # בדיקה מתוקנת - הגודל האמיתי של player עם keep_aspect=True:
        # scale = min(64/800, 64/600) = 0.08, new_size = 64x48
        assert "DRAWN_ON: 64x48 at (100,200)" in background.operations_log
        assert "DRAWN_ON: 128x64 at (50,50)" in background.operations_log
        
        captured = capsys.readouterr()
        assert "📊 סך הפעולות שבוצעו:" in captured.out or "🖼️  הצגת תמונה:" in captured.out

    def test_error_recovery(self):
        """בדיקת התמודדות עם שגיאות"""
        sprite = TestImg().read("sprite.png", (100, 100))
        small_bg = TestImg().read("small_bg.jpg", (50, 50))
        
        # ניסיון ציור שיכשל
        with pytest.raises(ValueError):
            sprite.draw_on(small_bg, 0, 0)
        
        # וודא שהמצב לא השתבש
        assert sprite.img is not None
        assert small_bg.img is not None
        assert len(sprite.operations_log) == 2  # READ + RESIZE
        assert len(small_bg.operations_log) == 2  # READ + RESIZE