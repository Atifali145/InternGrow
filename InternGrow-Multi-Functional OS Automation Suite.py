# TASK 3: Multi-Functional OS Automation Suite — Submission Guide

## Kya banaya hai (What this does)
Ek **unified script** jo 4 kaam ek saath karti hai:
1. 🗂️ **File Sorter** — kisi bhi folder ke files ko type ke hisaab se
   subfolders mein categorize karti hai (Images, Documents, Videos, Audio,
   Archives, Code, Others).
2. 🔍 **Regex Text Extractor** — kisi bhi text file se emails, phone numbers,
   ya URLs (ya apna custom pattern) extract karti hai.
3. 📦 **Log Compressor** — saare `.log` files dhoondh kar ek single timestamped
   `.zip` archive mein compress kar deti hai.
4. 🔔 **Desktop Notification** — jab sab kaam complete ho jaye to native
   desktop notification fire karti hai (Windows/Mac/Linux teeno pe kaam karta
   hai, `plyer` library ke through).

---

## Step 1 — Setup
```bash
pip install plyer
```
(`os`, `re`, `shutil`, `zipfile` — ye sab Python built-in hain, extra install
nahi chahiye)

## Step 2 — Script run karein
```bash
python os_automation_suite.py "C:\Users\YourName\Downloads"
```
Ya agar chahte hain ke original `.log` files delete ho jayein zip banne ke
baad (space bachane ke liye):
```bash
python os_automation_suite.py "C:\Users\YourName\Downloads" --delete-logs
```

## Kya hoga jab aap ye run karenge:
1. Pehle sab `.log` files dhoond kar ek `logs_archive_TIMESTAMP.zip` banegi
2. Phir baaki saare files unke type ke hisaab se subfolders mein move honge
   (Images/, Documents/, Code/, Archives/, etc.)
3. Aakhir mein ek desktop popup/toast notification aayega: "Done! Sorted X
   files, zipped Y logs."

## Regex extractor alag se use karna ho to:
```python
from os_automation_suite import extract_from_file

emails = extract_from_file("contacts.txt", "emails")
phones = extract_from_file("contacts.txt", "phone_numbers")
urls   = extract_from_file("page.txt", "urls")

# Custom pattern bhi de sakte hain:
custom = extract_from_file("data.txt", custom_pattern=r"INV-\d{4}")
```

---

## Demo test (maine already run karke verify kiya hai)
Test folder mein ye files thin: `photo1.jpg`, `resume.docx`, `app.py`,
`server1.log`, `server2.log`, `contacts.txt` (emails/phone ke saath).

**Result:**
- 2 log files → `logs_archive_...zip` mein compress ho gayi (Archives/ folder mein)
- 8 files sort ho gaye → Images: 2, Documents: 3, Code: 2, Archives: 1
- Emails extract hue: `support@resumiffy.com`, `sales@example.com`
- Phone extract hua: `+92-300-1234567`
- Notification console pe fallback hui (sandbox mein display nahi tha — aapke
  apne PC par real popup aayega)

---

## Internship submission ke liye kya include karein
1. ✅ `os_automation_suite.py` (source code)
2. ✅ Before/After screenshots — messy folder vs sorted folder
3. ✅ Screenshot ya screen recording — desktop notification popup dikhte hue
4. ✅ Ye README
5. 🎥 Optional: 1-2 min demo video (best impression ke liye — mentors ko live
   demo bohot pasand aata hai)

## Tips for "attractive" presentation
- Before/after folder ka side-by-side screenshot lein (visually impressive lagta hai)
- Terminal output ka colored/clean screenshot (emojis already included for
  readability)
- Mention karein ke script **cross-platform** hai aur **error-handling**
  (try/except) built-in hai — internship reviewers is cheez ko value karte hain
- Agar time ho to ek chhota GIF bana lein (ScreenToGif / OBS) file-sorting ka
  before-after — LinkedIn post ke liye bhi use ho sakta hai