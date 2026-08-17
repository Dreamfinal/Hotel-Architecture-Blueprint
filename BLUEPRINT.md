# Hotel Architecture Blueprint v1.0

## 1. ปัญหาที่ระบบนี้แก้

งานใหญ่ล้มเหลวบ่อยเพราะมีบริบท การตัดสินใจ และไฟล์จำนวนมากปะปนกัน ไม่ใช่เพราะทุกชิ้นยากในตัวเอง Hotel Architecture ลดภาระนี้ด้วยการแยกงานเป็น bounded work units ที่เรียกว่า “ห้อง” และให้ส่วนกลางดูแล dependency, ownership, validation และ escalation

## 2. องค์ประกอบ

| โรงแรม | ระบบงาน |
|---|---|
| Hotel | Mission หรือ phase ใหญ่ |
| Wing | กลุ่มงานตามโดเมนหรือ dependency |
| Room | หน่วยงานที่ส่งมอบและตรวจรับได้อย่างอิสระ |
| Lobby | จุดอ่านสถานะและเลือกห้อง |
| Booking/Claim | กลไกกัน worker สองตัวเข้าห้องเดียวกัน |
| Keycard | สิทธิ์และ write allowlist |
| Pinned baseline | จุดตั้งต้นเดียวกันของทุกห้อง เช่น commit SHA |
| Room report | หลักฐานการส่งมอบ |
| Housekeeping/QA | การตรวจแบบ deterministic และ review เชิงคุณภาพ |
| Front desk | Router หรือ orchestrator |

แนวคิดทางวิศวกรรมที่ประกอบกันคือ Composite Pattern, bounded context, actor-like work units, message-driven workflow, CI gates, ownership และ supervisor/escalation pattern

## 3. หนึ่งห้องที่ดีต้องตอบได้แปดข้อ

1. เป้าหมายที่วัดได้คืออะไร
2. รับ input อะไรและ baseline ใด
3. แก้ไฟล์หรือทรัพยากรใดได้บ้าง
4. ห้ามแตะอะไร
5. ต้องส่ง output อะไร
6. ใช้คำสั่งใดตรวจแบบ deterministic
7. ใครตรวจคุณภาพหรืออนุมัติ
8. เมื่อใดต้องหยุดและ escalate

หากตอบข้อใดไม่ได้ ห้องนั้นยังไม่พร้อมเปิด

## 4. วิธีแบ่งห้อง

แบ่งตาม ownership และผลส่งมอบ ไม่แบ่งตามจำนวนขั้นตอนอย่างเดียว ห้องควรใหญ่พอให้เกิดผลลัพธ์ที่มีความหมาย และเล็กพอให้ worker เข้าใจโดยไม่ต้องแบกทั้งระบบ

สัญญาณว่าห้องใหญ่เกินไป:

- มีหลาย objective ที่จบแยกกันได้
- ต้องใช้ผู้เชี่ยวชาญต่าง lane
- write scope กว้างจนชนห้องอื่นง่าย
- acceptance criteria มากและไม่สัมพันธ์กัน
- failure ของส่วนหนึ่งทำให้ต้องทำใหม่ทั้งหมด

สัญญาณว่าห้องเล็กเกินไป:

- เวลาส่งต่อมากกว่าเวลาทำงาน
- output ใช้งานหรือตรวจไม่ได้จนกว่าจะรวมหลายห้อง
- ทุกห้องต้องอ่านบริบทก้อนเดียวกันซ้ำทั้งหมด

## 5. Work graph

ห้องสร้างเป็นกราฟ dependency ไม่จำเป็นต้องเป็นเส้นตรง ห้องที่ไม่มี dependency ร่วมกันทำขนานได้ ห้อง review ต้องรอ implementation ที่เกี่ยวข้อง และการรวมงานต้องรอทุก gate ที่ประกาศไว้

ตัวอย่าง:

```text
R001 API contract ──→ R003 frontend ──┐
                                     ├──→ R005 integration review
R002 database ──────→ R004 backend ──┘
```

ส่งงานตรงไป `next_to` ตามกราฟที่อนุมัติแล้ว เรียก manager เฉพาะเมื่อมี blocker, ambiguity, dependency เปลี่ยน หรือปิดเฟสหลัง review เพื่อลดการตีความซ้ำและ context drift

## 6. Model routing

เลือกโมเดลตามชนิดความไม่แน่นอน ไม่ใช่ตามคำว่า “งานยาก” เพียงอย่างเดียว

| งาน | โมเดลที่เหมาะ |
|---|---|
| งานยากแต่ขอบเขตและวิธีตรวจชัด | โมเดลประหยัด/ระดับ worker |
| แตกโรงแรมหรือออกแบบ dependency | โมเดล reasoning สูง |
| ตัดสินใจข้ามห้องและผลกระทบกว้าง | โมเดล reasoning สูง |
| ตรวจด้วย test/lint/hash/schema ได้ | เครื่องมือ deterministic ก่อน LLM |
| ตรวจ UX, ความหมาย, ความเหมาะสม | reviewer ที่ตรง domain |

หลักคือใช้โมเดลแพงกับ judgment ที่ leverage สูง และใช้โมเดล worker ทำงานจำนวนมากภายในสัญญาที่ชัด

## 7. Git-backed Hotel

เมื่อทำงานผ่าน Git ให้หนึ่งห้องมี branch หรือ worktree ของตนเอง ทุกห้องเริ่มจาก pinned baseline เดียวกัน ใช้ branch existence หรือระบบ lock แบบ atomic เป็น claim และตั้ง default-deny write allowlist

ขั้นตอนปลอดภัย:

1. เตรียม manifests และ source packet แบบ read-only
2. validate ความครบและการไม่ทับซ้อน
3. pin baseline commit
4. เปิด claims
5. worker claim ห้องแบบ atomic และยืนยัน claim ของตัวเอง
6. ทำงานเฉพาะ allowlist
7. รัน checks และเขียน room report
8. reviewer ตรวจ
9. merge ผ่านผู้มีอำนาจรวมงาน

ห้ามอาศัยการ “ดูว่าเหมือนไม่มีใครทำ” เป็น claim เพราะเกิด race condition ได้

## 8. Success criteria ของทั้งโรงแรม

โรงแรมปิดได้เมื่อทุกห้องที่จำเป็นอยู่สถานะ `ACCEPTED`, checks ผ่าน, review ครบ, ไม่มี scope conflict, output รวมกลับ baseline ได้ และการตัดสินใจที่มีผลระยะยาวถูกบันทึก
