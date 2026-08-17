# Git Playbook — ออกแบบโรงแรมบน Repository

เอกสารนี้เป็นภาคบังคับสำหรับ Git-backed Hotel เป้าหมายไม่ใช่แค่สร้างหลาย branch แต่ทำให้แต่ละห้องมีต้นกำเนิด ขอบเขต เจ้าของ หลักฐาน และเส้นทางรวมงานที่ตรวจสอบได้

## 1. สำรวจ repository ก่อนออกแบบ

Agent ต้องตรวจข้อเท็จจริงแบบ read-only ก่อน:

```bash
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git branch --show-current
git log -1 --oneline
git worktree list
```

จากนั้นหา default branch, CI config, contribution guide, CODEOWNERS, branch naming, monorepo boundaries, generated files และคำสั่ง test/build จากไฟล์จริง ห้ามเดาจากชื่อ framework

รายงานสิ่งสกปรกใน working tree ก่อนสร้าง branch/worktree และห้ามทับการแก้ไขเดิมของผู้ใช้

## 2. แยก Work graph ออกจาก Git graph

Work graph บอกว่าอะไรต้องรออะไร ส่วน Git graph บอกว่า commit ใดแตกจากไหนและรวมกลับทางใด ทั้งสองกราฟสัมพันธ์กันแต่ไม่จำเป็นต้องเหมือนกัน

```text
Work:  R001 spec → R002 backend → R004 integration
                   R003 frontend ─┘

Git:   baseline ─┬─ room-R001
                 ├─ room-R002 (หลัง contract R001 ถูก pin)
                 └─ room-R003 (หลัง contract R001 ถูก pin)
```

ห้องที่พึ่ง output จากอีกห้องต้องเลือกอย่างใดอย่างหนึ่ง:

- รอให้ upstream merge เข้าสู่ integration baseline แล้วค่อยแตก branch
- pin upstream commit ที่อนุมัติแล้วเป็น explicit dependency
- รับ artifact/contract แบบ read-only โดยไม่คัดลอกประวัติที่กำกวม

ห้าม cherry-pick แบบไม่บันทึก dependency เพราะทำให้ provenance หาย

## 3. Baseline ต้อง immutable

ก่อนเปิด claims ให้ resolve ref เป็น full commit SHA และบันทึกใน `HOTEL_MANIFEST.json` กับ `GIT_POLICY.json`

```bash
git fetch origin
git rev-parse origin/main
```

ชื่อ branch เช่น `main` เคลื่อนที่ได้ จึงใช้เป็นคำอธิบายได้แต่ใช้แทน pinned SHA ไม่ได้ หาก baseline เปลี่ยนหลังเปิดโรงแรม ต้องปิด claims, วิเคราะห์ drift และเปิด revision ใหม่ ห้าม rebase ทุกห้องเงียบ ๆ

## 4. Branch และ worktree ต่อห้อง

รูปแบบแนะนำ:

```text
hotel/<hotel-id>/room-R001
hotel/<hotel-id>/room-R002
```

ใช้ worktree แยกเมื่อหลาย agent/process ทำพร้อมกัน:

```bash
git worktree add ../worktrees/<hotel-id>-R001 -b hotel/<hotel-id>/room-R001 <BASELINE_SHA>
```

ข้อดีคือ filesystem ของแต่ละห้องแยกจริง ลดการสลับ branch ผิดและรักษางานที่ยังไม่ commit ของห้องอื่น แต่ worktree ไม่แทน write allowlist; agent ยังแก้ได้เฉพาะ path ที่ประกาศ

## 5. Claim protocol

ระบบ claim ต้องมี atomic winner หนึ่งราย ตัวเลือกที่ใช้ได้:

- remote branch creation แบบห้าม force push
- compare-and-swap ในฐานข้อมูล/lock service
- issue assignment ที่ API รับประกัน atomicity

สำหรับ remote branch:

1. อ่าน occupancy เป็น snapshot เดียว
2. เลือกห้องว่าง
3. สร้าง branch จาก pinned SHA
4. เพิ่ม `CLAIM.md` ที่มี worker/session ID และ nonce
5. push โดยไม่ force
6. อ่าน claim ของ branch ตัวเองจาก remote และเทียบ ID/nonce
7. เริ่มงานเมื่อยืนยันตรงกันเท่านั้น

อย่าสแกนเนื้อหา claim ของห้องอื่นเพื่อหาเจ้าของ หาก branch มีอยู่ให้ถือว่าห้องไม่ว่าง และอย่าใช้ `--force` เพื่อชนะการแข่งขัน

## 6. Default-deny paths

แต่ละห้องประกาศ `write_allowlist` แบบ path ที่ตรวจได้ ก่อนส่ง PR ให้เทียบไฟล์ที่เปลี่ยนกับ allowlist:

```bash
git diff --name-only <BASELINE_SHA>...HEAD
```

ไฟล์นอก allowlist เป็น blocker แม้การแก้จะดูดี เพราะเป็น scope collision หากจำเป็นต้องขยาย scope ให้แก้ manifest ผ่าน architect/orchestrator ก่อน

สองห้องไม่ควรเป็นเจ้าของ path เดียวกัน หากหลีกเลี่ยงไม่ได้ ต้องกำหนด integration owner และลำดับ merge ชัดเจน ห้ามปล่อยให้ “แก้ conflict ตอนท้าย” เป็นแผนหลัก

## 7. Commit และหลักฐาน

หนึ่ง commit ควรมีเหตุผลเดียวและอธิบายผลลัพธ์ ไม่ใส่ไฟล์นอกห้อง ตรวจ staged allowlist ก่อน commit:

```bash
git diff --cached --name-only
git diff --cached --check
```

การอนุญาตให้แก้ไฟล์ไม่ได้แปลว่าอนุญาต commit, push หรือเปิด PR เสมอไป Agent ต้องแยก authority เหล่านี้ในแผน

Room report ต้องบันทึก baseline SHA, head SHA, changed paths, checks พร้อม exit code และ known risks เพื่อให้ reviewer ตรวจซ้ำได้

## 8. PR และ review gate

หนึ่ง room branch ควรมีหนึ่ง PR หรือหนึ่งหน่วย review ที่ trace กลับ manifest ได้ PR description อ้าง `hotel_id`, `room_id`, baseline, outputs, checks และ path allowlist

Gate ขั้นต่ำ:

- branch แตกจาก baseline/dependency ที่ถูกต้อง
- ไม่มีไฟล์นอก allowlist
- deterministic checks ผ่าน
- acceptance criteria มีหลักฐาน
- reviewer ที่ตรง domain อนุมัติ
- dependency ที่ระบุอยู่สถานะพร้อม

ผู้ implement ไม่ควร approve งานตนเองในห้องเสี่ยงสูง

## 9. Integration strategy

เลือกและประกาศก่อนเปิดโรงแรม:

- `merge commit`: เก็บ topology และ provenance ชัด เหมาะกับห้องใหญ่
- `squash merge`: ประวัติ main สะอาด แต่ต้องรักษา room report/PR เป็น audit trail
- `rebase merge`: ประวัติเส้นตรงแต่เปลี่ยน commit IDs ต้องระวัง pinned dependencies

รวมตาม dependency order ไม่ใช่ตามว่าใครเสร็จก่อน หลัง merge ทุกห้องที่ downstream ต้องตรวจ baseline drift ใหม่

Merge queue เหมาะเมื่อหลายห้องผ่านพร้อมกัน เพราะ test แต่ละ PR บน main เก่าอาจผ่าน แต่ล้มเหลวเมื่อรวมกัน

## 10. Rollback และปิดโรงแรม

ก่อน merge ระบุ rollback unit เช่น revert merge commit หรือ revert squash commit ห้ามออกแบบ rollback ที่ต้องลบประวัติหรือ force push shared branch

ปิดโรงแรมเมื่อ:

- ห้องที่จำเป็น merge/accepted ครบ
- integration checks ผ่านบน target branch ล่าสุด
- ไม่มี active claim หรือ unreviewed branch ที่ถูกลืม
- decision และข้อยกเว้นถูกบันทึก
- cleanup branch/worktree ได้รับอนุญาตแยกต่างหาก

## 11. Anti-patterns

- ทุก agent ใช้ branch เดียวกัน
- branch ต่อ agent แทน branch ต่อ outcome
- แตก branch จาก working tree ที่มีของค้าง
- ใช้ชื่อ `main` แทน full baseline SHA
- rebase หรือ force push ห้องของผู้อื่น
- ให้หลายห้องแก้ shared config เดียวกันโดยไม่มี integration room
- test เฉพาะใน room branch แต่ไม่ test หลังรวม
- ถือว่า PR ผ่านเท่ากับ deploy ได้
- ลบ branch/worktree อัตโนมัติโดยไม่มี authority
