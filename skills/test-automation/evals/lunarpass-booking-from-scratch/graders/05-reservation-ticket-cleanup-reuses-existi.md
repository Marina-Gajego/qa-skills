---
type: llm
focus: trace
weight: 1
---

Reservation/ticket cleanup reuses existing db helpers (deleteReservation, deleteTicket or cleanMission) or extends support/db.ts, not ad-hoc SQL inside the spec
