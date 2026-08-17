# Operating Rules

## Lifecycle

```text
DRAFT → VALIDATED → OPEN → IN_PROGRESS → REVIEW → ACCEPTED
                                  ↘ BLOCKED / REWORK
Hotel: DRAFT → READY_TO_OPEN → OPEN → CLOSING → CLOSED
```

- `DRAFT`: ยังแก้โครงสร้างได้ ห้าม claim
- `VALIDATED`: schema, dependency และ scope ผ่าน
- `OPEN`: pin baseline แล้วและเปิด claim
- `IN_PROGRESS`: มีผู้ถือ claim ที่ยืนยันได้
- `REVIEW`: worker ส่ง output และหลักฐานแล้ว
- `ACCEPTED`: reviewer ผ่าน
- `BLOCKED`: ต้องการข้อมูล อำนาจ หรือ dependency ภายนอก
- `REWORK`: ไม่ผ่าน review และวนกลับเจ้าของห้องเดิม

## กฎเหล็ก

1. Default deny: ห้องเขียนได้เฉพาะ `write_allowlist`
2. ทุกห้องเริ่มจาก baseline เดียวที่ระบุชัด
3. หนึ่งห้องมี claim ที่ active ได้หนึ่งรายการ
4. claim ต้องสร้างและยืนยันแบบ atomic ก่อนเริ่มงาน
5. รักษา `mission_id`, `hotel_id`, `room_id` และ routing metadata ทุก handoff
6. checks ต้องตัดสินด้วย exit code; ห้ามใส่คำถามเชิงคุณภาพเป็น CI
7. reviewer ไม่ควรเป็นผู้ implement งานเดียวกันเมื่อความเสี่ยงมีนัยสำคัญ
8. งาน fidelity สูงส่ง spec แบบ verbatim หรืออ้างไฟล์ canonical ห้าม paraphrase หลายทอด
9. retry ใช้ room/mission เดิมเพื่อเก็บประวัติและจำกัด runaway loop
10. งานลบข้อมูล, push/publish, deploy, ใช้งบ, policy หรือข้ามโปรเจกต์ต้องมีอำนาจชัด

## Escalation ladder

- กลับตัวง่าย อยู่ในห้อง และมี log: worker ตัดสินได้
- กระทบ dependency หรือ contract ห้องอื่น: ส่ง orchestrator/architect
- ความถูกต้องเชิง domain: ส่ง reviewer ที่ตรงสาย
- ทำลายข้อมูล ใช้งบ publish หรือเปลี่ยนนโยบาย: ส่ง owner
- retry ซ้ำโดยไม่เกิดข้อมูลใหม่: หยุดและ escalate พร้อมหลักฐาน

## Handoff ขั้นต่ำ

ทุกการส่งมอบต้องบอก:

- ทำอะไรสำเร็จ
- เปลี่ยนอะไรบ้าง
- checks ใดผ่าน/ไม่ผ่าน
- output อยู่ที่ไหน
- ความเสี่ยงหรือสิ่งค้าง
- ผู้รับถัดไปและเหตุผล
