# Changelog

All notable changes to DistroFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Analytics dashboard
- Additional platform integrations (ProductHunt, LinkedIn, TikTok, Facebook)
- Demo videos and GIFs

---

## [0.3.0] - 2025-11-28

### Added - Browser Extension (Week 3)
- **FastAPI Server**:
  - REST API endpoints for posting and scheduling
  - WebSocket support for real-time updates
  - Platform authentication status checking
  - Full API documentation at `/docs`
  - `distroflow serve` command to start server

- **Chrome Extension**:
  - Beautiful popup UI with gradient design
  - Multi-platform posting from browser
  - Real-time progress updates via WebSocket
  - Platform authentication status indicators
  - Desktop notifications for post completion
  - Context menu integration (right-click to post)
  - Keyboard shortcuts (Ctrl/Cmd+Enter to post)
  - Settings panel for API configuration
  - Extension icons (16px, 48px, 128px)

- **Documentation**:
  - Comprehensive extension guide (docs/EXTENSION.md)
  - Extension README with installation steps
  - API server test script (test_api_server.py)
  - Icon generator utilities

---

## [0.2.0] - 2025-11-28

### Added - Documentation & Polish (Week 2)
- Professional README with real-world examples
- QUICKSTART guide (5-minute setup)
- ARCHITECTURE deep dive for engineers
- PLATFORMS platform-specific guides
- CONTRIBUTING guidelines

### Changed
- Applied Black formatting to all code
- Fixed all Flake8 linting issues
- Updated setup.py to reference correct README
- Polished repository structure

---

## [0.1.0] - 2025-11-28

### Added
- **Core Infrastructure**
  - `BrowserManager`: Playwright-based browser automation
  - `AIHealer`: GPT-4 Vision CAPTCHA solver and auto-debugger
  - `Scheduler`: SQLite-based task scheduling system
  - `ContentTransformer`: Platform-specific content formatting

- **Platform Integrations**
  - Twitter: Post, comment, DM support
  - Reddit: Post to subreddits with title/content
  - HackerNews: Submit Show HN / Ask HN posts
  - Instagram: Post with media, send DMs

- **CLI Interface**
  - `launch`: Post to multiple platforms simultaneously
  - `schedule`: Schedule recurring posts
  - `setup`: Authentication configuration
  - `list-tasks`: View scheduled tasks
  - `cancel`: Cancel scheduled tasks
  - `daemon`: Run scheduler in background
  - `version`: Show version information

- **Documentation**
  - Professional README with examples
  - QUICKSTART guide for 5-minute setup
  - ARCHITECTURE deep dive for engineers
  - PLATFORMS platform-specific guides
  - CONTRIBUTING guidelines
  - 30-day execution plan

### Changed
- Refactored scattered scripts into unified package
- Standardized platform interface via `BasePlatform`
- Centralized authentication in `~/.distroflow/`

### Fixed
- Browser resource leaks via context managers
- Authentication persistence issues
- Platform selector reliability

---

## Release Notes

### v0.1.0 - "Foundation"

This is the initial release of DistroFlow, providing core automation infrastructure for cross-platform content distribution.

**Highlights**:
- Unified CLI for posting to 4 platforms
- AI-powered CAPTCHA solving
- Cost-optimized batch processing
- Self-hosted and open source

**What's Next**:
- Week 2: Documentation polish and demos
- Week 3: Additional platforms (ProductHunt, LinkedIn, TikTok)
- Week 4: Browser extension and official launch

**Known Limitations**:
- Manual authentication setup required
- Limited platform coverage (4/10+ planned)
- No tests yet (coming in v0.2.0)

---

[Unreleased]: https://github.com/yourusername/distroflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/distroflow/releases/tag/v0.1.0
