# macOS LaunchAgent Audio Degradation: Root Cause and Solution

## Problem Statement

A ship's bell application produces clear audio when executed from the terminal but exhibits severe degradation—scratchy, distorted playback at half-speed—when run as a macOS LaunchAgent background service.

## Initial Investigation

Standard debugging approaches failed to resolve the issue:

**Hypotheses tested:**
- Process contention for audio resources
- CPU scheduling priority differences  
- Missing environment variables
- TCC permission restrictions

**Solutions attempted:**
- Threading locks to prevent audio overlap
- Process termination before audio execution
- Elevated process priorities via `nice`
- Alternative audio players (`afplay`, `say`, `osascript`)
- User-space script delegation
- Environment variable modification

All approaches involving direct audio execution from the LaunchAgent service produced identical degradation.

## Resolution

A file-based inter-process communication system resolved the issue:

1. Background timer service writes trigger files
2. Separate watcher service monitors files and executes audio
3. Complete isolation between scheduling logic and audio playback

This approach restored normal audio quality.

## Systematic Analysis

Comprehensive diagnostic tools (`audio-debug-tests/`) isolated the root cause through controlled testing:

### Results

**Normal audio quality:**
- Terminal execution
- Process priorities (`nice -10` through `nice 19`)
- Environment variable modifications
- Alternative audio players (`say`, `qlmanage`)
- Python subprocess execution
- Background processes (`nohup`)
- LaunchAgent with `ProcessType="Interactive"`

**Degraded audio quality:**
- LaunchAgent with `ProcessType="Background"` (exclusive failure case)

## Root Cause

The issue stems from `ProcessType="Background"` in LaunchAgent configuration.

Background LaunchAgents operate in a restricted audio session context with:
- Limited user audio device access
- Modified audio buffer management
- Reduced user session privileges
- Altered real-time scheduling guarantees

This behavior is intentional. Background services are not designed for direct user audio interaction.

## Solution Architecture

The file-based trigger system provides optimal separation of concerns:

```
┌─────────────────────┐    trigger files    ┌──────────────────────┐
│   Timer Service    │ ──────────────────► │   Audio Watcher     │
│ ProcessType=        │                     │ ProcessType=         │
│ "Background"        │                     │ "Interactive"        │
│                     │                     │                      │
│ • Scheduling logic  │                     │ • Audio playback     │
│ • No audio access   │                     │ • User session       │
│ • Resource efficient│                     │ • Full audio access  │
└─────────────────────┘                     └──────────────────────┘
```

**Advantages:**
- Proper context isolation
- Adherence to macOS design principles
- Elimination of subprocess inheritance issues
- Optimal resource utilization

## Implications

Background LaunchAgents cannot reliably execute audio playback. Services requiring audio output must either:

1. Use `ProcessType="Interactive"` (simple but less efficient)
2. Delegate audio to a separate Interactive service (recommended)

## Implementation

**Components:**
- Timer service: `com.ike.ships-bell.plist` (Background) - scheduling
- Watcher service: `com.ike.ships-bell-watcher.plist` (Interactive) - audio
- Communication: Trigger files in `~/.local/share/ships-bell/`
- Audio script: `~/.local/bin/ships-bell-watcher`

**Watcher logic:**
```python
while True:
    if os.path.exists("double_strike"):
        os.remove("double_strike")
        play_audio("DoubleStrike.mp3")
    if os.path.exists("noon_strike"):
        os.remove("noon_strike") 
        play_audio("sir-thats-noon.mp3")
    time.sleep(0.1)
```

## Validation

Diagnostic tools in `audio-debug-tests/` confirm ProcessType as the determining factor:
- `audio-diagnostics.sh` - System analysis
- `service-context-test.sh` - Quality testing
- Comprehensive logging and environment comparison

## Conclusion

This investigation revealed a fundamental macOS limitation affecting multimedia background services. The file-based architecture provides a robust solution that respects system design principles while delivering reliable audio playback.

**Key finding**: Background LaunchAgents cannot reliably execute audio. Proper architecture requires delegation to Interactive services.

---

*Diagnostic tools available in `audio-debug-tests/` for verification and reproduction.*