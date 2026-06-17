import { useState, useEffect, useCallback, useRef } from 'react'
import styles from './SlideDeck.module.css'

const TOTAL = 8

const slides = [
  // ── Slide 0: Splash ──
  {
    id: 'splash',
    content: (
      <>
        <div className={styles.splashBg}>
          <video
            className={styles.bgVideo}
            src="/lacity-banner.mp4"
            autoPlay
            loop
            muted
            playsInline
          />
          <div className={styles.splashOverlay} />
        </div>

        <div className={styles.splashContent}>

          <div className={styles.splashTop}>
            <div className={styles.crests}>
              <div className={styles.crestGroup}>
                <img src="/LA.png" alt="Los Angeles city seal" className={styles.laCrest} />
                <span className={styles.crestLabel}>Los Angeles</span>
              </div>

              <span className={styles.xDivider}>x</span>

              <div className={styles.crestGroup}>
                <img src="/Vaakuna_Tampere.png" alt="Tampere coat of arms" className={styles.tampereCrest} />
                <span className={styles.crestLabel}>Tampere</span>
              </div>
            </div>

            <h1 className={styles.splashTitle}>
              Tampere <span className={styles.amp}>&amp;</span> Los Angeles
            </h1>
            <p className={styles.splashSub}>Building better civic technology together</p>
          </div>

          <div className={styles.splashBottom}>
            <p className={styles.splashTagline}>
              LAPOC is an open-source AI assistant for LA's planning and permitting
              processes. This collaboration between the City of Tampere and the City of
              Los Angeles explores how conversational AI can make government services
              more accessible to everyone.
            </p>

            <button className={styles.splashArrow} aria-label="Next slide">
              &#8595;
            </button>

            <p className={styles.splashFooter}>
              City of Tampere &middot; City of Los Angeles &middot; June 2026
            </p>
          </div>
        </div>
      </>
    ),
  },

  // ── Slide 1: The Problem ──
  {
    id: 'problem',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>The Problem</p>
        <h2>LA's planning maze, in one sentence:</h2>
        <p className={styles.lead}>
          Getting a permit in Los Angeles means stitching together case numbers
          from different systems, decoding jargon from multiple departments,
          and knowing where to even start — a process that stalls homeowners,
          slows developers, and makes simple questions expensive.
        </p>

        <div className={styles.divider} />

        <div className={styles.cardGrid}>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Homeowners</h3>
            <p>
              They hear "ADU" or "permit" and have no idea where to begin.
              APNs, case IDs, LADBS versus City Planning — it is a foreign
              language. Most give up and overpay for help they should not need.
            </p>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Developers</h3>
            <p>
              Every project touches CEQA, TOC, zoning, and permit history.
              Each lives in a different database. There is no single place
              to check a parcel's status, timeline, or outstanding items.
            </p>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Contractors</h3>
            <p>
              Pulling a permit means navigating LADBS inspection codes,
              PC branch assignments, TCO versus CofO. Get it wrong and
              the job stalls. The information exists but nobody surfaces it.
            </p>
          </div>
        </div>
      </div>
    ),
  },

  // ── Slide 2: The Solution ──
  {
    id: 'solution',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>The Solution</p>
        <h2>What is LAPOC?</h2>

        <div className={styles.oneLiner}>
          LAPOC is an assistant that answers LA planning and permitting questions
          in plain language. It looks up parcels, case statuses, and process steps
          through a single chat interface that adapts to the person asking.
        </div>

        <div className={styles.chipGroup}>
          <span className={`${styles.chip} ${styles.chipFilled}`}>LLM-powered agent</span>
          <span className={styles.chip}>Parcel lookup</span>
          <span className={styles.chip}>Case tracking</span>
          <span className={styles.chip}>Workflow guidance</span>
          <span className={styles.chip}>Speech input and output</span>
          <span className={styles.chip}>Persona-adaptive responses</span>
        </div>

        <p className={styles.bodyMuted}>
          Three modes — <strong>Homeowner</strong>, <strong>Developer</strong>, <strong>Contractor</strong> —
          each gets answers pitched at the right level. A homeowner hears plain
          language with defined terms. A developer gets CEQA thresholds and
          zoning code. A contractor gets LADBS office procedures and inspection
          timelines.
        </p>
      </div>
    ),
  },

  // ── Slide 3: Why It Matters ──
  {
    id: 'why',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>Why It Matters</p>
        <h2>Why should the public care?</h2>

        <div className={styles.cardGrid2}>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Time</h3>
            <p>
              A question that used to take a phone call, a visit to a
              department, or digging through a portal now takes one
              sentence typed or spoken. Ask in your own words, get
              an answer immediately.
            </p>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>One front door</h3>
            <p>
              Parcel data from Planning. Case status from LADBS. Process
              guidance from city code. All of it lives in one chat
              interface. No more figuring out which department to call.
            </p>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Jargon translated</h3>
            <p>
              CEQA, ZIMAS, LOD, TCO, CofO, PC branches. Every acronym
              gets explained in context. You do not need to become an
              expert in city codes just to ask a question about your
              property.
            </p>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Accessible</h3>
            <p>
              Speech input and output built in. A 3D mascot provides
              visual feedback during audio responses. No login, no
              download, no training required. Open the page and start
              talking.
            </p>
          </div>
        </div>
      </div>
    ),
  },

  // ── Slide 4: System Architecture ──
  {
    id: 'architecture',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>Technical Deep-Dive</p>
        <h2>System Architecture</h2>

        <div className={styles.archFlow}>
          <span className={styles.flowNode}>React + Vite</span>
          <span className={styles.flowArrow}>&rarr;</span>
          <span className={`${styles.flowNode} ${styles.flowNodeAlt}`}>FastAPI Backend</span>
          <span className={styles.flowArrow}>&rarr;</span>
          <span className={styles.flowNode}>Azure OpenAI</span>
          <span className={styles.flowArrow}>&darr;</span>
          <span className={styles.flowNode}>SQLite</span>
        </div>

        <div className={styles.archGrid}>
          <div className={styles.archPanel}>
            <div className={styles.archPanelHeader}>Backend (Python FastAPI + SQLite)</div>
            <div className={styles.archPanelBody}>
              <ul className={styles.archList}>
                <li><span className={styles.bullet}>&#9632;</span> <code>main.py</code> — entry point: loads env vars first, creates DB tables, sets up CORS, mounts 4 routers</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>routers/chat.py</code> — POST /chat runs the agent loop, generates follow-up suggestions, produces TTS summaries</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>agent/agent.py</code> — Azure OpenAI loop (max 6 turns) with tool dispatch and persona detection</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>agent/tools.py</code> — five tools: lookup_parcel(), get_case_detail(), get_workflow(), lookup_address(), check_adu_eligibility()</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>agent/prompts/system_prompts.jinja</code> — persona-specific prompts as Jinja2 blocks</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>database.py</code> — SQLAlchemy with a CWD-relative SQLite file</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>models.py</code> — Plot, Case, WorkflowStep, WorkflowPersona ORM models</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>seed/seed_data.py</code> — destructive reseed: 10 parcels, 30 cases, 135 workflow steps</li>
              </ul>
            </div>
          </div>

          <div className={styles.archPanel}>
            <div className={styles.archPanelHeader}>Frontend (React 18 + TypeScript + Vite)</div>
            <div className={styles.archPanelBody}>
              <ul className={styles.archList}>
                <li><span className={styles.bullet}>&#9632;</span> <code>Chat.tsx</code> — main page: owns all state, speech hooks, 30-second fetch timeout</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>ChatWindow.tsx</code> — renders message bubbles with markdown + card extraction</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>MapCard.tsx</code> — Leaflet map component rendered from MAP: sentinel data</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>ParcelCard / CaseDetailCard / WorkflowTimeline</code> — card components for sentinel-prefixed agent data</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>ChatMascot.tsx</code> — 3D ram model (R3F) with jaw animation synced to speech visemes</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>useSpeechToken / useSpeechRecognizer / useSpeechSynthesizer</code> — Azure Speech SDK pipeline</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>Vite proxy</code> — routes /plots, /cases, /chat, /static to the backend in development</li>
                <li><span className={styles.bullet}>&#9632;</span> <code>CSS Modules</code> — every component has a paired .module.css, no Tailwind or inline styles</li>
              </ul>
            </div>
          </div>
        </div>

        <p className={styles.archNote}>
          <strong>Structured text protocol:</strong> Agent tools return data with sentinel prefixes
          (PARCEL:, CASE DETAIL:, WORKFLOW:, MAP:). The frontend parses these into rich card components.
        </p>
      </div>
    ),
  },

  // ── Slide 5: Agent Loop & Data Flow ──
  {
    id: 'agent',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>Technical Deep-Dive</p>
        <h2>Agent Loop and Data Flow</h2>

        <div className={styles.cardGrid2}>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Agent Loop (per chat message)</h3>
            <div className={styles.cardBodySmall}>
              <strong>1.</strong> <code>run_agent()</code> — main LLM tool-calling loop
              (max 6 iterations, tool_choice: "auto")<br/>
              <strong>2.</strong> <code>generate_suggestions()</code> — second LLM call,
              only on the first user message; produces 4 follow-up prompts<br/>
              <strong>3.</strong> <code>generate_speech_keynotes()</code> — third LLM call
              on every response; 1-2 sentence spoken summary (40 words max, no markdown)<br/><br/>
              All three calls share the same Azure OpenAI deployment. Suggestions and speech
              keynotes have fallback logic if the LLM response is malformed.
            </div>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Data Flow</h3>
            <div className={styles.cardBodySmall}>
              <strong>User query</strong> &rarr; Vite proxy &rarr; FastAPI POST /chat
              &rarr; agent loop with tool dispatch<br/><br/>
              <strong>Tools query SQLite</strong> (10 parcels, 30 cases, 20 process
              types, 99 persona guidance rows)<br/><br/>
              <strong>LLM response</strong> &rarr; sentinel-prefixed structured data
              plus conversational prose &rarr; frontend card parsers<br/><br/>
              <strong>Three LLM calls per request</strong> (main + suggestions + speech).
              A 30-second frontend timeout sets the upper bound on chain depth.
            </div>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Persona Adaptation</h3>
            <div className={styles.cardBodySmall}>
              The frontend always sends persona: "auto". The LLM detects the user's
              role from their phrasing and appends [PERSONA:resident|developer|contractor]
              on the first reply. The Python backend strips the tag before returning
              the response to the UI.<br/><br/>
              System prompts live in system_prompts.jinja as named blocks — one per
              persona plus a suggest block. Edit the templates, not the Python code.
              Workflow guidance also filters by persona.
            </div>
          </div>
          <div className={styles.card}>
            <span className={styles.cardAccent} />
            <h3>Speech Pipeline</h3>
            <div className={styles.cardBodySmall}>
              useSpeechToken() fetches a short-lived STS token from GET /speech-token,
              refreshing every 9 minutes. This drives useSpeechRecognizer()
              (continuous speech-to-text) and useSpeechSynthesizer()
              (text-to-speech, voice en-US-Aria:DragonHDLatestNeural, MP3).<br/><br/>
              Viseme events feed useVisemeScheduler(), which drives the mascot's
              jaw animation. Greeting audio is cached in IndexedDB.
            </div>
          </div>
        </div>

        <div className={styles.chipGroup} style={{ marginTop: 12 }}>
          <span className={styles.chip}>Max 6 tool iterations</span>
          <span className={styles.chip}>Tool choice: auto</span>
          <span className={styles.chip}>3 LLM calls per request</span>
          <span className={styles.chip}>30s fetch timeout</span>
          <span className={styles.chip}>Jinja2 persona prompts</span>
        </div>
      </div>
    ),
  },

  // ── Slide 6: Next Steps ──
  {
    id: 'roadmap',
    content: (
      <div className={styles.slideInner}>
        <p className={styles.sectionLabel}>What's Next</p>
        <h2>Roadmap and Next Steps</h2>

        <div className={styles.roadmap}>
          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={styles.roadmapCircle}>&#10003;</div>
              <div className={styles.roadmapConnector} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagShip}`}>Shipped</span>
              <h4>Core agent with five tools</h4>
              <p>Parcel lookup, case detail, workflow guidance, address geolocation, and ADU eligibility checks — all running on Azure OpenAI with SQLite seed data.</p>
            </div>
          </div>

          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={styles.roadmapCircle}>&#10003;</div>
              <div className={styles.roadmapConnector} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagShip}`}>Shipped</span>
              <h4>Speech I/O and 3D mascot</h4>
              <p>Azure Speech TTS and STT with viseme-driven jaw animation on a 3D ram model rendered in React Three Fiber.</p>
            </div>
          </div>

          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={styles.roadmapCircle}>&#10003;</div>
              <div className={styles.roadmapConnector} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagShip}`}>Shipped</span>
              <h4>Persona-adaptive responses</h4>
              <p>Three personas (homeowner, developer, contractor) with language and depth tailored to each role.</p>
            </div>
          </div>

          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={`${styles.roadmapCircle} ${styles.roadmapCircleNum}`}>1</div>
              <div className={styles.roadmapConnector} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagNext}`}>Next</span>
              <h4>Live data integration</h4>
              <p>Connect to the ZIMAS portal and LADBS case management APIs — replace seed data with real-time parcel and case information.</p>
            </div>
          </div>

          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={`${styles.roadmapCircle} ${styles.roadmapCircleNum}`}>2</div>
              <div className={styles.roadmapConnector} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagNext}`}>Next</span>
              <h4>Interactive data layers</h4>
              <p>Parcel map visualization, zoning overlays, and interactive timelines with filterable milestones.</p>
            </div>
          </div>

          <div className={styles.roadmapStep}>
            <div className={styles.roadmapRail}>
              <div className={`${styles.roadmapCircle} ${styles.roadmapCircleFuture}`}>3</div>
              <div className={styles.roadmapConnector} style={{ minHeight: 0, background: 'transparent' }} />
            </div>
            <div className={styles.roadmapBody}>
              <span className={`${styles.tag} ${styles.tagFuture}`}>Future</span>
              <h4>Expanded tool ecosystem and LLM flexibility</h4>
              <p>Multi-step permit application assistant, document generation, support for non-Azure LLM providers, progressive web app for offline access.</p>
            </div>
          </div>
        </div>
      </div>
    ),
  },

  // ── Slide 7: Thank You ──
  {
    id: 'thankyou',
    content: (
      <div className={`${styles.slideInner} ${styles.textCenter}`}>
        <div className={styles.crests}>
          <div className={styles.crestGroup}>
            <img src="/LA.png" alt="Los Angeles city seal" className={styles.laCrest} />
            <span className={styles.crestLabel}>Los Angeles</span>
          </div>

          <span className={styles.xDivider}>x</span>

          <div className={styles.crestGroup}>
            <img src="/Vaakuna_Tampere.png" alt="Tampere coat of arms" className={styles.tampereCrest} />
            <span className={styles.crestLabel}>Tampere</span>
          </div>
        </div>

        <h2 className={styles.thankYouTitle}>Thank You</h2>

        <div className={styles.dividerCenter} />

        <p className={styles.thankYouBody}>
          Watch the recording or try LAPOC yourself at<br/>
          <a href="https://tre-app-lapoc.azurewebsites.net" className={styles.link}>
mango-pond-098047a03.7.azurestaticapps.net
          </a>
        </p>

        <p className={styles.thankYouSub}>
          The code is open-source.<br/>
          <a href="https://github.com/anomalyco/LAPOC" className={styles.link}>
github.com/jheaminoff/LAPOC
          </a>
        </p>

        <p className={styles.thankYouMeta}>
          City of Los Angeles &middot; Department of City Planning &middot; June 2026
        </p>
      </div>
    ),
  },
]

export default function SlideDeck() {
  const [current, setCurrent] = useState(0)
  const [time, setTime] = useState(new Date())
  const [isFullscreen, setIsFullscreen] = useState(false)
  const touchStartX = useRef(0)
  const deckRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', onFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange)
  }, [])

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      deckRef.current?.requestFullscreen().catch(() => {})
    } else {
      document.exitFullscreen().catch(() => {})
    }
  }

  const goTo = useCallback((index: number) => {
    const i = Math.max(0, Math.min(index, TOTAL - 1))
    setCurrent(i)
  }, [])

  const next = useCallback(() => goTo(current + 1), [current, goTo])
  const prev = useCallback(() => goTo(current - 1), [current, goTo])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault(); next()
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault(); prev()
      } else if (e.key === 'Home') {
        e.preventDefault(); goTo(0)
      } else if (e.key === 'End') {
        e.preventDefault(); goTo(TOTAL - 1)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [next, prev, goTo])

  const onTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.changedTouches[0].screenX
  }
  const onTouchEnd = (e: React.TouchEvent) => {
    const diff = touchStartX.current - e.changedTouches[0].screenX
    if (Math.abs(diff) > 60) {
      if (diff > 0) next()
      else prev()
    }
  }

  // Splash arrow click
  const handleSplashNext = () => next()

  return (
    <div
      className={styles.deck}
      ref={deckRef}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
    >
      <div className={styles.topBar}>
        <button className={styles.fullscreenBtn} onClick={toggleFullscreen} aria-label="Toggle fullscreen">
          {isFullscreen ? '⛶' : '⛶'}
        </button>
        <span className={styles.clock}>
          {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      {slides.map((slide, i) => (
        <div
          key={slide.id}
          className={`${styles.slide} ${i === 0 ? styles.slideSplash : ''} ${slide.id === 'thankyou' ? styles.slideDark : ''} ${slide.id === 'architecture' ? styles.slideArch : ''} ${i === current ? styles.active : ''}`}
        >
          {slide.content}

          {/* Navigation (hidden on splash) */}
          {i > 0 && (
            <div className={styles.nav}>
              <button
                className={styles.navBtn}
                onClick={prev}
                disabled={current === 1}
                aria-label="Previous slide"
              >
                &#8592;
              </button>
              <div className={styles.dots}>
                {Array.from({ length: TOTAL }).map((_, di) => (
                  <button
                    key={di}
                    className={`${styles.dot} ${di === current ? styles.dotActive : ''}`}
                    onClick={() => goTo(di)}
                    aria-label={`Go to slide ${di + 1}`}
                  />
                ))}
              </div>
              <button
                className={styles.navBtn}
                onClick={next}
                disabled={current === TOTAL - 1}
                aria-label="Next slide"
              >
                &#8594;
              </button>
            </div>
          )}

          <span className={styles.slideNum}>
            {i + 1} / {TOTAL}
          </span>
        </div>
      ))}

      {/* Splash next handler — intercepts the down arrow click */}
      {current === 0 && (
        <div className={styles.nav} style={{ bottom: 80 }}>
          <button className={styles.splashBtn} onClick={handleSplashNext} aria-label="Next slide">
            &#8595; Begin
          </button>
        </div>
      )}

      {current === 0 && current < TOTAL - 1 && (
        <span className={styles.kbHint}>press space or arrow key to continue</span>
      )}
    </div>
  )
}
