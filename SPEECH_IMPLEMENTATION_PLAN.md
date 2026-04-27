# Speech-to-Text (STT) and Text-to-Speech (TTS) Implementation Plan

## Project Overview
Add voice interaction capabilities to the LangChain-based Warehouse ERP AI Console, enabling users to speak prompts and receive audio responses.

---

## 🎯 Recommended Approach: **Option 2 - Manual Verification Mode**

### Why This Approach?
1. **Accuracy First**: STT can misinterpret technical terms, SQL keywords, or domain-specific vocabulary
2. **User Control**: Users can verify and edit the transcribed text before sending
3. **Better UX**: Prevents incorrect queries from being executed
4. **Debugging**: Users can see what was transcribed vs. what they said
5. **Flexibility**: Can easily add auto-send as an optional feature later

---

## 📋 Implementation Options Comparison

### Option 1: Direct Auto-Send (Not Recommended)
**Flow**: Speak → STT → Direct to LLM → Response (+ optional TTS)

**Pros**:
- Fastest interaction
- Hands-free operation
- Good for simple queries

**Cons**:
- No error correction opportunity
- Risky for SQL operations
- Technical terms may be misheard
- No visual feedback of what was understood

---

### Option 2: Manual Verification Mode (✅ Recommended)
**Flow**: Speak → STT → Display in textarea → User reviews/edits → Manual send → Response (+ optional TTS)

**Pros**:
- User can verify transcription accuracy
- Safe for database operations
- Better user trust
- Easy to correct mistakes
- Visual confirmation

**Cons**:
- Requires one extra click
- Not fully hands-free

---

### Option 3: Hybrid Mode (Future Enhancement)
**Flow**: Toggle between auto-send and manual modes

**Pros**:
- Best of both worlds
- User choice
- Can auto-send simple queries, manual for complex ones

**Implementation**: Add after Option 2 is stable

---

## 🏗️ Technical Architecture

### Backend Components

#### 1. New API Endpoints
```
POST /api/v1/speech/transcribe
- Accepts: audio file (WebM, WAV, MP3)
- Returns: { "text": "transcribed text" }
- Uses: OpenAI Whisper API or Groq Whisper

POST /api/v1/speech/synthesize
- Accepts: { "text": "response text" }
- Returns: audio file (MP3)
- Uses: OpenAI TTS API or ElevenLabs
```

#### 2. New Python Files
```
app/services/speech_service.py
- transcribe_audio(audio_file) -> str
- synthesize_speech(text) -> bytes

app/routes/speech.py
- POST /transcribe endpoint
- POST /synthesize endpoint

app/dto/speech.py
- TranscribeRequest
- TranscribeResponse
- SynthesizeRequest
```

#### 3. Configuration Updates
```python
# app/config.py additions
OPENAI_API_KEY: str = ""
SPEECH_MODEL: str = "whisper-1"
TTS_MODEL: str = "tts-1"
TTS_VOICE: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
MAX_AUDIO_SIZE_MB: int = 25
```

---

### Frontend Components

#### 1. HTML Updates (chat_ui.html)
```html
<!-- Add microphone button next to textarea -->
<div class="composer">
  <textarea id="prompt" rows="3"></textarea>
  <button id="micBtn" class="btn-mic" title="Speak">🎤</button>
  <button id="sendBtn" class="btn-primary">Send</button>
</div>

<!-- Add audio player for TTS responses (hidden by default) -->
<audio id="responseAudio" controls style="display:none"></audio>

<!-- Add recording indicator -->
<div id="recordingIndicator" class="recording-indicator" style="display:none">
  🔴 Recording...
</div>

<!-- Add TTS toggle -->
<label class="tts-toggle">
  <input type="checkbox" id="ttsEnabled" />
  Enable voice responses
</label>
```

#### 2. JavaScript Features
```javascript
// Web Audio API for recording
- MediaRecorder API for capturing audio
- AudioContext for processing
- Blob handling for audio data

// STT Flow
1. Click mic button → Start recording
2. Click again → Stop recording
3. Upload audio to /api/v1/speech/transcribe
4. Display transcribed text in textarea
5. User reviews and clicks Send

// TTS Flow (optional)
1. After receiving bot response
2. If TTS enabled, call /api/v1/speech/synthesize
3. Play audio response
4. Show audio player controls
```

---

## 🔧 Technology Stack

### STT Options

#### Option A: OpenAI Whisper (Recommended)
- **API**: `https://api.openai.com/v1/audio/transcriptions`
- **Model**: `whisper-1`
- **Pros**: Excellent accuracy, supports 50+ languages, handles technical terms well
- **Cons**: Requires OpenAI API key, costs $0.006/minute
- **Max file size**: 25 MB

#### Option B: Groq Whisper (Alternative)
- **API**: `https://api.groq.com/openai/v1/audio/transcriptions`
- **Model**: `whisper-large-v3`
- **Pros**: Faster, cheaper, you already use Groq
- **Cons**: May have slightly lower accuracy
- **Note**: Check if Groq supports Whisper API

#### Option C: Browser Web Speech API (Not Recommended)
- **Pros**: Free, no backend needed
- **Cons**: Chrome-only, less accurate, privacy concerns, no control

---

### TTS Options

#### Option A: OpenAI TTS (Recommended)
- **API**: `https://api.openai.com/v1/audio/speech`
- **Models**: `tts-1` (faster), `tts-1-hd` (higher quality)
- **Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Pros**: Natural voices, good quality
- **Cons**: $15/1M characters (~$0.015 per 1000 chars)

#### Option B: ElevenLabs (Premium Alternative)
- **Pros**: Best quality, very natural
- **Cons**: More expensive, separate API

#### Option C: Browser Web Speech API
- **Pros**: Free, no backend
- **Cons**: Robotic voices, limited control

---

## 📝 Implementation Steps

### Phase 1: Backend Setup (2-3 hours)

1. **Update Configuration**
   ```bash
   # Add to .env
   OPENAI_API_KEY=sk-...
   SPEECH_MODEL=whisper-1
   TTS_MODEL=tts-1
   TTS_VOICE=alloy
   ```

2. **Install Dependencies**
   ```bash
   uv add openai httpx
   ```

3. **Create Speech Service**
   - File: `app/services/speech_service.py`
   - Implement `transcribe_audio()` using OpenAI Whisper
   - Implement `synthesize_speech()` using OpenAI TTS
   - Add error handling and validation

4. **Create DTOs**
   - File: `app/dto/speech.py`
   - Define request/response models

5. **Create Routes**
   - File: `app/routes/speech.py`
   - POST `/transcribe` endpoint (accepts audio file)
   - POST `/synthesize` endpoint (accepts text)
   - Add authentication via `get_current_user`

6. **Register Router**
   - Update `app/api.py` to include speech router

---

### Phase 2: Frontend Implementation (3-4 hours)

1. **Add UI Elements**
   - Microphone button with icon
   - Recording indicator (pulsing red dot)
   - TTS toggle checkbox
   - Audio player for responses

2. **Implement Audio Recording**
   ```javascript
   // Use MediaRecorder API
   - Request microphone permission
   - Start/stop recording on button click
   - Convert to appropriate format (WebM/WAV)
   - Show visual feedback during recording
   ```

3. **Implement STT Integration**
   ```javascript
   - Upload recorded audio to /api/v1/speech/transcribe
   - Show loading indicator
   - Display transcribed text in textarea
   - Handle errors gracefully
   ```

4. **Implement TTS Integration**
   ```javascript
   - After bot response, check if TTS enabled
   - Call /api/v1/speech/synthesize with response text
   - Receive audio blob
   - Play audio automatically or show player
   ```

5. **Add Styling**
   - Microphone button styles (idle, recording, processing)
   - Recording indicator animation
   - Audio player styling
   - Mobile-responsive design

---

### Phase 3: Testing & Refinement (1-2 hours)

1. **Test STT Accuracy**
   - Test with technical terms (SQL, table names)
   - Test with different accents
   - Test background noise handling

2. **Test TTS Quality**
   - Test with long responses
   - Test with code snippets
   - Test different voices

3. **Error Handling**
   - Microphone permission denied
   - Network errors
   - API rate limits
   - Large file handling

4. **UX Improvements**
   - Add keyboard shortcuts (e.g., Ctrl+M for mic)
   - Add visual feedback for all states
   - Add tooltips and help text

---

## 🎨 UI/UX Design

### Microphone Button States
1. **Idle**: Gray microphone icon 🎤
2. **Recording**: Red pulsing icon 🔴
3. **Processing**: Loading spinner ⏳
4. **Success**: Green checkmark ✅
5. **Error**: Red X with error message ❌

### Recording Flow
```
[Textarea] [🎤] [Send]
           ↓ click
[Textarea] [🔴] [Send]  ← "Recording... Click to stop"
           ↓ click
[Textarea] [⏳] [Send]  ← "Transcribing..."
           ↓
[Textarea with transcribed text] [🎤] [Send]
```

### TTS Flow
```
Bot response appears
↓ (if TTS enabled)
[🔊 Playing response...] [⏸️ Pause]
```

---

## 📦 File Structure

```
app/
├── services/
│   └── speech_service.py          # NEW: STT/TTS logic
├── routes/
│   └── speech.py                  # NEW: Speech endpoints
├── dto/
│   └── speech.py                  # NEW: Speech DTOs
├── config.py                      # UPDATE: Add speech config
└── api.py                         # UPDATE: Register speech router

chat_ui.html                       # UPDATE: Add mic button, audio player
.env                               # UPDATE: Add OPENAI_API_KEY
pyproject.toml                     # UPDATE: Add openai dependency
```

---

## 💰 Cost Estimation

### OpenAI Pricing (as of 2024)
- **Whisper STT**: $0.006 per minute
  - 100 queries/day × 30 seconds avg = 50 minutes/day = $0.30/day = $9/month
  
- **TTS**: $15 per 1M characters
  - 100 responses/day × 200 chars avg = 20K chars/day = $0.30/day = $9/month

**Total**: ~$18/month for moderate usage

---

## 🔒 Security Considerations

1. **File Upload Validation**
   - Validate file type (audio only)
   - Limit file size (25 MB max)
   - Scan for malicious content

2. **Rate Limiting**
   - Limit transcription requests per user
   - Prevent abuse of TTS endpoint

3. **Authentication**
   - Require valid JWT token for all speech endpoints
   - Same auth as chat endpoints

4. **Privacy**
   - Don't log audio files
   - Don't store transcriptions permanently
   - Comply with data privacy regulations

---

## 🚀 Future Enhancements

1. **Auto-Send Mode**
   - Add toggle for auto-send vs manual verification
   - Confidence threshold for auto-send

2. **Voice Commands**
   - "Clear chat", "Logout", "Stop recording"
   - Wake word detection

3. **Multi-Language Support**
   - Detect language automatically
   - Support multiple TTS voices per language

4. **Offline Mode**
   - Use browser Web Speech API as fallback
   - Cache common responses

5. **Voice Profiles**
   - Remember user's preferred voice
   - Adjust speech rate/pitch

6. **Advanced Features**
   - Real-time streaming transcription
   - Interrupt TTS playback
   - Voice activity detection (auto-stop recording)

---

## 📊 Success Metrics

1. **Adoption Rate**: % of users who try voice features
2. **STT Accuracy**: % of transcriptions requiring no edits
3. **User Satisfaction**: Feedback on voice quality
4. **Performance**: Average transcription time < 2 seconds
5. **Error Rate**: < 5% failed transcriptions

---

## 🐛 Known Limitations

1. **Browser Compatibility**
   - MediaRecorder API not supported in older browsers
   - Requires HTTPS for microphone access

2. **Audio Quality**
   - Background noise affects accuracy
   - Poor microphone quality impacts results

3. **Language Support**
   - Whisper supports 50+ languages but accuracy varies
   - TTS voices limited to certain languages

4. **Latency**
   - Network latency for API calls
   - Audio processing time

---

## 📚 Resources & Documentation

### APIs
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)
- [MDN MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)

### Libraries
- [openai-python](https://github.com/openai/openai-python)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)

---

## ✅ Next Steps

1. **Review this plan** with your team
2. **Set up OpenAI API key** (or choose Groq alternative)
3. **Start with Phase 1** (Backend implementation)
4. **Test STT accuracy** with sample queries
5. **Implement Phase 2** (Frontend)
6. **Gather user feedback** and iterate

---

## 🎯 Recommended Starting Point

**Start with STT only (Manual Verification Mode)**:
1. Implement backend transcription endpoint
2. Add microphone button to UI
3. Display transcribed text in textarea
4. Let users test and provide feedback
5. Add TTS later based on user demand

This approach:
- Delivers value quickly
- Reduces complexity
- Allows for iteration based on real usage
- Minimizes initial costs

---

**Estimated Total Implementation Time**: 6-9 hours
**Recommended Timeline**: 2-3 days with testing
