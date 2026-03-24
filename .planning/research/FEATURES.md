# Feature Research: SOC / Threat Intelligence Dashboard

**Domain:** Security Operations Center (SOC) dashboard with real-time honeypot attack visualization
**Researched:** 2026-03-24
**Confidence:** MEDIUM

**Research Note:** Web search was unavailable for this session. Findings are based on training data knowledge of SOC platforms (Splunk, IBM QRadar, Microsoft Sentinel), threat intelligence platforms (MISP, OpenCTI, ThreatConnect), and honeypot systems (Cowrie, Dionaea, T-Pot). Claims should be verified via competitor product analysis if time permits.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels broken or incomplete. For a SOC/threat intelligence dashboard, these are non-negotiable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Real-time attack feed** | Core value proposition. Users need to see attacks as they happen. | MEDIUM | Socket.io/WebSocket is the standard approach. SSE is simpler but less bidirectional. |
| **Attack count statistics** | Immediate situational awareness. "How active are we?" | LOW | Simple counters that increment on each event. |
| **Geographic origin visualization** | Attackers come from somewhere. Country/IP context is fundamental. | MEDIUM | Country flags, world map heat, or origin list. |
| **Attack type / archetype classification** | Not all attacks are equal. Classification enables understanding threat landscape. | MEDIUM | Requires behavioral rules or ML. For fake data: archetype-based rules are sufficient. |
| **Connection status indicator** | Users must know if the feed is live or disconnected. | LOW | "LIVE" badge, connection state, auto-reconnect behavior. |
| **Dark mode** | SOC analysts work in low-light environments. Dark is the default expectation. | LOW | Explicit requirement per DESIGN.md. |
| **Responsive layout** | Users view dashboards on different screen sizes. | LOW | Grid-based layouts handle this naturally. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but memorable and impressive. This is where The Holding Cell's gamified pixel-art concept lives.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Gamified attack visualization (jail cell metaphor)** | Visually memorable. Transforms abstract threat data into theatrical experience. Stops recruiters from scrolling past. | MEDIUM | Core differentiator. Pixel-art prisoner animation is the "wow moment." |
| **Animated prisoner entrance (Framer Motion spring physics)** | Delight and demonstrate skill. Shows real-time data handling + animation competence. | MEDIUM | Physics-based spring animation. Bounce on landing creates organic feel. |
| **Attacker archetype fingerprinting** | Educational. Shows you understand threat categories, not just raw counts. | MEDIUM | script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist archetypes with distinct fingerprints. |
| **Hover-to-reveal arrest record** | Information on demand. Keeps UI clean while allowing deep dives. | LOW | Tooltip with IP, country, protocol, archetype, timestamp. Retro terminal aesthetic. |
| **Attack severity / color coding** | Rapid triage. Critical attacks should visually pop. | LOW | Amber for medium, red for critical per DESIGN.md. |
| **Attack feed replay / history** | Context for past events. "What happened while I was away?" | MEDIUM | Rolling buffer of recent attacks. Can be simple list, not full replay system. |
| **Attack pattern indicators** | Shows analytical thinking. E.g., "This IP ran 47 passwords in 2 minutes." | LOW | Derived data shown in arrest record. |
| **Interactive Shodan enrichment (per IP)** | External threat intelligence lookup. Demonstrates API integration skill. | MEDIUM | Removed from v1 per PLAN.md but valuable differentiator for v1.x. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for this project specifically.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Full packet capture / raw log viewer** | Sounds like "more data = more impressive." | Storage, complexity, and privacy issues. Fake data doesn't benefit from this. | Raw log string in arrest record tooltip is sufficient for MVP. |
| **Real user authentication / login system** | "Real products have auth." | Adds infrastructure complexity. This is a portfolio demo, not an enterprise product. | None needed for MVP. Consider simple password gate only if demo requires it. |
| **Multi-honeypot aggregation (Cowrie + Dionaea + T-Pot simultaneously)** | "More sources = more impressive." | Weekend 2 scope is single Cowrie integration. Premature optimization. | Single honeypot source, done well. |
| **Full SIEM integration (Splunk, QRadar connectors)** | "Real SOCs have SIEMs." | Defeats the portfolio demo purpose. Over-engineering. | Standalone demo with simulated data is the point. |
| **Machine learning / AI-based threat scoring** | "AI is the future." | Overkill for fake data. Real honeypot ML is a separate project entirely. | Rule-based archetype classification is sufficient and auditable. |
| **Real-time world map with animated attack paths** | Geo-visualization sounds impressive. | Adds significant complexity (GlobeGL, deck.gl). Could distract from jail cell metaphor. | Country flags + origin list is adequate. |

---

## Feature Dependencies

```
Real-time Attack Feed (Socket.io)
    └──requires──> Attack Archetype Classification
                        └──requires──> Attack Event Data Model

Animated Prisoner Entrance
    └──requires──> Prisoner Avatar Sprites
    └──requires──> Framer Motion Animation System
    └──enhances──> Real-time Attack Feed (provides visual payoff)

Hover Arrest Record
    └──requires──> Attack Event Data Model
    └──requires──> Tooltip Component

Stats Panel
    └──requires──> Real-time Attack Feed (increments on events)

Shodan Enrichment
    └──requires──> Real-time Attack Feed (triggers on prisoner hover/click)
    └──conflicts──> v1 scope (removed from Weekend 1)
```

### Dependency Notes

- **Real-time feed requires archetype classification:** The data model depends on having archetype labels to render. Classification logic (fake or real) must exist before the feed is useful.
- **Prisoner animation enhances feed:** The visual payoff for receiving an attack event is the prisoner flying into the cell. If animation is missing, the feed is just a list.
- **Shodan enrichment conflicts with v1:** It was explicitly removed from Weekend 1 scope to avoid complexity. Adding it would require re-introducing the `/shodan/:ip` endpoint and RadarWidget.

---

## MVP Definition

### Launch With (v1)

Minimum viable product -- what's needed to validate the concept and impress a recruiter.

- [x] **Real-time attack feed via Socket.io** -- The core pipeline. Everything else depends on this.
- [x] **Attack count statistics (StatsPanel)** -- Situational awareness. "How active are we?" Answer in 1 second.
- [x] **Gamified jail cell visualization with pixel-art prisoners** -- The core differentiator. Makes threat data theatrical.
- [x] **Animated prisoner entrance (spring physics)** -- The wow moment. Framer Motion, not CSS keyframes.
- [x] **Hover arrest record tooltip** -- Detail on demand. IP, country, protocol, archetype, timestamp.
- [x] **Attack archetype classification (5 types)** -- script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist. Educational AND visually distinct.
- [x] **Connection status indicator ("LIVE" badge)** -- Analyst knows if feed is alive.
- [x] **Dark retro-futuristic aesthetic** -- Per DESIGN.md. Bloomberg Terminal meets Hyper Light Drifter.

### Add After Validation (v1.x)

Features to add once core is working and portfolio demo is validated.

- [ ] **Shodan IP enrichment** -- On prisoner hover, query Shodan for exposure status. Demonstrates external API integration.
- [ ] **Attack pattern indicators** -- Derived insights: "47 password attempts," "reconnaissance detected," "unusual port scan."
- [ ] **Attack history log (scrollable list)** -- Complementary view to the jail cell. For when recruiters want to see raw data.
- [ ] **Demo speed mode** -- Toggle to increase attack cadence (1-2s instead of 3-8s) for live demos.
- [ ] **Sound effects** -- Subtle "clank" on prisoner landing. Enhances theater without being annoying.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Real Cowrie honeypot integration** -- Weekend 2 per PLAN.md. Real attack data changes everything.
- [ ] **Persistent attacker identity across sessions** -- Attacker returns, same prisoner sprite. Adds long-term narrative.
- [ ] **Multi-honeypot aggregation** -- T-Pot ecosystem, multiple honeypot types.
- [ ] **Geographic world map visualization** -- Animated attack paths on a globe. High complexity, could distract from jail cell.
- [ ] **Alerting / threshold notifications** -- "More than 10 APT operatives detected!" Push notification.
- [ ] **Export / reporting (PDF, CSV)** -- "Show me last week's attack data."

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Real-time attack feed (Socket.io) | HIGH | MEDIUM | P1 |
| Stats panel (attack counters) | HIGH | LOW | P1 |
| Jail cell grid + prisoner avatars | HIGH | MEDIUM | P1 |
| Framer Motion prisoner animation | HIGH | MEDIUM | P1 |
| Hover arrest record tooltip | MEDIUM | LOW | P1 |
| 5-archetype classification | MEDIUM | LOW | P1 |
| "LIVE" connection badge | MEDIUM | LOW | P1 |
| Dark retro aesthetic | MEDIUM | LOW | P1 |
| Shodan enrichment | MEDIUM | MEDIUM | P2 |
| Attack pattern indicators | MEDIUM | LOW | P2 |
| Scrollable attack history log | MEDIUM | MEDIUM | P2 |
| Demo speed mode | LOW | LOW | P2 |
| Sound effects | LOW | LOW | P3 |
| World map visualization | MEDIUM | HIGH | P3 |
| Multi-honeypot aggregation | MEDIUM | HIGH | P3 |
| Real Cowrie integration | HIGH | HIGH | P2 (Weekend 2) |

**Priority key:**
- P1: Must have for launch (Weekend 1)
- P2: Should have, add when possible (Weekend 1.x)
- P3: Nice to have, future consideration (v2+)

---

## Competitor Feature Analysis

| Feature | Splunk Enterprise Security | IBM QRadar | Microsoft Sentinel | The Holding Cell |
|---------|---------------------------|------------|--------------------|--------------------|
| Real-time feed | YES (Splunk Stream) | YES (QRadar offenses) | YES (KQL streaming) | YES (Socket.io) |
| Attack statistics | YES (KPIs, dashboards) | YES (offense counts) | YES (workbooks) | YES (StatsPanel) |
| Geographic origin | YES (IP mapping app) | YES (geo lookup) | YES (IP enrichment) | Country flags only |
| Attack classification | YES (correlation rules) | YES (reference sets) | YES (analytics rules) | 5 archetypes (v1) |
| Visual/animation | NO (enterprise static) | NO (enterprise static) | NO (enterprise static) | YES (pixel-art animation) |
| Gamification | NO | NO | NO | YES (jail cell metaphor) |
| Honeypot native | NO | NO | NO | YES (Cowrie planned) |
| Portfolio demo appeal | LOW | LOW | LOW | HIGH (unique) |

**Key insight:** Enterprise SOC tools (Splunk, QRadar, Sentinel) are powerful but visually boring. They are built for security operations, not for impressing recruiters. The Holding Cell's gamified pixel-art approach is a deliberate trade: less enterprise functionality, more memorability for a portfolio piece.

---

## Sources

- Splunk Enterprise Security product documentation (training data)
- IBM QRadar documentation (training data)
- Microsoft Sentinel / Azure Sentinel documentation (training data)
- MISP (Open Source Threat Intelligence Platform) feature set (training data)
- Cowrie honeypot documentation (training data)
- The Honeypot Project (training data)
- PLAN.md (project-specific requirements)
- DESIGN.md (design system requirements)
- PROJECT.md (project context)

---

*Feature research for: SOC / Threat Intelligence Dashboard*
*Researched: 2026-03-24*
