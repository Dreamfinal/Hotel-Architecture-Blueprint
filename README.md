# Hotel Architecture Blueprint

สถาปัตยกรรมสำหรับเปลี่ยนงานใหญ่ให้เป็น “โรงแรม” ที่ประกอบด้วยห้องงานขนาดพอดี แต่ละห้องมี objective, input, write scope, output, checks, reviewer และเส้นทางส่งต่องานของตัวเอง

เป้าหมายคือทำให้ AI หลายตัวหรือหลาย session ทำงานร่วมกันได้โดยไม่แบกบริบททั้งโปรเจกต์ ไม่แก้ไฟล์ชนกัน และไม่อ้างว่างานเสร็จโดยไม่มีหลักฐานตรวจรับ

## เริ่มใช้งาน

Clone repository:

```bash
git clone https://github.com/Dreamfinal/Hotel-Architecture-Blueprint.git
```

เปิด AI coding assistant ของคุณในโฟลเดอร์ repository นี้ แล้วส่งข้อความต่อไปนี้:

```text
ศึกษา Hotel Architecture Blueprint ใน repository นี้ให้ครบ โดยอ่าน AGENTS.md, START_HERE.md, BLUEPRINT.md, GIT_PLAYBOOK.md และ OPERATING_RULES.md ตามลำดับ

หลังอ่านแล้ว:
1. อธิบายความเข้าใจของคุณแบบสั้น ๆ
2. ตรวจโครงสร้างโปรเจกต์และสถานะ Git จริง ห้ามเดาข้อมูลที่ยังไม่ได้ตรวจ
3. ออกแบบ work graph และ Git graph สำหรับงานที่ฉันจะให้
4. สร้างร่าง HOTEL_MANIFEST, GIT_POLICY และ ROOM_MANIFEST ของแต่ละห้อง
5. ระบุ pinned baseline, branch/worktree, write allowlist, claim, checks, reviewer, merge order และ rollback
6. ยังไม่แก้ไฟล์ ไม่ commit ไม่ push ไม่เปิด PR และไม่ merge จนกว่าฉันจะอนุมัติแผน

เมื่อเข้าใจแล้วให้ตอบว่า “พร้อมรับโจทย์เพื่อออกแบบโรงแรม”
```

จากนั้นบอกงานจริง เช่น:

```text
ฉันต้องการย้ายระบบ authentication จาก session-based เป็น OAuth โดยรักษาผู้ใช้เดิมและไม่หยุด production ช่วยออกแบบโรงแรมสำหรับงานนี้
```

ถ้าต้องการให้ AI ลงมือหลังอนุมัติแผน ให้สั่งเพิ่มเติมอย่างชัดเจนว่ามันทำอะไรได้บ้าง เช่น สร้าง branch, แก้ไฟล์, commit, push หรือเปิด PR สิทธิ์เหล่านี้ไม่ควรถูกเหมารวมจากคำว่า “เริ่มทำ”

Prompt เดียวกันมีอยู่ใน [`PROMPT_TO_AGENT.txt`](PROMPT_TO_AGENT.txt) สำหรับคัดลอกได้ทันที

## Repository นี้สอนอะไร

- แตก mission ใหญ่เป็น bounded work units
- แยก work graph ออกจาก Git graph
- pin baseline ด้วย full commit SHA
- ใช้ branch/worktree แยกตามผลลัพธ์ของห้อง
- claim ห้องแบบ atomic เพื่อป้องกัน worker ชนกัน
- จำกัดการเขียนด้วย default-deny allowlist
- ใช้ deterministic checks ก่อน review เชิงคุณภาพ
- วาง PR gate, integration order และ rollback ก่อนเริ่มงาน
- เลือกโมเดลตามระดับ ambiguity และ judgment ไม่ใช่ดูแค่ว่างาน “ยาก” หรือ “ง่าย”

## ลำดับการศึกษา

1. [`START_HERE.md`](START_HERE.md) — วิธีเริ่มใช้
2. [`BLUEPRINT.md`](BLUEPRINT.md) — แนวคิดและการออกแบบห้อง
3. [`GIT_PLAYBOOK.md`](GIT_PLAYBOOK.md) — repository, branch, worktree, claim, PR และ merge
4. [`OPERATING_RULES.md`](OPERATING_RULES.md) — lifecycle, safety และ escalation
5. [`templates/`](templates/) — manifest พร้อมนำไปปรับใช้
6. [`examples/website-hotel/`](examples/website-hotel/) — ตัวอย่างโรงแรมขนาดเล็ก

## ตรวจ manifest ตัวอย่าง

ใช้ Python 3 โดยไม่ต้องติดตั้ง dependency เพิ่ม:

```bash
python tools/hotel_validate.py examples/website-hotel
```

ผลที่ถูกต้อง:

```text
PASS: .../examples/website-hotel
```

## ข้อควรเข้าใจ

Blueprint นี้ไม่ได้แทนสิทธิ์ของเจ้าของ repository และไม่อนุญาตให้ AI ทำ destructive action, commit, push, publish, merge หรือ deploy โดยอัตโนมัติ ผู้ใช้ต้องกำหนด authority ให้ชัดตามบริบทจริง

## License

Creative Commons Attribution 4.0 International — ดู [`LICENSE.txt`](LICENSE.txt)
