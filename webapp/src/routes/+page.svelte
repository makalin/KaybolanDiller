<script lang="ts">
  import { onMount } from 'svelte';
  import {
    checkHealth,
    detectLanguage,
    fetchLanguages,
    translateText,
    type Language,
    type TranslationResult
  } from '$lib/api';

  let languages: Language[] = [];
  let sourceText = '';
  let translatedText = '';
  let sourceLang = 'en';
  let targetLang = 'tr';
  let loading = false;
  let detecting = false;
  let error: string | null = null;
  let lastResult: TranslationResult | null = null;
  let apiOnline = false;
  let mockMode = true;
  let history: { source: string; target: string; from: string; to: string; time: number }[] = [];

  $: groupedLanguages = languages.reduce(
    (acc, lang) => {
      const key = lang.family;
      if (!acc[key]) acc[key] = [];
      acc[key].push(lang);
      return acc;
    },
    {} as Record<string, Language[]>
  );

  $: charCount = sourceText.length;

  onMount(async () => {
    try {
      const health = await checkHealth();
      apiOnline = health.status === 'ok';
      mockMode = health.mock_mode;
    } catch {
      apiOnline = false;
    }

    try {
      languages = await fetchLanguages();
    } catch (e) {
      error = 'Could not load languages. Is the API running on port 8000?';
      console.error(e);
    }
  });

  function swapLanguages() {
    [sourceLang, targetLang] = [targetLang, sourceLang];
    if (translatedText) {
      sourceText = translatedText;
      translatedText = '';
      lastResult = null;
    }
  }

  async function handleTranslate() {
    if (!sourceText.trim()) return;
    loading = true;
    error = null;
    try {
      lastResult = await translateText(sourceText, sourceLang, targetLang);
      translatedText = lastResult.translated_text;
      history = [
        {
          source: sourceLang,
          target: targetLang,
          from: sourceText.slice(0, 80),
          to: translatedText.slice(0, 80),
          time: Date.now()
        },
        ...history.slice(0, 9)
      ];
    } catch (e) {
      error = e instanceof Error ? e.message : 'Translation failed';
    } finally {
      loading = false;
    }
  }

  async function handleDetect() {
    if (!sourceText.trim()) return;
    detecting = true;
    error = null;
    try {
      const result = await detectLanguage(sourceText);
      sourceLang = result.detected_language;
    } catch (e) {
      error = 'Language detection failed';
    } finally {
      detecting = false;
    }
  }

  function copyTranslation() {
    if (translatedText) navigator.clipboard?.writeText(translatedText);
  }

  function clearAll() {
    sourceText = '';
    translatedText = '';
    lastResult = null;
    error = null;
  }

  function langLabel(code: string): string {
    return languages.find((l) => l.code === code)?.name ?? code;
  }
</script>

<svelte:head>
  <title>KaybolanDiller — Lost Languages Translator</title>
</svelte:head>

<main class="app">
  <header class="header">
    <div class="brand">
      <span class="logo" aria-hidden="true">🌍</span>
      <div>
        <h1>KaybolanDiller</h1>
        <p class="tagline">Preserving endangered languages through AI translation</p>
      </div>
    </div>
    <div class="status-row">
      <span class="badge" class:online={apiOnline} class:offline={!apiOnline}>
        {apiOnline ? 'API online' : 'API offline'}
      </span>
      {#if mockMode && apiOnline}
        <span class="badge demo">Demo mode</span>
      {/if}
    </div>
  </header>

  <section class="translator" aria-label="Translation workspace">
    <div class="panel">
      <div class="panel-header">
        <select bind:value={sourceLang} aria-label="Source language">
          {#each Object.entries(groupedLanguages) as [family, langs]}
            <optgroup label={family}>
              {#each langs as lang}
                <option value={lang.code}>
                  {lang.name}{lang.is_endangered ? ' ⚠' : ''}
                </option>
              {/each}
            </optgroup>
          {/each}
        </select>
        <button type="button" class="ghost" on:click={handleDetect} disabled={detecting || !sourceText}>
          {detecting ? 'Detecting…' : 'Detect'}
        </button>
      </div>
      <textarea
        bind:value={sourceText}
        placeholder="Enter text to translate…"
        rows="6"
        maxlength="5000"
        aria-label="Source text"
      ></textarea>
      <span class="meta">{charCount} / 5000</span>
    </div>

    <div class="actions-col">
      <button type="button" class="swap" on:click={swapLanguages} title="Swap languages" aria-label="Swap languages">
        ⇄
      </button>
      <button
        type="button"
        class="primary"
        on:click={handleTranslate}
        disabled={loading || !sourceText.trim()}
      >
        {loading ? 'Translating…' : 'Translate'}
      </button>
    </div>

    <div class="panel">
      <div class="panel-header">
        <select bind:value={targetLang} aria-label="Target language">
          {#each Object.entries(groupedLanguages) as [family, langs]}
            <optgroup label={family}>
              {#each langs as lang}
                <option value={lang.code}>
                  {lang.name}{lang.is_endangered ? ' ⚠' : ''}
                </option>
              {/each}
            </optgroup>
          {/each}
        </select>
        <button type="button" class="ghost" on:click={copyTranslation} disabled={!translatedText}>
          Copy
        </button>
      </div>
      <div class="output" class:loading>
        {#if loading}
          <p class="placeholder pulse">Translating…</p>
        {:else if error}
          <p class="error">{error}</p>
        {:else if translatedText}
          <p class="result">{translatedText}</p>
        {:else}
          <p class="placeholder">Translation will appear here</p>
        {/if}
      </div>
      {#if lastResult}
        <div class="result-meta">
          <span>Model: {lastResult.model_used}</span>
          <span>Confidence: {Math.round(lastResult.confidence_score * 100)}%</span>
          {#if lastResult.is_demo}
            <span class="demo-tag">Beta / demo</span>
          {/if}
        </div>
      {/if}
    </div>
  </section>

  <div class="toolbar">
    <button type="button" class="ghost" on:click={clearAll}>Clear</button>
    <span class="pair-hint">{langLabel(sourceLang)} → {langLabel(targetLang)}</span>
  </div>

  {#if history.length > 0}
    <section class="history" aria-label="Recent translations">
      <h2>Recent</h2>
      <ul>
        {#each history as item}
          <li>
            <span class="hist-pair">{langLabel(item.source)} → {langLabel(item.target)}</span>
            <span class="hist-text">{item.from} → {item.to}</span>
          </li>
        {/each}
      </ul>
    </section>
  {/if}

  <footer class="footer">
    <p>
      {languages.length} languages · Turkic dialects &amp; endangered language focus ·
      <a href="https://github.com/makalin/KaybolanDiller" target="_blank" rel="noopener">GitHub</a>
    </p>
  </footer>
</main>

<style>
  .app {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 3rem;
  }

  .header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .logo {
    font-size: 2.5rem;
    line-height: 1;
  }

  h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .tagline {
    margin: 0.25rem 0 0;
    color: var(--text-muted);
    font-size: 0.95rem;
  }

  .status-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .badge {
    font-size: 0.75rem;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    color: var(--text-muted);
  }

  .badge.online {
    border-color: var(--success);
    color: var(--success);
  }

  .badge.offline {
    border-color: var(--danger);
    color: var(--danger);
  }

  .badge.demo {
    border-color: var(--warning);
    color: var(--warning);
  }

  .translator {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: stretch;
  }

  @media (max-width: 768px) {
    .translator {
      grid-template-columns: 1fr;
    }
    .actions-col {
      flex-direction: row !important;
      justify-content: center;
    }
  }

  .panel {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .panel-header {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  select {
    flex: 1;
    padding: 0.6rem 0.75rem;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 0.9rem;
  }

  textarea {
    width: 100%;
    min-height: 160px;
    padding: 1rem;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 1rem;
    line-height: 1.6;
    resize: vertical;
  }

  textarea:focus,
  select:focus {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
  }

  .meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: right;
  }

  .actions-col {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.75rem;
    padding-top: 2rem;
  }

  .swap {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 1px solid var(--border);
    background: var(--bg-elevated);
    color: var(--text);
    font-size: 1.25rem;
    transition: background 0.2s, border-color 0.2s;
  }

  .swap:hover {
    background: var(--bg-input);
    border-color: var(--accent);
  }

  .primary {
    padding: 0.75rem 1.25rem;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    white-space: nowrap;
    transition: background 0.2s;
  }

  .primary:hover:not(:disabled) {
    background: var(--accent-hover);
  }

  .primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .ghost {
    padding: 0.5rem 0.75rem;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-muted);
    font-size: 0.85rem;
  }

  .ghost:hover:not(:disabled) {
    border-color: var(--accent);
    color: var(--text);
  }

  .output {
    min-height: 160px;
    padding: 1rem;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 8px;
    line-height: 1.6;
  }

  .output.loading {
    opacity: 0.7;
  }

  .placeholder {
    color: var(--text-muted);
    margin: 0;
  }

  .result {
    margin: 0;
    font-size: 1.05rem;
  }

  .error {
    color: var(--danger);
    margin: 0;
  }

  .pulse {
    animation: pulse 1.2s ease-in-out infinite;
  }

  @keyframes pulse {
    50% {
      opacity: 0.5;
    }
  }

  .result-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.75rem;
    color: var(--text-muted);
  }

  .demo-tag {
    color: var(--warning);
  }

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 1rem;
  }

  .pair-hint {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .history {
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
  }

  .history h2 {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin: 0 0 1rem;
  }

  .history ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .history li {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .hist-pair {
    font-size: 0.75rem;
    color: var(--accent);
  }

  .hist-text {
    font-size: 0.9rem;
    color: var(--text-muted);
  }

  .footer {
    margin-top: 3rem;
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .footer a {
    color: var(--accent);
    text-decoration: none;
  }

  .footer a:hover {
    text-decoration: underline;
  }
</style>
